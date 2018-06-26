import os
from qgis.networkanalysis import *

os.sys.path.append(r'C:\Users\David\Desktop\BachArbeit\Programmierung\New')

from GraphAnalyzer_extended import *


class Buckets():
    
    # initializes Bucketstructure with max-needed Buckets
    def __init__(self, nodes, C):
        self.nodes = nodes
        self.B = [[] for i in range(int(self.nodes*C) + 1)]
        self.L = 0
    
    # add a Knot to the right Bucket (Bucket identifier == knot distance)
    def addKnot(self, knot, distance):
        self.B[distance].append(knot)
        return self.B
    
    # delete a Knot 
    def deleteKnot(self, knot, distance):
        self.B[distance].pop(self.B[distance].index(knot))
        return self.B
     
    # after distance-updating knot changes Bucket
    def changeBucket(self, knot, old_distance, new_distance):
        self.deleteKnot(knot, old_distance)
        self.addKnot(knot, new_distance)
    
    # choose Knot with minimum distance value for next scan
    def chooseKnot(self):
        i = self.L
        while self.B[i] == []:
            i += 1
        self.L = i
        return self.B[i][0] 


def dijkstraBuckets(graph, s_idx):
    global l, F, n
    
    n = graph.vertexCount()
    F = []; l = []; k={}
    
    for i in range(0, n):
        l.append( float('inf'))
    l[s_idx] = 0
    
    for i in range(0, n):
        F.append(-1)
    
    C = int(max([graph.arc(i).property(0) for i in range(graph.arcCount())]))
    
    Temp = [s_idx]
    
    b = Buckets(n, C)
    b.addKnot(s_idx, 0)
    
    while Temp != []:
        v_idx = b.chooseKnot()
        
        Temp.remove(v_idx)
        if v_idx != s_idx:
            F[v_idx] = k[v_idx]
            
        for neighb in neighborhood(graph, v_idx):
            if l[neighb] == float('inf'):
                Temp.append(neighb)
                l[neighb] = l[v_idx] + int(weight(graph, v_idx, neighb))
                b.addKnot(neighb, l[neighb])
                k[neighb] = findEdge(graph, v_idx, neighb)
            elif l[v_idx] + weight(graph, v_idx, neighb) < l[neighb]:
                b.changeBucket(neighb, l[neighb], (l[v_idx] + int(weight(graph, v_idx, neighb))))
                l[neighb] = l[v_idx] + int(weight(graph, v_idx, neighb))
                k[neighb] = findEdge(graph, v_idx, neighb)
                
        
        b.deleteKnot(v_idx, l[v_idx])
    return F, l
    
    
    