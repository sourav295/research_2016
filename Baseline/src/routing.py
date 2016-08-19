import router
import roadm
import random
from configure import GlobalConfiguration
import simpy

class Network_Components(object):
    
    routers  = []
    hosts    = []
    sinks    = []
    roadms   = []
    muxs     = []
    linecards= []
    
    total_cost    = 0
    network_graph = None
    
    @staticmethod
    def initialize(topology):
        
        '''' Optical Core Componenets'''
        for optical_net in [op_net for op_net in topology.networks if topology.isOpticalCore(op_net)]:
            Network_Components.roadms.extend( optical_net.all_roadms )
            
        '''' Core Office Components'''
        for core_office in [core_net for core_net in topology.networks if topology.isCoreOffice(core_net)]:
            
            rs = [ nc for nc in core_office.network_components if topology.isRouter(nc) ]
            Network_Components.routers.extend(rs)
            for r in rs:
                Network_Components.linecards.extend( r.linecards )
                '''
                for l in r.linecards:
                    Network_Components.hosts.extend(    [ link.this_port for link in l.links if topology.isHost(link.remote_port)   ]   )
                    Network_Components.sinks.extend(    [ link.this_port for link in l.links if topology.isSink(link.remote_port)   ]   )
            '''
            Network_Components.hosts.extend(    [ nc for nc in core_office.network_components if topology.isHost(nc)   ]   )
            Network_Components.sinks.extend(    [ nc for nc in core_office.network_components if topology.isSink(nc)   ]   )
            
            Network_Components.muxs.extend(     [ nc for nc in core_office.network_components if topology.isMux(nc)    ]   )
        
        Network_Components.network_graph = topology.network_graph
        
        print "SDN", [r for r in Network_Components.routers if r.is_SDN]
        print "NFV", [r for r in Network_Components.routers if r.is_NFV]

    @staticmethod
    def selectRandomSink():
        all_topology_sinks = Network_Components.sinks
        return (random.choice(all_topology_sinks))

    @staticmethod
    def findExplicitPath(src, dest):
        explicit_path =   Network_Components.network_graph.shortestPath(src, dest)
        #we are only interestd in the border roadms, roadms handle the path it takes. But this path gives necessary info to reach the border roadm from a router
        #Muxponder_Processor.remove_path_error(explicit_path)
        return roadm.Roadm.expel_inner_roadms_from_path(explicit_path)
    
    @staticmethod
    def getStats():
        queues = []
        for l in Network_Components.linecards:
            map = l.routing_processor.key_to_prioQueue_map
            for key in map:
                if not map[key] in queues:
                    queues.append(map[key])
                    
        return sum(c.packets_drop for c in queues)
    
        
    @staticmethod
    def flush():
        Network_Components.routers  = []
        Network_Components.hosts    = []
        Network_Components.sinks    = []
        Network_Components.roadms   = []
        Network_Components.muxs     = []
        Network_Components.linecards= []
        
        Network_Components.total_cost    = 0
        Network_Components.network_graph = None

class Muxponder_Processor(object):
    
    def __init__(self, local_ports):
        self.local_ports            = local_ports
        self.outPort_nextHop_map    = {}
        self.nextHop_Store_map      = {}
        
    def add_interface(self, next_hop, out_port):
        self.outPort_nextHop_map[out_port]  = next_hop
        self.nextHop_Store_map[next_hop]    = simpy.Store(GlobalConfiguration.simpyEnv)

    def getStore(self, out_port):
        return self.nextHop_Store_map[  self.outPort_nextHop_map[out_port]  ]
    
    def putStore(self, next_hop, muxponder_port):
        return self.nextHop_Store_map[  next_hop  ]
        
    '''Required for wiring'''
    #returns only 1 ustream network component
    def getNextHopOnUpstreamInf(self):
        return self.outPort_nextHop_map[ self.getUpstreamBoundInf() ]
    #returns a list of downstream network components
    def getNextHopListOnDownstreamInfs(self):
        nxtHopOnUpstream = self.getNextHopOnUpstreamInf()
        return [x for x in self.nextHop_Store_map if x != nxtHopOnUpstream]
    def getUpstreamBoundInf(self):
        upstreamBounfInfs = [inf for inf in self.local_ports if inf.is_upstream_bound]
        if len(upstreamBounfInfs) == 1:
            return upstreamBounfInfs[0]
        else:
            raise ValueError('Upstream Bound interface more or less than 1: {}'.format(len(upstreamBounfInfs)))
            
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
        
        #competing queues and prio - log information
        competing_priority_queues = [self.key_to_prioQueue_map[k] for k in self.key_to_prioQueue_map if k[0] == next_hop]
        pck.log("{}".format(str(Priority_Queue.findCompetition(competing_priority_queues))))
        
        #key to the appropiate priority queue
        key = (next_hop, in_port)
        try:
            prioQueue = self.key_to_prioQueue_map[key]
        except:
            router_list = [r for r in Network_Components.linecards if r.routing_processor == self]
            key_list    = [k for k in self.key_to_prioQueue_map]
            raise ValueError('Problem with path {}, next hop {}, router: {} \n {}'.format(pck.explicit_path, next_hop, router_list[0], key_list))
        
        pck.log("Packet stored in appropiate Queue to reach {}".format(next_hop))
        prioQueue.put(pck)
        
        
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
            return in_port.is_adjacent_linecard([next_hop])
        except AttributeError:
            return False
    
class Routing_Backplane(object):
    
    def __init__(self, linecards):
        self.linecards = linecards
        
    def wire_linecards(self):
        for linecard1 in self.linecards:
            for linecard2 in self.linecards:
                if linecard1 != linecard2:
                    router.Linecard.switching_fabric_connect(linecard1, linecard2)
                
        
class Priority_Queue(object):
    
    def __init__(self, new_port):
        self.queue = []
        self.attached_out_port = [new_port]
        new_port.wait = GlobalConfiguration.simpyEnv.event()
        
        self.qlimit       = GlobalConfiguration.qlimit
        self.byte_size    = 0
        self.packets_drop = 0
        
    def is_empty(self):
        return False if self.queue else True
    
    def get(self):
        #highesh priority => lowest priority no.
        priority_level_list = [pck.priority for pck in self.queue]
        #print priority_level_list
        highest_priority_index = priority_level_list.index(min(priority_level_list))
        msg = self.queue[highest_priority_index]
        self.queue.remove(msg)
        
        self.byte_size -= msg.size                      
        return msg
    
    def put(self, value):
        tmp = self.byte_size + value.size
        if tmp >= self.qlimit:
            self.packets_drop += 1
            value.log("!! Dropped")
        else:
            self.queue.append(value)
            self.byte_size = tmp
            #notify the out interface
            for port in self.attached_out_port:
                port.wait.succeed()
                port.wait = GlobalConfiguration.simpyEnv.event()
                if GlobalConfiguration.queue_log:
                    value.log("Port {}, notified of arrival".format(str(port)))
            
    def append_port(self, new_port):
        self.attached_out_port.append(new_port)
        new_port.wait = GlobalConfiguration.simpyEnv.event()
        
    def count(self, priority = None):
        if priority == None:
            return len(self.queue)
        else:
            return len( [msg for msg in self.queue if msg.priority == priority] )
        
    '''Used for loggin'''
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
    
    '''Used for loggin'''
    @staticmethod
    def notify_pcks(msg, port, competing_queues, time, string_msg):
        for q in competing_queues:
            for pck in q.queue:
                if msg != pck:
                    pck.log("At {} By {} :\n\t{} \n\t{}".format(time, port,  string_msg, Priority_Queue.findCompetition(competing_queues)))