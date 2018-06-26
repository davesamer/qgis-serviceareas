import os
from qgis.networkanalysis import *

''' Implementation of Two_Q algorithm first introduced by Pallotino'''

from GraphAnalyzer_extended import *

class Two_Queue():
    
    def __init__(self):
        self.Q1 = []
        self.Q2 = []
    
    def insert_Q1(self, x):
        self.Q1.append(x)
        return self.Q1
    
    def insert_Q2(self, x):
        self.Q2.append(x)
        return self.Q2
    
    def remove_Q1(self):
        deVal = self.Q1[0]
        del(self.Q1[0])
        return deVal
    
    def remove_Q2(self):
        deVal = self.Q2[0]
        del(self.Q2[0])
        return deVal
        
    def isEmpty_Q1(self):
        if self.Q1 == []:
           return True 
    
    def isEmpty_Q2(self):
        if self.Q2 == []:
            return True
    
    def isEmpty(self):
        if self.isEmpty_Q2() and self.isEmpty_Q1():
            return True


def Two_Q(graph, s_idx):
    global l, F
    
    n = graph.vertexCount()
    
    # F: tree, l: cost
    F = []; l = []; k={}
    Temp = [s_idx]

    for i in range(0, n):
        l.append(float('inf'))
    l[s_idx] = 0
    
    for i in range(0, n):
        F.append(-1)
    
    #initialize Queue
    Q = Two_Queue()
    Q.insert_Q2(s_idx)

    while not Q.isEmpty():
        if not Q.isEmpty_Q2():
            v_idx = Q.Q2[0]
            Q.remove_Q2()
        else:
            v_idx = Q.Q1[0]
            Q.remove_Q1()
        
        if v_idx != s_idx:
            F[v_idx] = k[v_idx]
        
        for neighb in neighborhood(graph, v_idx):
            if l[neighb] == float('inf'):
                Q.insert_Q1(neighb)
                l[neighb] = l[v_idx] + weight(graph, v_idx, neighb)
                k[neighb]= findEdge(graph, v_idx, neighb)
        
            elif l[v_idx] + weight(graph, v_idx, neighb) < l[neighb]:
                Q.insert_Q2(neighb)
                l[neighb] = l[v_idx] + weight(graph, v_idx, neighb)
                k[neighb] = findEdge(graph, v_idx, neighb)
            
    return F, l
