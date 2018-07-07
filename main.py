import os
import time
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

from DijkstraBuckets import dijkstraBuckets
from DijkstraNaive import dijkstraNaive
from Two_Q import Two_Q
from Two_Q_heuristic import Two_Q_heuristic, bFS
from heuristic import heuristic_buffer

from GraphAnalyzer_extended import *


path_S = 'path Streetnetwork'
path_F = 'path Firestations'
path_B = 'path boundaries'


        
def loadData(path_Streets, path_Boundaries, path_Points):
    global streetnetwork, firestations, canvas, PointList, NameList
    
    canvas = qgis.utils.iface.mapCanvas()
    
    QgsMapLayerRegistry.instance().removeAllMapLayers()
    vertex_items = [ i for i in canvas.scene().items() if issubclass(type(i), qgis.gui.QgsVertexMarker)]
    for ver in vertex_items:
        if ver in canvas.scene().items():
            canvas.scene().removeItem(ver)
    
    streetnetwork = iface.addVectorLayer(path_Streets, 'Streetnet', 'ogr')
    boundaries = iface.addVectorLayer(path_Boundaries, 'Abschnitt Neuhofen', 'ogr')
    firestations = iface.addVectorLayer(path_Points, 'Firestations', 'ogr')
    
    renderer = boundaries.rendererV2()
    symbol = renderer.symbol()
    symbol.setColor(QColor(124,10,2,20))
    iface.legendInterface().refreshLayerSymbology(boundaries)
    
    renderer = streetnetwork.rendererV2()
    symbol = renderer.symbol()
    symbol.setColor(QColor('black'))
    iface.legendInterface().refreshLayerSymbology(streetnetwork)
    
    renderer = firestations.rendererV2()
    symbol = renderer.symbol()
    symbol.setColor(QColor('red'))
    iface.legendInterface().refreshLayerSymbology(firestations)
    
    PointList = []
    NameList = []
    
    iter = firestations.getFeatures()
    for feature in iter:
            attrs = feature.attributes()
            NameList.append(attrs[0])
            PointList.append(QgsPoint(attrs[1],  attrs[2]))


def selectData(sourcenode_single, impedance):
    global streetnet_clip, firestation_point
    
    pa_name = NameList[sourcenode_single]
    firestation = QgsVectorLayer('Point?crs=epsg:32633',pa_name , 'memory')
    prov = firestation.dataProvider()
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPoint(PointList[sourcenode_single]))
    prov.addFeatures([feat])
    
    path_Buffer = path_root+'//Buffer_.shp'
    QgsGeometryAnalyzer().buffer(firestation, path_Buffer, impedance, False, False, -1)
    Buffer = iface.addVectorLayer(path_Buffer, 'Buffer', 'ogr')
    
    renderer = Buffer.rendererV2()
    symbol = renderer.symbol()
    symbol.setColor(QColor(0,0,200,20))
    iface.legendInterface().refreshLayerSymbology(Buffer)
    
    path_Streetnetclip = path_root+'//streetnet_clip.shp'
    processing.runalg("qgis:clip",streetnetwork,path_Buffer, path_Streetnetclip)
    streetnet_clip = iface.addVectorLayer(path_Streetnetclip, 'Streetnetclip', 'ogr')
    
    renderer = streetnet_clip.rendererV2()
    symbol = renderer.symbol()
    symbol.setColor(QColor(200,200,200,0))
    iface.legendInterface().refreshLayerSymbology(streetnet_clip)
    
    QgsMapLayerRegistry.instance().addMapLayers([firestation])
    
    firestation_point = [PointList[sourcenode_single]]
    
    
def createNetwork(streetnet, PointList):
        global graph, tiedPoint
        
        director = QgsLineVectorLayerDirector(streetnet, -1, '', '', '', 3)
        director = QgsLineVectorLayerDirector(streetnet, 35,  '1', '0', '2',4)
        
        distanceStrategy = QgsDistanceArcProperter()
        director.addProperter(distanceStrategy)
        crs = QgsCoordinateReferenceSystem(32633)
        builder = QgsGraphBuilder(crs)
        
        tiedPoint = director.makeGraph(builder, PointList)
        graph = builder.graph()
   

