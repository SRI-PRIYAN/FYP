from prometheus_api_client import PrometheusConnect
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
from keras import regularizers
from keras.layers import Input, Dense, Flatten, Reshape, LSTM, RepeatVector, TimeDistributed
from keras.models import Sequential
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('fivethirtyeight')
sns.set_style('darkgrid')
sns.set_context("notebook", rc={
    "font.size": 8,
    "axes.titlesize": 16,
    "axes.labelsize": 11,
    "axes.labelspacing": 10
})

pc = PrometheusConnect(url="http://localhost:9090")

train_start_time = pd.Timestamp('2023-04-29T00:00:00IST')
train_end_time = pd.Timestamp('2023-05-02T00:00:00IST')

validate_start_time = pd.Timestamp('2023-05-03T00:01:00IST')
validate_end_time = pd.Timestamp('2023-05-03T23:59:00IST')

test_start_time = pd.Timestamp('2023-05-08T12:20:00IST')
test_end_time = pd.Timestamp('2023-05-08T13:30:00IST')


#Fetch metrics
def query_metric(query, start_time, end_time):
    return pc.custom_query_range(query, start_time, end_time, '1m')

# Returns a 2D array of size (num_values, num_nodes)
# num_values depends on the start and end time given when fetching the metric
def extract_values(raw_metric):
    metric = []

    scaler = StandardScaler()
    for data in raw_metric:
        d = np.array(data['values']).T[1]
        scaled_d = scaler.fit_transform(d.reshape((-1, 1))).flatten()
        metric.append(scaled_d)
    
    return np.array(metric, dtype=np.float64).T

def get_metric(query, start_time, end_time):
    raw_metric = query_metric(query, start_time, end_time)
    return extract_values(raw_metric)

def get_features(metrics):
    return metrics.transpose((1, 2, 0))


def get_lstm_features(features, lookback):
    rows = features.shape[0]
    features = features.reshape(rows, -1)
    res = []
    for i in range(rows - lookback + 1):
        res.append(features[i : i + lookback, :])
    
    return np.array(res)


queries = [
    'sum(rate(node_cpu_seconds_total{mode="user"}[10m])) by (node)',
    'node_memory_MemAvailable_bytes',
    'sum(rate(kubelet_http_requests_total[10m])) by (kubernetes_io_hostname)',
    '(sum(rate(node_network_transmit_bytes_total[10m])) by (node))',
    '(sum(rate(node_network_receive_bytes_total[10m])) by (node))',
    'sum(kubelet_running_containers{container_state="running"}) by (kubernetes_io_hostname)',
    'sum(container_processes) by (kubernetes_io_hostname)',
    'node_sockstat_sockets_used',
    'sum(container_sockets) by (kubernetes_io_hostname)',
    'avg(kubelet_http_requests_duration_seconds_sum) by (kubernetes_io_hostname)'
]

train_metrics = np.array(
    [get_metric(query, train_start_time, train_end_time) for query in queries]
)

x_train = get_features(train_metrics)

x_train = get_lstm_features(x_train, 3)

validate_metrics = np.array(
    [get_metric(query, validate_start_time, validate_end_time) for query in queries]
)

x_validate = get_features(validate_metrics)

x_validate = get_lstm_features(x_validate, 3)

#Autoencoder
input_shape = (4, 10)

encoder_input = Input(shape=input_shape)
x = Flatten()(encoder_input)

x = Dense(32, activation='LeakyReLU')(x)
x = Dense(28, activation='LeakyReLU')(x)
x = Dense(32, activation='LeakyReLU')(x)

x = Dense(40, activation='linear')(x)
decoder_output = Reshape(input_shape)(x)

autoencoder = keras.Model(encoder_input, decoder_output)

autoencoder.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

autoencoder.summary()

history = autoencoder.fit(x_train, x_train,
                epochs=200,
                shuffle=False,
                validation_data=(x_validate, x_validate))

#LSTM Autoencoder
timesteps = 3
num_features = 40 # 10 features for each of the 4 nodes

autoencoder = Sequential()
autoencoder.add(LSTM(32, activation='relu', input_shape=(timesteps, num_features), return_sequences=True))

autoencoder.add(LSTM(28, activation='relu', return_sequences=True))
autoencoder.add(LSTM(32, activation='relu', return_sequences=True))

autoencoder.add(TimeDistributed(Dense(num_features)))

autoencoder.compile(optimizer='adam', loss='mse', metrics='accuracy')

autoencoder.summary()

history = autoencoder.fit(x_train, x_train,
                epochs=100,
                shuffle=False,
                validation_data=(x_validate, x_validate))

#detect attack
nodeNumberToName = {
    0: 'gke-cluster-1-default-pool-31bf2469-0r0m',
    1: 'gke-cluster-1-default-pool-31bf2469-818b',
    2: 'gke-cluster-1-default-pool-31bf2469-dmtp',
    3: 'gke-cluster-1-default-pool-31bf2469-hpfb',
}

def getNodeName(nodeNumber):
    return nodeNumberToName[nodeNumber]

def get_attacked_nodes(x, threshold):
    predictions = autoencoder.predict(x)
    # For LSTM
    # intermediate = np.mean((predictions - x) ** 2, axis=(0, 1))
    # error = np.mean(intermediate.reshape((4, 10)), axis=1)
    error = np.mean((predictions - x) ** 2, axis=(2, 0))
    print(f'error => {error}')
    nodeNumbers = np.where(error > threshold)[0]
    return [getNodeName(nodeNumber) for nodeNumber in nodeNumbers]

