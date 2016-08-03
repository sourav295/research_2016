import router as router_module
import graph
import routing
import logging
import roadm
from SimComponents import Cable
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
    
    def __init__(self, network_components= None, copy_core_office = None, core_office_change = None):
        if network_components != None and copy_core_office == None and core_office_change == None:
            #normal initialization
            self.network_components = network_components
        elif network_components == None and copy_core_office != None and core_office_change != None:
            #copy constructor - "reference to core office" and "core office changes" has to be provided
            #temp_list = copy_core_office.network_components
            '''COPY CODE NOT COMPLETE'''
            #self.network_components = [router_module.Copy.execute(net_comp) for net_comp in temp_list]
            #implement change
            core_office_change.implement_change(self.network_components)
        else:
            raise ValueError('You can either have normal initialization OR copy, no other option')
        

        
    def wireComponenets(self):
               
        all_routers = [ r for r in self.network_components if isinstance(r, router_module.Router) ]#all routers in this core office
        network_graph = routing.Network_Components.network_graph
        
        for router in all_routers:
            for link in router.links:
                local_port  = link.this_port #this router's switch port 
                remote_port = link.remote_port #could be the remote  switch_port, sink or host(packet generator)
                
                '''Router Interface connected to another router interface'''
                if isinstance(remote_port, router_module.Interface):
                    #idetify remote router
                    remote_router  = remote_port.find_host_router(routing.Network_Components.routers)
                    self.cable_components(local_port, remote_port)
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_router, local_port)
                    #for dijkstr's calculations
                    network_graph.add_edge(router, remote_router, 1)
                    
                '''Router Interface connected to a Packet Generator (Host)'''
                if isinstance(remote_port, router_module.Host):
                    self.cable_components(local_port, remote_port)
                    self.cable_components(remote_port, local_port)
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_port, local_port)
                    #for dijkstr's calculations
                    network_graph.add_edge(router, remote_port, 1)
                    network_graph.add_edge(remote_port, router, 1)
                    
                '''Router Interface connected to a Packet Sink (Sink)'''
                if isinstance(remote_port, router_module.Sink):
                    self.cable_components(local_port, remote_port)
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_port, local_port)
                    #for dijkstr's calculations
                    network_graph.add_edge(router, remote_port, 1)
                    network_graph.add_edge(remote_port, router, 1)
                    
                '''Router Interface connected to a Roadm'''
                if isinstance(remote_port, roadm.Roadm):
                    roadm_degree = remote_port.get_an_unconnected_degree()
                    roadm_degree.mark_as_interfacing_outside_network()
                    
                    self.cable_components(local_port,roadm_degree.in_port)
                    self.cable_components(roadm_degree.out_port, local_port)
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_port, local_port)
                    #for dijkstr's calculations
                    network_graph.add_edge(router, remote_port, 1)
                    network_graph.add_edge(remote_port, router, 1)
        
        
    def cable_components(self, from_port, to_port, delay = 10):
        cable = Cable(GlobalConfiguration.simpyEnv, delay)
        from_port.out   = cable
        cable.out       = to_port
  
class Topology(object):
    
    networks= []
    network_graph = graph.Graph()
    
    def isInstOf(instance, type):
        return isinstance(instance, type)
    
    isRouter = functools.partial(isInstOf, type=router_module.Router)
    isHost   = functools.partial(isInstOf, type=router_module.Host)
    isSink   = functools.partial(isInstOf, type=router_module.Sink)
    
    isOpticalCore = functools.partial(isInstOf, type=Optical_Core)
    isCoreOffice  = functools.partial(isInstOf, type=Core_Office)
    
    def wireComponents(self):

        routing.Network_Components.initialize(self)
        
        ''''Wire Optical Core Componenets'''
        for optical_net in [op_net for op_net in self.networks if isinstance(op_net, Optical_Core)]:
            optical_net.wireComponenets()
            optical_net.distribut_switching_information(self.network_graph)
            
        ''''Wire Core Office Components'''
        for core_office in [core_net for core_net in self.networks if isinstance(core_net, Core_Office)]:
            core_office.wireComponenets()
        
        self.log_topology()
        
        
    def log_topology(self):
        #save grsph png
        self.network_graph.savefig(GlobalConfiguration.topology_png_file_path)
                
        for router in routing.Network_Components.routers:
            topology_logger.info("=========================================")
            topology_logger.info("Router: {}".format(router))
            #print routing processor
            topology_logger.info("-----------------------------------------")
            port_component_map = router.routing_processor.outPort_to_nextHop_map
            for local_port in port_component_map:
                topology_logger.info("local port: {:10} -- next componenet --> remote component: {:10}".format(local_port, port_component_map[local_port]))
            topology_logger.info("-----------------------------------------")
            #print router link information
            for link in router.links:
                topology_logger.info("local port: {:10} -- connected to --> remote port: {:10}".format(link.this_port, link.remote_port))
            topology_logger.info("=========================================")
            
            
        for border_roadms in roadm.Roadm.get_border_roadms(routing.Network_Components.roadms):
            topology_logger.info("||||=========================================||||")
            topology_logger.info("{}".format(border_roadms))
            topology_logger.info("{}".format(border_roadms.LFIB))
        
class Core_Office_Change(object):
    
    def __init__(self, ref_of_link_to_ammend, new_remote_port):
        self.ref_of_link_to_ammend  = ref_of_link_to_ammend
        self.new_remote_port        = new_remote_port
        
    def implement_change(deep_copied_network_list):
        for net_comp in deep_copied_network_list:
            if isinstance(net_comp, router_module.Router):
                matched_links = [link for link in net_comp.links if  self.ref_of_link_to_ammend == link ]
                if matched_links:
                    #match found! - amend
                    matched_links[0].remote_port = self.new_remote_port
                    return
        
        raise ValueError('No matching link found while copying core network')
        