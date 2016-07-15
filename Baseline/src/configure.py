from springpython.config import XMLConfig
from springpython.context import ApplicationContext

import simpy


class GlobalConfiguration(object):
    
    simpyEnv = simpy.Environment()
    

    def configure(self, configs):
        
        context = ApplicationContext(configs)
        topology = context.get_object("topology")
        
        topology.drawRoughGraph()
        topology.wireComponents()
        
        GlobalConfiguration.simpyEnv.run(until=int(200))