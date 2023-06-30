from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url='http://localhost:9090', disable_ssl=True)

def getCpuUsagePercentage(nodeName: str):
    query = f'avg(rate(node_cpu_seconds_total{{mode="user", node="{nodeName}"}}[2m])) by (node) * 1000'
    
    results = prom.custom_query(query=query)
    print(nodeName)
    print(results)

    return float(results[0]['value'][1])


def getMemoryUsagePercentage(nodeName: str):
    query = f'(1 - (node_memory_MemAvailable_bytes{{node="{nodeName}"}} / node_memory_MemTotal_bytes{{node="{nodeName}"}})) * 100'

    results = prom.custom_query(query=query)

    return float(results[0]['value'][1])


if __name__ == '__main__':
    import mappings
    import numpy as np 
    import matplotlib.pyplot as plt 
  
    X = ['Node 1','Node 2','Node 3','Node 4']

    YCPU=[]
    ZMem=[]

    print('\n------------Usage Statistics------------\n')
    for nodeNumber in mappings.nodeNumberToName:
        nodeName = mappings.nodeNumberToName[nodeNumber]
        print(nodeName)
        cpu = getCpuUsagePercentage(nodeName)
        YCPU.append(cpu)
        memory = getMemoryUsagePercentage(nodeName)
        ZMem.append(memory)
        print(f'{nodeNumber}. {nodeName} -> cpu={cpu:.2f}%, memory={memory:.2f}%')


    #plotting 
    X_axis = np.arange(len(X))
    plt.bar(X_axis - 0.2, YCPU, 0.4, label = 'CPU')
    plt.bar(X_axis + 0.2, ZMem, 0.4, label = 'Mem')
    
    plt.xticks(X_axis, X)
    plt.xlabel("Nodes")
    plt.ylabel("Memory and CPU usage")
    plt.legend()
    plt.show()

    #avg
    avg_mem=np.mean(YCPU)
    avg_cpu=np.mean(ZMem)
    print(avg_mem, avg_cpu)

