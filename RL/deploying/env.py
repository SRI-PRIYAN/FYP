ContainerNumber = 6
NodeNumber = 4
ServiceNumber = 4
ResourceType = 2
service_containernum = [1,1,3,1]
service_container = [[0],[1],[2,3,4],[5]] 
service_container_relationship = [0,1,2,2,2,3]
alpha = 0.5 # reward weighting factor
beta =[0.5,0.5]
count = 0
CPUnum = 4
Mem = 4*1024

import numpy as np
from mappings import getContainerDetails, getNodeName
from metrics import getCpuUsagePercentage, getMemoryUsagePercentage
from deploy import deploy
#import agent

class Env():
    def __init__(self):
        self.State = []
        self.node_state_queue = []
        self.container_state_queue = []
        self.action_queue = []
        self.prepare()

    def prepare(self):
        self.container_state_queue = [-1,0.5/CPUnum,128/Mem , -1,0.5/CPUnum,256/Mem , -1,0.5/CPUnum,256/Mem, -1,0.5/CPUnum,256/Mem, -1,0.5/CPUnum,256/Mem, -1,0.5/CPUnum,128/Mem]

        for i in range(NodeNumber):
            self.node_state_queue.extend( [ 0,0,0,0,0,0, 0 , 0 ] )
        self.State = self.container_state_queue + self.node_state_queue
        self.action = [-1,-1]
        self.action_queue = [-1,-1]
   
        # Communication weight between microservices
        self.service_weight = [[0,1,0,0],[1,0,1,0],[0,1,0,2],[0,0,2,0]]
        # Communication distance between nodes
        self.Dist = [[0,1,1,1],[1,0,1,1],[1,1,0,1],[1,1,1,0]]

    # To calculate the distance between container i and j
    def getContainerDistance(self, i, j):
        m = self.container_state_queue[i*3]
        n = self.container_state_queue[j*3]

        p = service_container_relationship[i]
        q = service_container_relationship[j]

        if self.Dist[m][n] != 0 and (p != q):
            return self.Dist[m][n]
        
        return 0


    # To calculate the communication cost between container i and j
    def getContainerCommunicationCost(self, i, j):
        cost = 0
        interaction = self.service_weight[i][j] / (service_containernum[i] * service_containernum[j])
        for k in range (len(service_container[i])):
            for l in range (len(service_container[j]) ):
                cost += self.getContainerDistance(service_container[i][k],service_container[j][l]) * interaction 
        return cost


    def getTotalCommunicationCost(self):
        cost = 0
        for i in range (ServiceNumber):
            for j in range (ServiceNumber):
                cost += self.getContainerCommunicationCost(i,j)   
        return 0.5 * cost


    def getVarianceOfResourceUsage(self):
        NodeCPU = []
        NodeMemory = []

        for i in range(NodeNumber):
            cpu =  self.node_state_queue[i*(ContainerNumber+2)+ContainerNumber] 
            memory = self.node_state_queue[i*(ContainerNumber+2)+ (ContainerNumber+1)]
            NodeCPU.append(cpu)
            NodeMemory.append(memory)

        variance = beta[0] * np.var(NodeCPU) + beta[1] * np.var(NodeMemory)
        return variance

    def getJointCost(self):
        g1 = self.getTotalCommunicationCost()
        g2 = self.getVarianceOfResourceUsage()
        result = (alpha * g1)  + ((1 - alpha) * g2)
        return result, g1, g2

    def state_update(self,container_state_queue,node_state_queue):
        
        print(self.State)

    # update state
    def update(self):
        if self.action[0] >= 0 and self.action[1] >= 0:
            app, version = getContainerDetails(self.action[1])
            nodeName = getNodeName(self.action[0])

            # Update Container State
            self.container_state_queue[ self.action[1] * 3 ] = self.action[0] 
            # Update Node State
            self.node_state_queue[self.action[0] * (ContainerNumber+2) + self.action[1] ] = 1
            # Update CPU Usage
            self.node_state_queue[self.action[0] * (ContainerNumber+2) + ContainerNumber] = getCpuUsagePercentage(nodeName) / 100
            # Update Memory Usage
            self.node_state_queue[self.action[0] * (ContainerNumber+2) + (ContainerNumber + 1) ] = getMemoryUsagePercentage(nodeName) / 100

            self.action_queue.append(self.action)

            deploy(app, version, nodeName)
        else:
            print("invalid action")  
            self.node_state_queue = []
            self.container_state_queue = []
            self.action_queue = []
            self.prepare()

        self.State = self.container_state_queue + self.node_state_queue
        return self.State


    # input: action(Targetnode，ContainerIndex)
    # output: next state, cost, done
    def step(self, action):
        global count
        self.action = self.index_to_act(action)
        self.update()
        cost, comm, var = self.getJointCost()   
        done = False 
        count = 0
        
        for i in range(ContainerNumber):
            if self.container_state_queue[3*i] != -1:
                count += 1
        if count == ContainerNumber:
            done = True
        
        return self.State, cost, done, comm, var

    def reset(self):
        self.node_state_queue = []
        self.container_state_queue = []
        self.prepare() 
        return self.State,self.action
    
    def index_to_act(self, index):
        act = [-1,-1]
        act[0] = int(index / ContainerNumber)
        act[1] = index % ContainerNumber
        return act