from prometheus_api_client import PrometheusConnect
from itertools import repeat
import matplotlib.pyplot as plt

prom = PrometheusConnect(url='http://localhost:9090', disable_ssl=True)

query=f'istio_requests_total'

results = prom.custom_query(query=query)

source_list=[]
dest_list=[]
value_list=[]
num_failed_requests=0

for elem in results:
    metric = elem.get("metric")
    source = metric.get('source_app')
    dest   = metric.get('destination_app')
    resp_code = metric.get('response_code')
    value  = int(elem.get("value")[1])


    if dest == "productpage" and resp_code != 200 :
        num_failed_requests+=1
    

print(num_failed_requests)