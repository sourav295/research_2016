import router as router_module
import graph
import routing
import logging
import roadm
from SimComponents import Cable, Packet
from configure import GlobalConfiguration
import functools
import copy
#logging topology
topology_logger = logging.getLogger("topology") 

class Optical_Core(object):
    
    all_roadms = []
    connections= []
    network_graph = graph.Graph()
    
    def wireComponenets(self):
        for link in self.connections:
            link.connect()
            self.network_graph.add_edge(link.frm, link.to , 1)
            self.network_graph.add_edge(link.to , link.frm, 1)
    
    def distribut_switching_information(self, network_graph_for_topology):
        border_roadms = roadm.Roadm.get_border_roadms(self.all_roadms)
        for ingress_roadm in border_roadms:
            for egress_roadm in border_roadms:
                if not ingress_roadm == egress_roadm:
                    #distribute Labels at each RoadM in the optical network-
                    path = self.network_graph.shortestPath(ingress_roadm, egress_roadm)
                    ingress_roadm.distribute_labels(egress_roadm, path)
        for link in self.connections:
            network_graph_for_topology.add_edge(link.frm, link.to , 1)
            network_graph_for_topology.add_edge(link.to , link.frm, 1)
        #print network_graph_for_topology.edges

class Core_Office(object):
    
    def __init__(self, network_components):
        self.network_components = network_components
        
    def wireComponenets(self):
               
        all_routers     = [ r for r in self.network_components if isinstance(r, router_module.Router) ]#all routers in this core office
        all_muxponders  = [ m for m in self.network_components if isinstance(m, router_module.Muxponder) ]
        network_graph   = routing.Network_Components.network_graph
        
        all_linecards = []
        for r in all_routers:
            all_linecards.extend(r.linecards)
        
        
        '''Make muxponders aware of their surroundings'''
        for mux in all_muxponders:
            for link in mux.links:
                local_mux_port  = link.this_port #this mux's local port 
                remote_port     = link.remote_port #this is the remote port
                if isinstance(remote_port, router_module.Interface):
                    #idetify remote router
                    remote_linecard  = remote_port.find_host_linecard(routing.Network_Components.linecards)
                    local_mux_port.addInterface(remote_linecard) #create entry
                elif isinstance(remote_port, roadm.Roadm):
                    central_add_drop  = remote_port.add_drop_module
                    
                    self.cable_components(  local_mux_port        ,central_add_drop.Tx    )
                    self.cable_components(  central_add_drop.Rx   ,local_mux_port         )
                    #register in this router's processor
                    local_mux_port.addInterface(remote_port)
                    #for dijkstr's calculations
                    network_graph.add_edge(mux, remote_port, 1)
                    network_graph.add_edge(remote_port, mux, 1)
                else:
                    raise ValueError('This case has not been handled')
                    
                    
        '''Make routers/ linecards aware of their surrounding'''
        for linecard in all_linecards:
            for link in linecard.links:
                local_port  = link.this_port #this router's switch port 
                remote_port = link.remote_port #could be the remote  switch_port, sink or host(packet generator)
                
                '''Router Interface connected to another router interface'''
                if isinstance(remote_port, router_module.Interface):
                    #idetify remote line card
                    remote_linecard  = remote_port.find_host_linecard(routing.Network_Components.linecards)
                    self.cable_components(local_port, remote_port)
                    #register in this router's processor
                    local_port.addInterface(remote_linecard)
                    #for dijkstr's calculations
                    if linecard.backplane != remote_linecard.backplane:
                        network_graph.add_edge(linecard, remote_linecard, 1)
                    else:
                        network_graph.add_edge(linecard, remote_linecard, 0)
                    
                '''Router Interface connected to a Packet Generator (Host)'''
                if isinstance(remote_port, router_module.Host):
                    self.cable_components(local_port, remote_port)
                    self.cable_components(remote_port, local_port)
                    #register in this router's processor
                    local_port.addInterface(remote_port)
                    #for dijkstr's calculations
                    network_graph.add_edge(linecard, remote_port, 1)
                    network_graph.add_edge(remote_port, linecard, 1)
                    
                '''Router Interface connected to a Packet Sink (Sink)'''
                if isinstance(remote_port, router_module.Sink):
                    self.cable_components(local_port, remote_port)
                    #register in this router's processor
                    local_port.addInterface(remote_port)
                    #for dijkstr's calculations
                    network_graph.add_edge(linecard, remote_port, 1)
                    network_graph.add_edge(remote_port, linecard, 1)
                    
                '''Router Interface connected to a Roadm'''
                if isinstance(remote_port, roadm.Roadm):
                    central_add_drop  = remote_port.add_drop_module
                    
                    self.cable_components(  local_port            ,central_add_drop.Tx    )
                    self.cable_components(  central_add_drop.Rx   , local_port            )
                    #register in this router's processor
                    local_port.addInterface(remote_port)
                    #for dijkstr's calculations
                    network_graph.add_edge(linecard, remote_port, 1)
                    network_graph.add_edge(remote_port, linecard, 1)
                    
                '''Router Interface connected to another Muxponder interface'''
                if isinstance(remote_port, router_module.MuxInterface):
                    #idetify remote muxponder
                    self.cable_components(local_port, remote_port)
                    self.cable_components(remote_port, local_port)
                    remote_mux  = remote_port.find_host_muxponder(routing.Network_Components.muxs)
                    #register in this router's processor
                    local_port.addInterface(remote_mux)
                    #for dijkstr's calculations
                    network_graph.add_edge(linecard, remote_mux, 1)
                    network_graph.add_edge(remote_mux, linecard, 1)
                
        
        
    def cable_components(self, from_port, to_port, delay = GlobalConfiguration.delay_over_IP):
        cable = Cable(GlobalConfiguration.simpyEnv, delay)
        from_port.out   = cable
        cable.out       = to_port
  
