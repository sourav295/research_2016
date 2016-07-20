'''
import graph

graph = graph.Graph()

for node in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
    graph.add_node(node)

graph.add_edge('A', 'B', 1)
graph.add_edge('A', 'C', 1)
graph.add_edge('B', 'D', 1)
graph.add_edge('C', 'D', 1)
graph.add_edge('B', 'E', 1)
graph.add_edge('D', 'E', 1)
graph.add_edge('E', 'F', 1)
graph.add_edge('F', 'G', 1)

print graph.shortestPath('D','A')
'''

import router

GlobalConfiguration.configure(configs)

print router.Network_Components.sinks