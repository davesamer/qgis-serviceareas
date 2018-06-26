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


                      
