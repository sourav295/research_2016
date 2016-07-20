from collections import defaultdict, deque
import matplotlib.pyplot as plt
import networkx as nx

class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}
        self.G = {}
        
        self.nxGraph = nx.Graph() #for plot

    def add_node(self, value):
        self.nodes.add(value)
        
        self.nxGraph.add_node(value)

    def add_edge(self, from_node, to_node, dist):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = dist
        
        temp={}
        if from_node in self.G:
            temp = self.G[from_node]
        
        
        temp[to_node] = dist
        self.G[from_node]=temp
        
        self.nxGraph.add_edge(from_node, to_node, distance=float(dist))
        
    def savefig(self, filePath):
        nx.draw(self.nxGraph, with_labels=True)
        plt.savefig(filePath)


def dijkstra(graph, initial):
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node
        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            try:
                weight = current_weight + graph.distances[(min_node, edge)]
            except:
                continue
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path


def shortest_path(graph, origin, destination):
    visited, paths = dijkstra(graph, origin)
    '''
    #changed by me to make it undirectional
    if destination not in paths:
        cost, explicitPath = shortest_path(graph, destination, origin)#switch destination and origin
        return cost, explicitPath[::-1]#reverse explicit path
    '''    
    full_path = deque()
    _destination = paths[destination]

    while _destination != origin:
        full_path.appendleft(_destination)
        _destination = paths[_destination]

    full_path.appendleft(origin)
    full_path.append(destination)

    return visited[destination], list(full_path)

def verify_path(explicit_path, origin, destination):
    return explicit_path[0] == origin and explicit_path[-1] == destination

if __name__ == '__main__':
    graph = Graph()

    for node in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        graph.add_node(node)

    graph.add_edge('A', 'B', 10)
    graph.add_edge('A', 'C', 20)
    
    print graph.G
'''    
    graph.add_edge('B', 'D', 15)
    graph.add_edge('C', 'D', 30)
    graph.add_edge('B', 'E', 50)
    graph.add_edge('D', 'E', 30)
    graph.add_edge('E', 'F', 5)
    graph.add_edge('F', 'G', 2)
'''
        
    #print(shortest_path(graph, 'A', 'D')) # output: (25, ['A', 'B', 'D'])
