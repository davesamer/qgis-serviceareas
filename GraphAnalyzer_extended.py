from qgis.networkanalysis import *


''' calculate neighborhood of a given vertex in a graph'''
def neighborhood(graph, v_idx):
    N = []
    OutArcs = graph.vertex(v_idx).outArc()
    for j in OutArcs:
        N.append(graph.arc(j).inVertex())
    return N

''' calculate weight of an edge - give graph and two vertexes of edge'''
def weight(graph, v_idx, neighbor):
    OutArcs = graph.vertex(v_idx).outArc()
    for j in OutArcs:
        if graph.arc(j).inVertex() == neighbor:
            return graph.arc(j).property(0)

''' find edge of a graph given two vertexes'''
def findEdge(graph, v_idx, neighbor):
    OutArcs = graph.vertex(v_idx).outArc()
    for j in OutArcs:
        if graph.arc(j).inVertex() == neighbor:
            return j


                      
