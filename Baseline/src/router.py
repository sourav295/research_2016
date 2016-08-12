
import simpy
import random
import functools
import graph
import routing
import logging
from roadm import Roadm


from configure import GlobalConfiguration

from SimComponents import PacketGenerator, PacketSink, SwitchPort, Cable, MuxponderPort

class Router(object):

    def __init__(self, hostname, linecards):
        self.hostname   = hostname
        self.linecards  = linecards
        self.backplane  = routing.Routing_Backplane(linecards)

        self.backplane.wire_linecards()
        
        for i in range(len(self.linecards)):
            self.linecards[i].id        = "{}_LC{}".format(self.hostname, i)
            self.linecards[i].backplane =  self.backplane
            
                    
    def __repr__(self):
        return "{}".format(self.hostname)
    
class Linecard(object):

    def __init__(self, bandwidth, links):
        self.links      = links
        self.id         = None
        self.backplane  = None
        self.bandwidth  = bandwidth
        
        
        #Assign default interface
        for link in self.links:
            if link.this_port == None:
                link.this_port  = Interface(self.bandwidth)

        local_ports = [l.this_port for l in self.links]
        self.routing_processor = routing.Routing_Processor(local_ports)
        
        for link in self.links:
            local_port  = link.this_port
            local_port.set_routing_processor(self.routing_processor)
                    
    def __repr__(self):
        return "{}".format(self.id)
    
    @staticmethod
    def switching_fabric_connect(lc_1, lc_2):
        #check if link already exist
        for l in [l1.this_port for l1 in lc_1.links]:
            if l in [l2.remote_port for l2 in lc_2.links]:
                return
        
        
        #create interface of same bandwidth
        inf1  = Interface(lc_1.links[0].this_port.bandwidth)
        inf2  = Interface(lc_2.links[0].this_port.bandwidth)
        link1 = Link(inf1, inf2)
        link2 = Link(inf2, inf1)
        
        inf1.set_routing_processor(lc_1.routing_processor)
        inf2.set_routing_processor(lc_2.routing_processor)
        #amendments
        lc_1.links.append(link1)
        lc_2.links.append(link2)
        
        lc_1.routing_processor.local_ports.append(inf1)
        lc_2.routing_processor.local_ports.append(inf2)
        

class Muxponder(object):
    
    def __init__(self, hostname, links):
        self.hostname   = hostname
        self.links      = links

        local_ports = [l.this_port for l in self.links]
        self.muxponder_processor  = routing.Muxponder_Processor(local_ports)
        
        for link in self.links:
            local_port  = link.this_port
            local_port.set_muxponding_processor(self.muxponder_processor)
    
    def __repr__(self):
        return "{}".format(self.hostname)        

class Link(object):
    def __init__(self, this_port = None, remote_port = None):
        self.this_port    = this_port   #switch port at local end
        self.remote_port  = remote_port #could be switch port, sink or host
        
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.this_port == other.this_port and self.remote_port == other.remote_port)

class Host(PacketGenerator):

    def __init__(self, mean_pkt_size, bandwidth, hostname):
        
        mean_arrv_rate = GlobalConfiguration.mean_arrv_rate
        arrv_time_distribution = functools.partial(random.expovariate, mean_arrv_rate)
        pkt_size_distribution  = functools.partial(random.expovariate, 1.0/float(mean_pkt_size))
        
        PacketGenerator.__init__(self, GlobalConfiguration.simpyEnv, hostname, arrv_time_distribution, pkt_size_distribution, rate = float(bandwidth))
        self.hostname = hostname
    
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
    
    def __init__(self, bandwidth):
        
        SwitchPort.__init__(self, GlobalConfiguration.simpyEnv, float(bandwidth), None, False)
        
        self.bandwidth      = bandwidth
        self.id             = Interface.curr_id
        Interface.curr_id   = Interface.curr_id + 1         
        
    def find_host_linecard(self, linecard_list):
        for linecard in linecard_list:
            for link in linecard.links:
                if link.this_port == self:
                    return linecard
        return None
    
    def is_adjacent_linecard(self, next_hop_lc):
        for linecard in next_hop_lc:
            for link in linecard.links:
                if link.remote_port == self:
                    return True
        return False
                

    def __repr__(self):
        return "(Inf){}".format(self.id)

class MuxInterface(MuxponderPort):
    
    curr_id = 0
    
    def __init__(self, bandwidth, is_upstream_bound = False):
        
        MuxponderPort.__init__(self, GlobalConfiguration.simpyEnv, float(bandwidth), is_upstream_bound)
        
        self.id                = MuxInterface.curr_id
        MuxInterface.curr_id   += 1
        self.is_upstream_bound = is_upstream_bound
    
    def find_host_muxponder(self, muxponders):
        for mux in muxponders:
            for link in mux.links:
                if link.this_port == self:
                    return mux
        return None

    def __repr__(self):
        return "(MuxInf){}".format(self.id)

        