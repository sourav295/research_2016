from springpython.config import XMLConfig
from springpython.context import ApplicationContext

import simpy


class GlobalConfiguration(object):
    
    simpyEnv = simpy.Environment()
    
    @staticmethod
    def configure(configs):
        
        context = ApplicationContext(configs)
        '''
        x3 = context.get_object("x3")
        x2 = context.get_object("x2")
        print x2.a
        print x3.a
        '''
        topology = context.get_object("topology")
        
        topology.wireComponents()
        
'''
class X(object):
    
    a=""
    
class Y(object):
    
    a=""
    
'''    