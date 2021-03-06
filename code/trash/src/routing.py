import router
import random

class Network_Components(object):
    
    routers = []
    hosts = []
    sinks = []
    network_graph = None
    
    @staticmethod
    def initialize(topology):
        Network_Components.routers = [ nc for nc in topology.network_components if isinstance(nc, router.Router) ]
        Network_Components.hosts = [ nc for nc in topology.network_components if isinstance(nc, router.Host) ]
        Network_Components.sinks = [ nc for nc in topology.network_components if isinstance(nc, router.Sink) ]
        
        Network_Components.network_graph = topology.network_graph

    @staticmethod
    def selectRandomSink():
        all_topology_sinks = Network_Components.sinks
        return (random.choice(all_topology_sinks))

    @staticmethod
    def findExplicitPath(src, dest):
        #src = Network_Components.hosts[0]
        return  Network_Components.network_graph.shortestPath(src, dest)
    
    
    
    