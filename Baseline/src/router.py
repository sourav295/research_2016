
import simpy
import random
import functools
import graph
import routing

from configure import GlobalConfiguration

from SimComponents import PacketGenerator, PacketSink, SwitchPort, RandomBrancher


        
class Router(object):

    def __init__(self, hostname, links):
        self.hostname   = hostname
        self.links      = links
        
        self.routing_processor = routing.Routing_Processor()
        
        for link in self.links:
            local_port  = link.this_port
            local_port.set_routing_processor(self.routing_processor)
                    
    def __repr__(self):
        return "(Router){}".format(self.hostname)

class Link(object):
    def __init__(self, this_port, remote_port):
        self.this_port    = this_port   #switch port at local end
        self.remote_port  = remote_port #could be switch port, sink or host

class Host(PacketGenerator):

    def __init__(self, hostname, mean_arrv_time, mean_pkt_size):
        
        arrv_time_distribution = functools.partial(random.expovariate, 1.0/float(mean_arrv_time))
        pkt_size_distribution  = functools.partial(random.expovariate, 1.0/float(mean_pkt_size))
        
        PacketGenerator.__init__(self,GlobalConfiguration.simpyEnv, hostname, arrv_time_distribution, pkt_size_distribution)
        
        self.hostname   = hostname
        
    
    def __repr__(self):
        return "(Host){}".format(self.hostname)
        
class Sink(PacketSink):

    def __init__(self, hostname):#, rec_arrivals=False, absolute_arrivals=False, rec_waits=True, debug=False, selector=None
        
        
        PacketSink.__init__(self, GlobalConfiguration.simpyEnv, debug=True)
        
        self.hostname   = hostname
       
        
    def __repr__(self):
        return "(Sink){}".format(self.hostname)
   
class Interface(SwitchPort):
    
    curr_id = 0
    
    def __init__(self, name, bandwidth, port, address, netmask):
          
          
        SwitchPort.__init__(self, GlobalConfiguration.simpyEnv, float(bandwidth), None, False)
        
        self.name       = name
        self.bandwidth  = bandwidth
        self.port       = port
        self.address    = address
        self.netmask    = netmask
        self.id         = Interface.curr_id
        
        Interface.curr_id = Interface.curr_id + 1         
        
    def find_host_router(self, routers):
        for router in routers:
            for link in router.links:
                if link.this_port == self:
                    return router
    
    def __repr__(self):
        return "(Inf){}".format(self.id)

    
        
    
class Topology(object):
    
    
    network_components= []
    network_graph = graph.Graph()
    
    def wireComponents(self):

        routing.Network_Components.initialize(self)
        
       
        all_routers = routing.Network_Components.routers        
        for router in all_routers:
            for link in router.links:
                local_port  = link.this_port #this router's switch port 
                remote_port = link.remote_port #could be the remote  switch_port, sink or host(packet generator)
                
                if isinstance(remote_port, Interface):
                    #idetify remote router
                    remote_router  = remote_port.find_host_router(all_routers)
                    local_port.out = remote_port#remote_port = switch port
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_router, local_port)
                    #for dijkstr's calculations
                    self.network_graph.add_edge(router, remote_router, 1)
                    
                
                if isinstance(remote_port, Host):
                    local_port.out  = remote_port
                    remote_port.out = local_port
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_port, local_port)
                    #for dijkstr's calculations
                    self.network_graph.add_edge(router, remote_port, 1)
                    self.network_graph.add_edge(remote_port, router, 1)
                    
                    
                if isinstance(remote_port, Sink):
                    local_port.out = remote_port
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_port, local_port)
                    #for dijkstr's calculations
                    self.network_graph.add_edge(router, remote_port, 1)
                    self.network_graph.add_edge(remote_port, router, 1)
                
        self.network_graph.savefig("path_graph1.png")
                
        #just some logging - very dirty, needed to be cleaned        
        for router in all_routers:
            print router
            
            
            for link in router.links:
                print "local port:  ",link.this_port, " remote port: ",link.remote_port
            print "======="
                
                