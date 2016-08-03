from springpython.config import XMLConfig
from springpython.context import ApplicationContext

import simpy
import logging




class GlobalConfiguration(object):
    
    #simpy simulation
    simpyEnv = simpy.Environment()
    
    #spring xml resources
    config_xml = [XMLConfig("resource/xml/Topology.xml"), XMLConfig("resource/xml/Router.xml"), XMLConfig("resource/xml/Roadm.xml")]
    
    #topology png file path
    topology_png_file_path = "./resource/log/path_graph.png"
    
    #nPriorityLevels
    nPrioLevels = 3
    
    @staticmethod
    def configure():
        
        #topology logger
        logger = logging.getLogger("topology")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('./resource/log/topology.log', mode='w')
        logger.addHandler(handler)
        #simulation logger
        logger_2 = logging.getLogger("simulation")
        logger_2.setLevel(logging.INFO)
        handler_2 = logging.FileHandler('./resource/log/simulation.log', mode='w')
        logger_2.addHandler(handler_2)
        #packet logger
        logger_3 = logging.getLogger("packets")
        logger_3.setLevel(logging.INFO)
        handler_3 = logging.FileHandler('./resource/log/packet.log', mode='w')
        logger_3.addHandler(handler_3)
        
        
        context = ApplicationContext(GlobalConfiguration.config_xml)
        topology = context.get_object("topology")
        topology.wireComponents()
        
        #test = context.get_object("optcl_net")
        #test.wireComponenets()
        

        
        