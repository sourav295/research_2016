from springpython.config import XMLConfig
from springpython.context import ApplicationContext

import simpy
import logging



class GlobalConfiguration(object):
    
    
    
    #topology png file path
    topology_png_file_path = "./resource/log/path_graph.png"
    
    
    #simulation
    queue_log  = False
    
    architecture_list = ("baseline", "streamline")
    #Main configs: ===========================================================
    achitecture     = architecture_list[0]  
    
    qlimit          = 50000             # bytes
    delay_over_IP   = 1                 # delay over ip channel
    N_Channels      = 200               # on optical fibre
    nPrioLevels     = 3                 # no of priority levels
    
    start_rate      = 17                # first pkt generation rate
    end_rate        = 17.5              # last  pkt generation rate
    rate_increments = 0.1               # increments
    
    simulation_until= 100               # Simulation time
    
    test_run        = False              # runs the code only for the start_rate, information logged
    #=========================================================================
    
    #spring xml resources
    config_xml = [  XMLConfig("resource/xml/" + achitecture + "/Topology.xml"), \
                    XMLConfig("resource/xml/" + achitecture + "/Router.xml"),   \
                    XMLConfig("resource/xml/" + achitecture + "/Roadm.xml")      ]
    
    
    #Not configurable
    mean_arrv_rate  = None        # 1/arrival_time
    topology        = None
    to_log          = True
    simpyEnv        = simpy.Environment()
    
    
    @staticmethod
    def configure():
        #if log ?
        log_type = logging.INFO if GlobalConfiguration.to_log else logging.ERROR
        
        #topology logger
        logger = logging.getLogger("topology")
        logger.setLevel(log_type)
        handler = logging.FileHandler('./resource/log/topology.log', mode='w')
        logger.addHandler(handler)
        
        #simulation logger
        logger_2 = logging.getLogger("simulation")
        logger_2.setLevel(log_type)
        handler_2 = logging.FileHandler('./resource/log/simulation.log', mode='w')
        logger_2.addHandler(handler_2)
        
        #packet logger
        logger_3 = logging.getLogger("packets")
        logger_3.setLevel(log_type)
        handler_3 = logging.FileHandler('./resource/log/packet.log', mode='w')
        logger_3.addHandler(handler_3)
        
        
        #----- WIRING
        
        GlobalConfiguration.simpyEnv = simpy.Environment()
        context = ApplicationContext(GlobalConfiguration.config_xml)
        
        topology = context.get_object("topology")
        GlobalConfiguration.topology = topology #reqd for statistic generations
        
        topology.wireComponents()
        
    @staticmethod
    def getStats():# returns #of pkts dropped and # of pkts generated
        return GlobalConfiguration.topology.getStats()
        
        