
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

    def __init__(self, hostname, linecards, is_SDN = False, is_NFV = False):
        self.hostname   = hostname
        self.linecards  = linecards
        self.backplane  = routing.Routing_Backplane(linecards)

        #self.backplane.wire_linecards()
    
        self.is_SDN = is_SDN
        self.is_NFV = is_NFV
        
        for i in range(len(self.linecards)):
            #COMPLETE LINE CARD SETUP
            self.linecards[i].id        = "{}_LC{}".format(self.hostname, i)
            self.linecards[i].backplane =  self.backplane
            #init the servers attached to linecard
            self.linecards[i].connect_servers()
            #init the routing processor, notify interfaces
            self.linecards[i].config_routing_processor()
            
        self.backplane.wire_linecards()
        
        self.is_ethernet_switch = False
            
    def set_as_SDN(self):
        self.is_SDN = True
        for linecard in self.linecards:
            linecard.set_as_SDN()
    def set_as_NFV(self):
        self.is_NFV = True
        for linecard in self.linecards:
            linecard.set_as_NFV()
    def set_as_ethernet_switch(self):
        self.is_ethernet_switch = True
            
    def __repr__(self):
        return "{}".format(self.hostname)
    
class Linecard(object):

    def __init__(self, bandwidth, links = None, connected_servers = None):
        self.links      = links if links != None else []
        self.id         = None
        self.backplane  = None
        self.bandwidth  = bandwidth
        
        self.is_SDN = False
        self.is_NFV = False
        
        self.routing_processor = None
        self.connected_servers = connected_servers
        
        
    def config_routing_processor(self):
        
        local_ports = [l.this_port for l in self.links]
        
        self.routing_processor = routing.Routing_Processor(local_ports)
        
        for link in self.links:
            local_port  = link.this_port
            local_port.set_routing_processor(self.routing_processor)
            if local_port.rate != self.bandwidth:
                raise ValueError("Configuration error - the linecard rate doesnt match the port rate")
            
    def multiply(self, link, remote_line_card):
        n_port_lc = GlobalConfiguration.nOfPortPerLC
        if n_port_lc > 1:
            for i in range(n_port_lc): 
                copy_this_port, copy_this_link, copy_remote_port, copy_remote_link  = link.copy1()
                
                copy_this_port.set_routing_processor(self.routing_processor)
                copy_remote_port.set_routing_processor(remote_line_card.routing_processor)
                #amendments
                self.links.append(copy_this_link)
                remote_line_card.links.append(copy_remote_link)
                
                self.routing_processor.local_ports.append(copy_this_port)
                remote_line_card.routing_processor.local_ports.append(copy_remote_port)
                
    def connect_servers(self):
        if self.connected_servers != None:
            host_bandwidth = self.connected_servers.bandwidth
            linecard_id    = self.id
            for i in range(self.connected_servers.no_of_servers):
                host_id = "{}_G{}".format(linecard_id, i)
                sink_id = "{}_S{}".format(linecard_id, i)
                
                h = Host( host_bandwidth, host_id)
                s = Sink( sink_id )

                inf_h = Interface(self.bandwidth)
                inf_s = Interface(self.bandwidth)
                
                link_h = Link(inf_h , h)
                link_s = Link(inf_s , s)
        
                self.links.append(  link_h  )
                self.links.append(  link_s  )
                
    
    def set_as_SDN(self):
        #check if it not set as NFV
        if self.is_NFV:
            raise ValueError("line card happens to be both NFV and SDN")
        #mark as SDN
        self.is_SDN = True
        for link in self.links:
            local_port  = link.this_port
            local_port.set_delay_factor(  GlobalConfiguration.delay_fact_SDN  )
            
    def set_as_NFV(self):
        #check if it not set as SDN
        if self.is_SDN:
            raise ValueError("line card happens to be both NFV and SDN")
        #mark as NFV
        self.is_NFV = True
        for link in self.links:
            local_port  = link.this_port
            local_port.set_delay_factor(  GlobalConfiguration.delay_fact_NFV  )
    
    def __repr__(self):
        return "{}".format(self.id)
    
    @staticmethod
    def switching_fabric_connect(lc_1, lc_2):
        #check if link already exist
        for l in [l1.this_port for l1 in lc_1.links]:
            if l in [l2.remote_port for l2 in lc_2.links]:
                return #nothing has to be done
        
        
        #create interface of same bandwidth
        inf1  = Interface(lc_1.bandwidth)
        inf2  = Interface(lc_2.bandwidth)
        link1 = Link(inf1, inf2, 0)#delay set to zero
        link2 = Link(inf2, inf1, 0)#delay set to zero
        
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
            #local_port.id += " "+hostname 
            local_port.set_muxponding_processor(self.muxponder_processor)
    
    def __repr__(self):
        return "{}".format(self.hostname)        

class Link(object):
    def __init__(self, this_port = None, remote_port = None, delay = None):
        self.this_port    = this_port   #switch port at local end
        self.remote_port  = remote_port #could be switch port, sink or host
        self.delay        = delay
        
        if self.delay == None:
            self.delay = GlobalConfiguration.delay_over_IP
            
    def copy1(self):#remote port has to be a router interface
        copy_this_port  = self.this_port.copy1()
        copy_remote_port= self.remote_port.copy1()
        copy_this_link  = Link(copy_this_port,  copy_remote_port, self.delay)
        copy_remote_link= Link(copy_remote_port,copy_this_port,   self.delay)
        
        return copy_this_port, copy_this_link, copy_remote_port, copy_remote_link 
        
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.this_port == other.this_port and self.remote_port == other.remote_port)

class Host(PacketGenerator):

    def __init__(self, bandwidth, hostname):
        
        mean_arrv_rate = GlobalConfiguration.mean_arrv_rate
        mean_pkt_size  = GlobalConfiguration.mean_pkt_size
        
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
                
    def copy1(self):
        return Interface(self.bandwidth)

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
    
class Server(object):
    
    def __init__(self, bandwidth, no_of_servers):
        self.bandwidth     = bandwidth
        self.no_of_servers = int(no_of_servers)
        
        