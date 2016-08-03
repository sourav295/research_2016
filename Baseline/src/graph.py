from collections import defaultdict, deque
import matplotlib.pyplot as plt
import networkx as nx
import dijkstra
import pygraphviz

class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = {}
        
        self.nxGraph = nx.Graph() #for plot

    def add_node(self, value):
        self.nodes.add(value)
        self.nxGraph.add_node(value)

    def add_edge(self, from_node, to_node, dist):
        self.join_uniDirectionally(from_node, to_node, dist)
        self.nxGraph.add_edge(from_node, to_node, distance=float(dist))
    
    def join_uniDirectionally(self, from_node, to_node, dist):
        #submap exists for every key (from_node) in the map "edges" 
        #content of submap : to_node vs distace
        sub_map = self.edges[from_node] if from_node in self.edges else {}
        sub_map[to_node] = dist
        self.edges[from_node]= sub_map
        
    def savefig(self, filePath):
        pos = nx.nx_agraph.graphviz_layout(self.nxGraph)
        nx.draw(self.nxGraph, pos, with_labels=True)
        plt.savefig(filePath)
        
    def shortestPath(self,start,end):
        return dijkstra.shortestPath(self.edges, start, end)
    
   