import os
import numpy as np
import matplotlib.pyplot as plt

from math import sqrt
from random import randint

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.networkanalysis import *
from qgis.analysis import QgsGeometryAnalyzer 
import processing


''' Implementation of SBB (Streetbased Buffer) which calculates Buffer-Service-Area with Distance close to real Shortest-Path-Distance of given Network'''

def euklid(graph, v_idx, t_idx):
    return sqrt(((graph.vertex(v_idx).point()[0] - graph.vertex(t_idx).point()[0]) ** 2) + ((graph.vertex(v_idx).point()[1] - graph.vertex(t_idx).point()[1]) ** 2))

def build_shortestPath(graph,startPoint, EndPoint):
    global p, costs
        
    tStart = tiedPoint[startPoint]

    idStart = graph.findVertex(tStart)
    idStop = EndPoint
        
    (tree, costs) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)
        
    if tree[idStop] == -1:
        print("Path not found")
    else:
        p = []
        curPos = idStop
        while curPos != idStart:
            p.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
            curPos = graph.arc(tree[curPos]).outVertex();
        p.append(tStart)
        
    return p

def heuristic_buffer(graph, sourcenode, impedance, accuracy, pa_name, PointList, ratio=None):
    global area_buffer_heuristic
    
    path_root = 'C://Users//David//Desktop//BachArbeit//Praxis'
    
    euklid_dist = []
    real_dist = []
    ratio_list = []
    
    if ratio == None:
        for j in range(accuracy):
            endvertex = randint(0, graph.vertexCount())
            euklid_distance = euklid(graph, sourcenode, endvertex)
            (tree, costs) = QgsGraphAnalyzer.dijkstra(graph, sourcenode, 0)
            real_distance = costs[endvertex]
            euklid_dist.append(euklid_distance)
            real_dist.append(real_distance)
            ratio_list.append(euklid_distance/real_distance)
        ratio_list = [x for x in ratio_list if x!= 0]
        ratio_median = sum(ratio_list)/len(ratio_list)
        
        print('Euklid-Real-Distance-Ration: ' + str(ratio_median))
        
    else:
        ratio_median = ratio
        
    firestation = QgsVectorLayer('Point?crs=epsg:32633',pa_name , 'memory')
    prov = firestation.dataProvider()
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPoint(PointList[sourcenode]))
    prov.addFeatures([feat])
    
    path_Buffer_heuristic = path_root+'//Buffer_heuristic_'+str(pa_name)+'.shp'
    QgsGeometryAnalyzer().buffer(firestation, path_Buffer_heuristic, (impedance*ratio_median), False, False, -1)
    Buffer_heuristic = iface.addVectorLayer(path_Buffer_heuristic, pa_name, 'ogr')
    
    renderer = Buffer_heuristic.rendererV2()
    symbol = renderer.symbol()
    symbol.setColor(QColor(226,51,38,70))
    iface.mapCanvas().refresh()
    iface.legendInterface().refreshLayerSymbology(Buffer_heuristic)
    

    features = Buffer_heuristic.getFeatures()
    for f in features:
        geom = f.geometry()
        area_buffer_heuristic = geom.area() / 1000000
        
        
    return area_buffer_heuristic, ratio_median
