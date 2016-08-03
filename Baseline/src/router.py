
import simpy
import random
import functools
import graph
import routing
import logging
from roadm import Roadm


from configure import GlobalConfiguration

from SimComponents import PacketGenerator, PacketSink, SwitchPort, Cable

        

        
class Router(object):

    def __init__(self, hostname, links):
        self.hostname   = hostname
        self.links      = links

        local_ports = [l.this_port for l in self.links]
        self.routing_processor = routing.Routing_Processor(local_ports)
        
        for link in self.links:
            local_port  = link.this_port
            local_port.set_routing_processor(self.routing_processor)
                    
    def __repr__(self):
        return "{}".format(self.hostname)

class Link(object):
    def __init__(self, this_port, remote_port):
        self.this_port    = this_port   #switch port at local end
        self.remote_port  = remote_port #could be switch port, sink or host
        
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.this_port == other.this_port and self.remote_port == other.remote_port)

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
    
    #def __init__(self, name, bandwidth, port, address, netmask):
    def __init__(self, bandwidth):
           
          
        SwitchPort.__init__(self, GlobalConfiguration.simpyEnv, float(bandwidth), None, False)
        
        self.bandwidth  = bandwidth
        self.id         = Interface.curr_id
        
        Interface.curr_id = Interface.curr_id + 1         
        
    def find_host_router(self, routers):
        for router in routers:
            for link in router.links:
                if link.this_port == self:
                    return router
        return None
    
    def is_adjacent_router(self, next_hop_router):
        for router in next_hop_router:
            for link in router.links:
                if link.remote_port == self:
                    return True
        return False
                

    def __repr__(self):
        return "(Inf){}".format(self.id)

class Copy(object):
    
    @staticmethod
    def copyObj(comp):
        if isinstance(comp, Interface):
            return Interface(comp.bandwidth)
        
        if isinstance(comp, Link):
            return Link(   Copy.copyObj(comp.this_port), Copy.copyObj(comp.remote_port)   )
        
        if isinstance(comp, Router):
            return Router(comp.hostname, [ Copy.copyObj(l) for l in comp.links ])
        
        if isinstance(comp, Sink):
            return Router(comp.hostname)
        
        if isinstance(comp, Host):
            return Router(comp.hostname, comp.mean_arrv_time, comp.mean_pkt_size)
        
        return comp#other roadm etc
        
    @staticmethod
    def exc(network_components):
        core_net_routers = [r for r in network_components if isinstance(r, Router)]
        oldInf_to_newInf_map = {}
        for r in core_net_routers:
            for link in r.links:
                oldInf_to_newInf_map[link.this_port] = Copy.copyObj(link)
            
            