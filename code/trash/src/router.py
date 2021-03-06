
import simpy
import random
import functools
import graph
import routing

from configure import GlobalConfiguration

from SimComponents import PacketGenerator, PacketSink, SwitchPort, RandomBrancher


        
class Router(object):

    def __init__(self, hostname, interfaces):
        self.hostname   = hostname
        self.interfaces = interfaces
    
    def __repr__(self):
        return "(Router){}".format(self.hostname)
        

class Host(PacketGenerator):

    def __init__(self, hostname, interfaces, mean_arrv_time, mean_pkt_size):
        
        arrv_time_distribution = functools.partial(random.expovariate, 1.0/float(mean_arrv_time))
        pkt_size_distribution  = functools.partial(random.expovariate, 1.0/float(mean_pkt_size))
        
        PacketGenerator.__init__(self,GlobalConfiguration.simpyEnv, hostname, arrv_time_distribution, pkt_size_distribution)
        
        self.hostname   = hostname
        self.interfaces = interfaces
    
    def __repr__(self):
        return "(Host){}".format(self.hostname)
        
class Sink(PacketSink):

    def __init__(self, hostname, interfaces):#, rec_arrivals=False, absolute_arrivals=False, rec_waits=True, debug=False, selector=None
        
        
        PacketSink.__init__(self, GlobalConfiguration.simpyEnv, debug=True)
        
        self.hostname   = hostname
        self.interfaces = interfaces
        
    def __repr__(self):
        return "(Sink){}".format(self.hostname)
   
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
    
    
    network_components= []
    links = []
    
    network_graph = graph.Graph()
    
    
    
    def wireComponents(self):

        routing.Network_Components.initialize(self)
        
        '''Find all nodes in topology'''
        for node in self.network_components:
            self.network_graph.add_node(node)

        '''
        -Find all links in topology
        -Find the receiving and transmition(remote) end of the network components from the associated link
        -Wire the nodes together (add edges to the Graph)
        '''
        for link in self.links:
            linkRxRouters = link.findRouterForThisRx(self.network_components)
            linkTxRouters = link.findRouterForThisTx(self.network_components)
            
            '''Should check if the array returned has more than one element or not'''  
            if len(linkRxRouters)==1 and len(linkTxRouters)==1:
                #for dijkstr's calculations
                self.network_graph.add_edge(linkRxRouters[0], linkTxRouters[0], 1)
                '''self.network_graph.add_edge(linkRxRouters[0].hostname, linkTxRouters[0].hostname, 1)'''
                #To wire the components for the packet generater and switch components
                #Setting the out attr for the components    
                Rx = link.Rx if isinstance(linkRxRouters[0], Router) else linkRxRouters[0]
                Tx = link.Tx if isinstance(linkTxRouters[0], Router) else linkTxRouters[0]
                if(not isinstance(Rx, Sink)):
                    Rx.out[linkTxRouters[0]] = Tx
                if(not isinstance(Tx, Sink)):
                    Tx.out[linkRxRouters[0]] = Rx
                
        self.network_graph.savefig("path_graph1.png")
        
        
        for r in routing.Network_Components.routers:
            for i in r.interfaces:
                print r
                print i.out
        for r in routing.Network_Components.hosts:
            print r
            print r.out
   