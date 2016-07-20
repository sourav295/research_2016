import router
import random
from configure import GlobalConfiguration
import simpy

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
    
class Routing_Processor(object):
    
    def __init__(self):
        self.out_port_vs_remote_component_map={}
        self.remote_component_vs_store_map={}
        
    def add_interface(self, network_component, local_interface):
        self.out_port_vs_remote_component_map[local_interface]  = network_component
        self.remote_component_vs_store_map[network_component]   = simpy.Store(GlobalConfiguration.simpyEnv)
        
    def put(self, pck):
        next_hop = pck.next_hop()
        store = self.remote_component_vs_store_map[next_hop]
        return store.put(pck)
        
        
    def get(self, local_interface):
        network_component = self.out_port_vs_remote_component_map[local_interface]
        store = self.remote_component_vs_store_map[network_component]
        return store
        
    