class Topology(object):
    
    networks= []
    network_graph = graph.Graph()
    
    def isInstOf(instance, type):
        return isinstance(instance, type)
    
    isLinecard = functools.partial(isInstOf, type=router_module.Linecard)
    isRouter   = functools.partial(isInstOf, type=router_module.Router)
    isHost     = functools.partial(isInstOf, type=router_module.Host)
    isSink     = functools.partial(isInstOf, type=router_module.Sink)
    isMux      = functools.partial(isInstOf, type=router_module.Muxponder)
    
    isOpticalCore = functools.partial(isInstOf, type=Optical_Core)
    isCoreOffice  = functools.partial(isInstOf, type=Core_Office)
    
    def wireComponents(self):
        
        routing.Network_Components.flush()

        routing.Network_Components.initialize(self)
        Packet.all_packets_generated = []   #flush all the previous generated packets
        
        ''''Wire Optical Core Componenets'''
        for optical_net in [op_net for op_net in self.networks if isinstance(op_net, Optical_Core)]:
            optical_net.wireComponenets()
            optical_net.distribut_switching_information(self.network_graph)
            
        ''''Wire Core Office Components'''
        for core_office in [core_net for core_net in self.networks if isinstance(core_net, Core_Office)]:
            core_office.wireComponenets()
        
        if GlobalConfiguration.to_log:
            self.log_topology()
        
        
    def log_topology(self):
        #save graph png
        self.network_graph.savefig(GlobalConfiguration.topology_png_file_path)
                
        for router in routing.Network_Components.routers:
            topology_logger.info("=========================================")
            
            #--------
            topology_logger.info("Router: {}".format(router))
            for linecard in router.linecards:
                topology_logger.info("-----------------------------------------")
                topology_logger.info("===={}====".format(linecard))
                port_component_map = linecard.routing_processor.outPort_to_nextHop_map
                for local_port in port_component_map:
                    topology_logger.info("local port: {:10} -- next componenet --> remote component: {:10}".format(local_port, port_component_map[local_port]))
                topology_logger.info("-----------------------------------------")
            
            #print router link information
            for linkcard in router.linecards:
                topology_logger.info("<===={}====>".format(linkcard))
                for link in linkcard.links:
                    topology_logger.info("local port: {:10} -- connected to --> remote port: {:10}".format(link.this_port, link.remote_port))
            #--------
            
            topology_logger.info("=========================================")
            
            
        all_border_roadms = roadm.Roadm.get_border_roadms(routing.Network_Components.roadms)
        if all_border_roadms != None:
            for border_roadms in all_border_roadms:
                topology_logger.info("||||=========================================||||")
                topology_logger.info("{}".format(border_roadms))
                topology_logger.info("{}".format(border_roadms.LFIB))
    
    def getStats(self):#nOfPktdropped, nOfPktGenerated
        return routing.Network_Components.getStats(), Packet.getStats()
    
class NFV_SDN(object):
    sdn_list = []
    nfv_list = []
    
    def distribute_information(self):
        for sdn in self.sdn_list:
            sdn.set_as_SDN()
        for nfv in self.nfv_list:
            nfv.set_as_NFV()
