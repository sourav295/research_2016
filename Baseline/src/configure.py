from springpython.config import XMLConfig
from springpython.context import ApplicationContext

import simpy


class GlobalConfiguration(object):
    
    simpyEnv = simpy.Environment()
    
    @staticmethod
    def configure(configs):
        
        context = ApplicationContext(configs)
        topology = context.get_object("topology")
        topology.wireComponents()
        
