import os
import numpy as np
import matplotlib.pyplot as plt


from qgis.networkanalysis import *
from math import sqrt



os.sys.path.append(r'C:\Users\David\Desktop\BachArbeit\Programmierung\New')

from GraphAnalyzer_extended import *
from Two_Q import Two_Queue

def euklid(graph, v_idx, t_idx):
    return sqrt(((graph.vertex(v_idx).point()[0] - graph.vertex(t_idx).point()[0]) ** 2) + ((graph.vertex(v_idx).point()[1] - graph.vertex(t_idx).point()[1]) ** 2))

def medianArclength(graph, percent=99):
    global values
    
    values = [graph.arc(i).property(0) for i in range(graph.arcCount())]
    values.sort()
    part = percent*len(values)/100
    count = [i for i in range(len(values[:part]))]
    values = values[:part]
    
    median = (sum(values)) / (len(values[:part]))

    return median
 


def bFS(graph, s_idx, arcLength=None):
    global l, F
    
    if arcLength == None:
        arcLength=medianArclength(graph)
    
    n = graph.vertexCount()
    # F: tree, l: cost
    F = []; l = []; k={}
    Temp = [s_idx]

    for i in range(0, n):
        l.append(float('inf'))
    l[s_idx] = 0
    
    for i in range(0, n):
        F.append(-1)

    while Temp != []:
        v_idx = Temp[0]
        Temp.remove(v_idx)
        if v_idx != s_idx:
            F[v_idx] = k[v_idx]
        
        for neighb in neighborhood(graph, v_idx):
            if l[neighb] == float('inf') :
                Temp.append(neighb)
                l[neighb] = l[v_idx] + 1
                k[neighb]= findEdge(graph, v_idx, neighb)
    
    n = arcLength
    l = [i*n for i in l]
                
    return F, l    



def Two_Q_heuristic(graph, s_idx, percent):
    global F, l
    
    median = medianArclength(graph, percent)
    
    sum = 0
    for j in range(graph.arcCount()):
        sum += graph.arc(j).property(0)
    Mittelwert = sum/(graph.arcCount())
    
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
                l[neighb] = l[v_idx] + median
                k[neighb]= findEdge(graph, v_idx, neighb)
        
            elif l[v_idx] + median < l[neighb]:
                Q.insert_Q2(neighb)
                l[neighb] = l[v_idx] + median
                k[neighb] = findEdge(graph, v_idx, neighb)
            
    return F, l
    































                
            
        
        
        
    
    
    
        
    
    
        
    