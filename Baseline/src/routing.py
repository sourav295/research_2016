import router
import roadm
import random
from configure import GlobalConfiguration
import simpy

class Network_Components(object):
    
    routers = []
    hosts   = []
    sinks   = []
    roadms  = []
    network_graph = None
    
    @staticmethod
    def initialize(topology):
        
        '''' Optical Core Componenets'''
        for optical_net in [op_net for op_net in topology.networks if topology.isOpticalCore(op_net)]:
            Network_Components.roadms.extend( optical_net.all_roadms )
            
        '''' Core Office Components'''
        for core_office in [core_net for core_net in topology.networks if topology.isCoreOffice(core_net)]:
            Network_Components.routers.extend(  [ nc for nc in core_office.network_components if topology.isRouter(nc) ]   )
            Network_Components.hosts.extend(    [ nc for nc in core_office.network_components if topology.isHost(nc)   ]   )
            Network_Components.sinks.extend(    [ nc for nc in core_office.network_components if topology.isSink(nc)   ]   )
             
        Network_Components.network_graph = topology.network_graph

    @staticmethod
    def selectRandomSink():
        all_topology_sinks = Network_Components.sinks
        return (random.choice(all_topology_sinks))

    @staticmethod
    def findExplicitPath(src, dest):
        explicit_path =   Network_Components.network_graph.shortestPath(src, dest)
        #we are only interestd in the border roadms, roadms handle the path it takes. But this path gives necessary info to reach the border roadm from a router
        return roadm.Roadm.expel_inner_roadms_from_path(explicit_path)
'''
#class Routing_Processor(object):
    
    def __init__(self):
        self.out_port_vs_remote_component_map   =   {}
        self.remote_component_vs_store_map      =   {}#each next hop component has a different store
        self.next_hop_to_notification_map       =   {}
        
    def add_interface(self, network_component, local_interface):
        self.out_port_vs_remote_component_map[local_interface]  = network_component
        self.remote_component_vs_store_map[network_component]   = simpy.PriorityStore(GlobalConfiguration.simpyEnv)
        """
        if not network_component in self.next_hop_to_notification_map:
            self.next_hop_to_notification_map[network_component] = GlobalConfiguration.simpyEnv.event()
        local_interface.wait_for_pcks = self.next_hop_to_notification_map[network_component]
        """
    def put(self, pck):
        next_hop = pck.next_hop()
        store = self.remote_component_vs_store_map[next_hop]
        #insert pck to priority item as payload
        priority_item = simpy.PriorityItem(pck.priority, pck)
        #self.notify_interfaces(next_hop)
        return store.put(priority_item)
        
        
    def get_store(self, local_interface):
        network_component = self.out_port_vs_remote_component_map[local_interface]
        store = self.remote_component_vs_store_map[network_component]
        return store
    
    def notify_interfaces(self, next_hop):
        self.next_hop_to_notification_map[next_hop].succeed()
        self.next_hop_to_notification_map[next_hop] = GlobalConfiguration.simpyEnv.event()
        
'''

class Routing_Processor(object):
    
    def __init__(self, local_ports):
        
        self.local_ports = local_ports
        
        self.outPort_to_nextHop_map =   {}
        self.key_to_prioQueue_map   =   {}#key = (next hop, in)
        
    def add_interface(self, next_hop, out_port):
        self.outPort_to_nextHop_map[out_port]  = next_hop
        for in_port in self.local_ports:
            if in_port != out_port and not self.is_inPort_leading_to_nextHop(in_port, next_hop):
                key = (next_hop, in_port)
                if key not in self.key_to_prioQueue_map:
                    self.key_to_prioQueue_map[key] = Priority_Queue(out_port)
                else:
                    prio_que = self.key_to_prioQueue_map[key]
                    prio_que.append_port(out_port)
        
    def put(self, pck, in_port):
        next_hop = pck.next_hop()
        
        #compeiting queues and prio - log information
        competing_priority_queues = [self.key_to_prioQueue_map[k] for k in self.key_to_prioQueue_map if k[0] == next_hop]
        pck.log("{}".format(str(Priority_Queue.findCompetition(competing_priority_queues))))
        
        #key to the appropiate priority queue
        key = (next_hop, in_port)
        print pck
        print pck.explicit_path
        prioQueue = self.key_to_prioQueue_map[key]
        prioQueue.put(pck)
        pck.log("Packet stored in appropiate Queue to reach {}".format(next_hop))
        
        
    def get_all_prio_queues(self, out_port):
        next_hop = self.outPort_to_nextHop_map[out_port]
        all_queues = []
        for in_port in self.local_ports:
            if in_port != out_port and not self.is_inPort_leading_to_nextHop(in_port, next_hop):
                key = (next_hop, in_port)
                all_queues.append(  self.key_to_prioQueue_map[key]  )
        return all_queues
    
    def is_inPort_leading_to_nextHop(self, in_port, next_hop):
        try:
            return in_port.is_adjacent_router([next_hop])
        except AttributeError:
            return False
    
        
class Priority_Queue(object):
    
    def __init__(self, new_port):
        self.queue = []
        self.attached_out_port = [new_port]
        new_port.wait = GlobalConfiguration.simpyEnv.event()
        
    def is_empty(self):
        return False if self.queue else True
    
    def get(self):
        #highesh priority = lowest priority no.
        priority_level_list = [pck.priority for pck in self.queue]
        #print priority_level_list
        highest_priority_index = priority_level_list.index(min(priority_level_list))
        msg = self.queue[highest_priority_index]
        self.queue.remove(msg)
        return msg
    
    def put(self, value):
        self.queue.append(value)
        #notify the out interface
        for port in self.attached_out_port:
            port.wait.succeed()
            port.wait = GlobalConfiguration.simpyEnv.event()
        
    def append_port(self, new_port):
        self.attached_out_port.append(new_port)
        new_port.wait = GlobalConfiguration.simpyEnv.event()
        
    def count(self, priority = None):
        if priority == None:
            return len(self.queue)
        else:
            return len( [msg for msg in self.queue if msg.priority == priority] )
        
        
    @staticmethod
    def findCompetition(competing_queues):
        n = GlobalConfiguration.nPrioLevels+1
        prio_count_map = {}
        #init
        for prio in range(1,n):
            prio_count_map[prio] = 0
        for queue in competing_queues:
            for prio in range(1,n):
                prio_count_map[prio] += queue.count(priority = prio)
        return prio_count_map
