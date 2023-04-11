containerNumberToDetails = {
    0: {'app': 'productpage', 'version': 'v1'},
    1: {'app': 'details', 'version': 'v1'},
    2: {'app': 'reviews', 'version': 'v1'},
    3: {'app': 'reviews', 'version': 'v2'},
    4: {'app': 'reviews', 'version': 'v3'},
    5: {'app': 'ratings', 'version': 'v1'}
}

nodeNumberToName = {
    0: 'gke-cluster-1-default-pool-a33b274c-9t2g',
    1: 'gke-cluster-1-default-pool-a33b274c-g246',
    2: 'gke-cluster-1-default-pool-a33b274c-hsm7',
    3: 'gke-cluster-1-default-pool-a33b274c-z3f4',
}

def getNodeName(nodeNumber: int):
    return nodeNumberToName[nodeNumber]

def getContainerDetails(containerNumber: int):
    d = containerNumberToDetails[containerNumber]
    return d['app'], d['version']