def createSPT(graph, sourcenode, algorithm):
    global tree, cost, sa_name
    
    sa_name = NameList[sourcenode]
    
    if len(tiedPoint) > 1:
        tStart = tiedPoint[sourcenode]
        idStart = graph.findVertex(tStart)
    elif len(tiedPoint) == 1:
        tStart = tiedPoint[0]
        idStart = graph.findVertex(tStart)
    
    rp = QgsVertexMarker(canvas)
    rp.setColor(QColor('green'))
    rp.setIconType(QgsVertexMarker.ICON_CIRCLE)
    rp.setIconSize(10)
    rp.setPenWidth(5)
    rp.setCenter(tStart)
    
    """--------------------------------------------------------------"""    
    """shortest Path Algorithm for Shortest-Path-Tree"""
    
    if algorithm == 'standard':
       (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, idStart, 0)
    
    elif algorithm == 'dijkstraBuckets':
        (tree, cost) = dijkstraBuckets(graph, idStart)
    
    elif algorithm == 'dijkstraNaive':
        (tree, cost) = dijkstraNaive(graph, idStart)    
    
    elif algorithm == 'Two_Q':
        (tree, cost) = Two_Q(graph, idStart)
    
    elif algorithm == 'Two_Q_heuristic':
        (tree, cost) = Two_Q_heuristic(graph, idStart, 95)
        
    elif algorithm == 'bFS':
        (tree, cost) = bFS(graph, idStart)
    
    else:
        raise ValueError('not an algorithm')
    
    """ ----------------------------------------------------------"""


def createServiceArea(graph, impedance, algorithm):
    global area
    
    upperBound = []
    r = impedance
    i = 0
    
    while i < len(cost):
        if cost[i] > r and tree[i] != -1:
            outVertexId = graph.arc(tree[i]).outVertex()
            if cost[outVertexId] < r:
                upperBound.append(graph.vertex(i).point())
        i = i + 1
        
    orig_upperBound = upperBound[:]
    CenterPoint = orig_upperBound[0]
    ServiceList = [CenterPoint]
        
    for i in range(len(orig_upperBound)-1):
        Distance_List = []
        
        for Point in upperBound:
            # calculates nearest-neighbour of CenterPoint
            point_distance = sqrt(((Point[0] - CenterPoint[0]) ** 2) + ((Point[1] - CenterPoint[1]) ** 2))
            Distance_List.append((point_distance, Point))
            # nearest Neighbor gets next CenterPoint
        CenterPoint = min(Distance_List)[1]
            # CenterPoint is added to List
        upperBound.remove(CenterPoint)
        ServiceList.append(CenterPoint)
    ServiceList.remove(ServiceList[-1])
    
    # create Polygon-Layer for Service Area
    layer = QgsVectorLayer('Polygon?crs=epsg:32633',sa_name , 'memory')
    prov = layer.dataProvider()
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPolygon([ServiceList]))
    prov.addFeatures([feat])
    
    # calculate area (km2) of Servie-Area-Polygon
    features = layer.getFeatures()
    for f in features:
        geom = f.geometry()
        area = geom.area() / 1000000
    
    renderer = layer.rendererV2()
    symbol = renderer.symbol()
    symbol.setColor(QColor(226,51,38,70))
    iface.mapCanvas().refresh()
    iface.legendInterface().refreshLayerSymbology(layer)
    ServiceAreaList.append(layer)
    
    # add  Service-Area-Layer to Map
    QgsMapLayerRegistry.instance().addMapLayers([layer])



