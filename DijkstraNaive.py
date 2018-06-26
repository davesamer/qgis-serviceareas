import os
from qgis.networkanalysis import *

''' Implementation of Dijkstra-Algorithm first introduced by E. Dijkstra --> Naive Implementation'''
''' Temporaray nodes are organised in an unordered list'''

from GraphAnalyzer_extended import *

def dijkstraNaive(graph, s_idx):
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

    while Temp != []:
        lv, v_idx = min([(l[node], node) for node in Temp])
        Temp.remove(v_idx)
        if v_idx != s_idx:
            F[v_idx] = k[v_idx]
        
        for neighb in neighborhood(graph, v_idx):
            if l[neighb] == float('inf') :
                Temp.append(neighb)
                l[neighb] = l[v_idx] + weight(graph, v_idx, neighb)
                k[neighb]= findEdge(graph, v_idx, neighb)
            elif l[v_idx] + weight(graph, v_idx, neighb) < l[neighb]:
                l[neighb] = l[v_idx] + weight(graph, v_idx, neighb)
                k[neighb] = findEdge(graph, v_idx, neighb)
                
    return F, l
    
