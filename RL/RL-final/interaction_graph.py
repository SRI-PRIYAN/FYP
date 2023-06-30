from prometheus_api_client import PrometheusConnect
from itertools import repeat
import matplotlib.pyplot as plt

prom = PrometheusConnect(url='http://localhost:9090', disable_ssl=True)

query=f'istio_requests_total'

results = prom.custom_query(query=query)

source_list=[]
dest_list=[]
value_list=[]

for elem in results:
    metric = elem.get("metric")
    source = metric.get('source_app')
    dest   = metric.get('destination_app')
    value=  int(elem.get("value")[1])


    
    if source != "auth" and source != "logger" and source!= 'istio-ingressgateway' and source!='prometheus' and source!='unknown' and dest!=None:
        print(source,value)
        #for i in range(value):
        source_list.append(source)
        value_list.append(value)
        print(len(source_list))
    if dest != "auth" and dest != "logger" and dest!= 'istio-ingressgateway' and dest!='prometheus' and dest!='unknown' and dest!=None and source!=None:
        print(dest,value)
        #for i in range(value):
        dest_list.append(dest)
        print(len(dest_list))

dest_list = dest_list[:len(source_list)]

source_list=['productpage','productpage','reviews','ratings','details']
dest_list=['details','reviews','ratings','reviews','productpage']
value_list=[10,10,20,20,10]
print(len(source_list))
print(len(dest_list))


plt.scatter(source_list,dest_list,s=value_list)
plt.show()