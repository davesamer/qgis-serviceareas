from qgis.networkanalysis import *

def neighborhood(graph, v_idx):
    N = []
    OutArcs = graph.vertex(v_idx).outArc()
    for j in OutArcs:
        N.append(graph.arc(j).inVertex())
    return N
    
def weight(graph, v_idx, neighbor):
    OutArcs = graph.vertex(v_idx).outArc()
    for j in OutArcs:
        if graph.arc(j).inVertex() == neighbor:
            return graph.arc(j).property(0)
            
def findEdge(graph, v_idx, neighbor):
    OutArcs = graph.vertex(v_idx).outArc()
    for j in OutArcs:
        if graph.arc(j).inVertex() == neighbor:
            return j

def NNN(graph, v_idx):
    Neighbors = []
    NNN = []
    N = neighborhood(graph, v_idx)
    
    for neighbor_1 in N:
        for neighbor_2 in neighborhood(graph, neighbor_1):
            NNN.append(neighbor_2)
            for neighbor_3 in neighborhood(graph, neighbor_2):
                NNN.append(neighbor_3)
                for neighbor_4 in neighborhood(graph, neighbor_3):
                    NNN.append(neighbor_4)
                
    for i in NNN:
        if i != v_idx and i not in N:
            if i not in Neighbors:
                Neighbors.append(i)
                
    return Neighbors
            
            