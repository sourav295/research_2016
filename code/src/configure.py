from springpython.config import XMLConfig
from springpython.context import ApplicationContext

import simpy
import logging
import os

class GlobalConfiguration(object):
    
    
    
    #topology png file path
    topology_png_file_path = None
    
    
    #simulation
    queue_log  = False
    

    #Main configs: ===========================================================
    
    qlimit          = 50000             # bytes
    mean_pkt_size   = 576               # bytes
    delay_over_IP   = 0.00001           # delay over ip channel 0.00001
    N_Channels      = 192              # on optical fibre
    nPrioLevels     = 8                 # no of priority levels
    
    start_rate      = 10                  # first pkt generation rate
    end_rate        = 15                  # last  pkt generation rate
    rate_increments = 0.5                # increments
    
    delay_fact_SDN  = 1.2
    delay_fact_NFV  = 1.2
    
    simulation_until= 10                # Simulation time
    
    test_run        = False              # runs the code only for the start_rate, information logged
    
    simulate_delay_on_server = True
    #=========================================================================
    
    job_description = None
    config_xml      = None
    log_folder      = None
    result_log      = None
    job_id          = None
    job_stat_log    = None
    
    #Not configurable
    mean_arrv_rate  = None        # 1/arrival_time
    topology        = None
    to_log          = True
    simpyEnv        = simpy.Environment()
    SDN_list        = []
    NFV_list        = []
    
    @staticmethod
    def configure():
        
        #----- WIRING
        
        GlobalConfiguration.simpyEnv = simpy.Environment()
        context      = ApplicationContext(GlobalConfiguration.config_xml)
        
        topology = context.get_object("topology")
        GlobalConfiguration.topology = topology #reqd for statistic generations

        sdn_nfv = context.get_object("nfv_sdn")
        sdn_nfv.distribute_information()
        
        topology.wireComponents()
        
    @staticmethod
    def parse_options(args):
        
        GlobalConfiguration.job_id      = args[1]
        root_dir                        = args[2]
        GlobalConfiguration.result_log  = args[3]
        GlobalConfiguration.job_stat_log= args[4]
        
        xml_files = ["/xml/Topology.xml", "/xml/Router.xml", "/xml/Roadm.xml"]

        #----error check
        if len(args) != 5:
            raise ValueError("Option parse error - [JOB ID], [ job root dir path ] , [ final result log ]")

        #check if config files exist
        for file in xml_files:
            file_path = root_dir + file
            if not os.path.isfile(file_path):
                raise ValueError("{} does not exist".format(file_path))
        #---------------
        
        GlobalConfiguration.config_xml              = [XMLConfig(root_dir + file) for file in xml_files]
        GlobalConfiguration.topology_png_file_path  = root_dir + "/log/path_graph.png"
        GlobalConfiguration.log_folder              = root_dir + "/log/"
        
        description = open(root_dir + "/description.txt", 'r')
        GlobalConfiguration.job_description = description.read().replace('\n', '')
        
        print GlobalConfiguration.job_description
        
        GlobalConfiguration.config_log(GlobalConfiguration.log_folder)
        
    @staticmethod
    def config_log(log_dir):
        #if log ?
        log_type = logging.INFO if GlobalConfiguration.to_log else logging.ERROR
        
        for log_category in ["topology", "simulation", "packets"]:
           #topology logger
            logger = logging.getLogger(log_category)
            logger.setLevel(log_type)
            handler = logging.FileHandler(log_dir + log_category +'.log', mode='w')
            logger.addHandler(handler)
    
    @staticmethod
    def getStats():# returns #of pkts dropped and # of pkts generated
        return GlobalConfiguration.topology.getStats()
        