def run_Program(sourcenode, impedance=1000, algorithm='standard', accuracy=2000, ratio=None):
    global ServiceAreaList
    ServiceAreaList = []

    print("-------------------------------------------------------") 
    begin = time.time()
    
    print('Algorithm: ' + algorithm)
    print ('-  -  -  -  -  -  -  -  -  -  -')
    
    a = time.time()
    loadData(path_S, path_B, path_F)
    print('Load Data : '+ str(time.time() - a) + ' sec')

    if type(sourcenode) != type([]):
        
        if algorithm == 'heuristic':
            
            pa_name = NameList[sourcenode]
            
            a = time.time() 
            selectData(sourcenode, impedance)
            print('Select Data : '+ str(time.time()-a) + ' sec')
            
            a = time.time() 
            area_buffer = heuristic_buffer(graph, sourcenode, impedance, accuracy, pa_name, PointList, ratio)
            print('Create Service Area for : '+ pa_name+ ' : ' +str(time.time() - a) + ' sec')
            print('Area of Service Area : ' +  str(area_buffer) + ' km^2')
            
            
        else:
            a = time.time() 
            selectData(sourcenode, impedance)
            print('Select Data : '+ str(time.time()-a) + ' sec')
        
            a = time.time() 
            createNetwork(streetnet_clip, firestation_point)
            print('Create Network : '+ str(time.time()-a) + ' sec')
        
            a = time.time()
            createSPT(graph, sourcenode, algorithm)
            print('Create SP-Tree : '+ str(time.time()-a) + ' sec')
        
            a = time.time()
            createServiceArea(graph, impedance, algorithm)
            print('Create Service Area for ' + sa_name+  ' : '+ str(time.time()-a) + ' sec')
        
            print('Area of Service Area : ' +  str(area) + ' km^2')
        
    else:
        a = time.time() 
        createNetwork(streetnetwork, PointList)
        print('Create Network : '+ str(time.time() - a) + ' sec')
        
        for i in sourcenode:
            
            if algorithm == 'heuristic':
                pa_name = NameList[i]
                print('-                    -                          -')
                a = time.time() 
                area_buffer = heuristic_buffer(graph, i, impedance, accuracy, pa_name, PointList, ratio)
                print('Create Service Area for : '+ pa_name+ ' : ' +str(time.time() - a) + ' sec')
                print('Area of Service Area : ' +  str(area_buffer) + ' km^2')
                print('-                    -                          -')
                
            else:
                print('-                    -                          -')
                a = time.time()
                createSPT(graph, i, algorithm)
                print('Create SP-Tree : '+ str(time.time() - a) + ' sec')

                a = time.time()
                createServiceArea(graph, impedance, algorithm)
                print('Create Service Area for ' + sa_name+  ' : '+ str(time.time()-a) + ' sec')
                print('Area of Service Area : ' +  str(area) + ' km^2')
                print('-                    -                          -')
    
    overall = time.time() - begin
    print ('-  -  -  -  -  -  -  -  -  -  -')
    print('Overall Time: '+str(overall))
    
    print("-------------------------------------------------------") 


'''------------------Tests------------------'''
'''------------------------------------------'''

'''Load Data'''

#run_Program([])

'''Travel Time Zones'''

'''----------QGis Dijkstra-----------'''
#run_Program([1],3000)
#run_Program(2,3000)
#run_Program([2,3,8],2000)

'''----------Naive Dijkstra----------'''
#run_Program(2,3000, 'dijkstraNaive')
#run_Program([2,3,8],3000, 'dijkstraNaive')

'''-------------Two_Q----------------'''
#run_Program(2,2000, 'Two_Q')
#run_Program([2,3,8],2000, 'Two_Q')

'''------------Dijkstra Buckets--------'''
#run_Program(2,2000, 'dijkstraBuckets')
#run_Program([2,3,8],2000, 'dijkstraBuckets') --> takes too much time

'''Buffer'''

'''---------------SBB------------------'''
#run_Program([2] ,2000, 'heuristic', accuracy=50)
#run_Program(2 ,2000, 'heuristic', ratio=0.8)
#run_Program([2,3,8,11,0] ,3000, 'heuristic', ratio=0.8)



'''--------------Ergebnisse Feuerwehr---------------'''   

#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],1000, 'dijkstraNaive')
#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],2000, 'dijkstraNaive')
#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],4000, 'dijkstraNaive')

#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],1000, 'heuristic', accuracy=50)
#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],1000, 'heuristic', accuracy=50)
#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],1000, 'heuristic', accuracy=50)

#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],1000, 'heuristic', ratio=0,8)
#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],1000, 'heuristic', accuracy=50)
#run_Program([0,1,2,3,4,5,6,7,8,9,10,11],1000, 'heuristic', accuracy=50)
