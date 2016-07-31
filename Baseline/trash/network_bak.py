import router as router_module
import graph
import routing
import logging
import roadm
from SimComponents import Cable
from configure import GlobalConfiguration

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
        print network_graph_for_topology.edges

    
    
        
        
        
  
class Topology(object):
    
    
    network_components= []
    network_graph = graph.Graph()
    
    def wireComponents(self):

        routing.Network_Components.initialize(self)
        
        ''''Wire Optical Core Componenets'''
        for optical_net in [op_net for op_net in self.network_components if isinstance(op_net, Optical_Core)]:
            optical_net.wireComponenets()
            optical_net.distribut_switching_information(self.network_graph)
            
            
        
        
        all_routers = routing.Network_Components.routers        
        for router in all_routers:
            for link in router.links:
                local_port  = link.this_port #this router's switch port 
                remote_port = link.remote_port #could be the remote  switch_port, sink or host(packet generator)
                
                '''Router Interface connected to another router interdace'''
                if isinstance(remote_port, router_module.Interface):
                    #idetify remote router
                    remote_router  = remote_port.find_host_router(all_routers)
                    self.cable_components(local_port, remote_port)
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_router, local_port)
                    #for dijkstr's calculations
                    self.network_graph.add_edge(router, remote_router, 1)
                    
                '''Router Interface connected to a Packet Generator (Host)'''
                if isinstance(remote_port, router_module.Host):
                    self.cable_components(local_port, remote_port)
                    self.cable_components(remote_port, local_port)
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_port, local_port)
                    #for dijkstr's calculations
                    self.network_graph.add_edge(router, remote_port, 1)
                    self.network_graph.add_edge(remote_port, router, 1)
                    
                '''Router Interface connected to a Packet Sink (Sink)'''
                if isinstance(remote_port, router_module.Sink):
                    self.cable_components(local_port, remote_port)
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_port, local_port)
                    #for dijkstr's calculations
                    self.network_graph.add_edge(router, remote_port, 1)
                    self.network_graph.add_edge(remote_port, router, 1)
                    
                '''Router Interface connected to a Roadm'''
                if isinstance(remote_port, roadm.Roadm):
                    roadm_degree = remote_port.get_an_unconnected_degree()
                    roadm_degree.mark_as_interfacing_outside_network()
                    
                    self.cable_components(local_port,roadm_degree.in_port)
                    self.cable_components(roadm_degree.out_port, local_port)
                    #register in this router's processor
                    local_port.get_routing_processor().add_interface(remote_port, local_port)
                    #for dijkstr's calculations
                    self.network_graph.add_edge(router, remote_port, 1)
                    self.network_graph.add_edge(remote_port, router, 1)
                    
        
        self.network_graph.savefig(GlobalConfiguration.topology_png_file_path)
                
        for router in all_routers:
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
            
    def cable_components(self, from_port, to_port, delay = 10):
        cable = Cable(GlobalConfiguration.simpyEnv, delay)
        from_port.out   = cable
        cable.out       = to_port