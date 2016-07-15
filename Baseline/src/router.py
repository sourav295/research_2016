
import simpy
import random
import functools
import dijkstra

from configure import GlobalConfiguration

from SimComponents import PacketGenerator, PacketSink, SwitchPort, RandomBrancher

class Router(object):

    def __init__(self, hostname, interfaces):
        self.hostname   = hostname
        self.interfaces = interfaces

class Host(PacketGenerator):

    def __init__(self, hostname, interfaces, mean_arrv_time, mean_pkt_size):
        
        arrv_time_distribution = functools.partial(random.expovariate, 1.0/float(mean_arrv_time))
        pkt_size_distribution  = functools.partial(random.expovariate, 1.0/float(mean_pkt_size))
        
        PacketGenerator.__init__(self,GlobalConfiguration.simpyEnv, hostname, arrv_time_distribution, pkt_size_distribution)
        
        self.hostname   = hostname
        self.interfaces = interfaces
        
class Sink(PacketSink):

    def __init__(self, hostname, interfaces):#, rec_arrivals=False, absolute_arrivals=False, rec_waits=True, debug=False, selector=None
        
        
        PacketSink.__init__(self, GlobalConfiguration.simpyEnv, debug=True)
        
        self.hostname   = hostname
        self.interfaces = interfaces 
   
class Interface(SwitchPort):
    
    def __init__(self, name, bandwidth, port, address, netmask):
          
          
        SwitchPort.__init__(self, GlobalConfiguration.simpyEnv, float(bandwidth), None, False)
        
        self.name       = name
        self.bandwidth  = bandwidth
        self.port       = port
        self.address    = address
        self.netmask    = netmask
    
class Link(object):

    def __init__(self, Rx, Tx):
        self.Tx = Tx
        self.Rx = Rx
    
    def findRouterForThisRx(self, routers):
        routersWithIntfRx=[r for r in routers if self.Rx in r.interfaces]
        return routersWithIntfRx
    
    def findRouterForThisTx(self, routers):
        routersWithIntfTx=[r for r in routers if self.Tx in r.interfaces]
        return routersWithIntfTx

    
class Topology(object):
    routers= []
    links   = []
    graph = dijkstra.Graph()
    
    def drawRoughGraph(self):

        for node in self.routers:
            self.graph.add_node(node.hostname)

        for link in self.links:
            linkRxRouters = link.findRouterForThisRx(self.routers)
            linkTxRouters = link.findRouterForThisTx(self.routers)
            
            '''Should check if the array returned has more than one element or not'''  
            if len(linkRxRouters)==1 and len(linkTxRouters)==1:
                self.graph.add_edge(linkRxRouters[0].hostname, linkTxRouters[0].hostname, 1)    
            
        self.graph.savefig("path_graph1.png")
        print self.graph.nodes
        print dijkstra.shortest_path(self.graph, "PG1", "PS1")
        
    def wireComponents(self):
        for link in self.links:
            linkRxRouters = link.findRouterForThisRx(self.routers)
            linkTxRouters = link.findRouterForThisTx(self.routers)
            
            if len(linkRxRouters)==1 and len(linkTxRouters)==1:
                Rx = link.Rx if isinstance(linkRxRouters[0], Router) else linkRxRouters[0]
                Tx = link.Tx if isinstance(linkTxRouters[0], Router) else linkTxRouters[0]
                Rx.out = Tx
                