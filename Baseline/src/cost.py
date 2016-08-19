from routing import Network_Components
from configure import GlobalConfiguration

from springpython.config import XMLConfig
from springpython.context import ApplicationContext


class CostMap(object):
    
    
    def __init__(self):
            
        #====== COST CONFIGURATION ======================
        self.muxponder_cost  = 10
        self.server_cost     = 1
        
        #COST REDUCTIONS
        self.cost_reduction_fact_SDN = 1               #REDUCTION ON SDN
        self.cost_reduction_fact_NFV = 1               #REDUCTION ON NFV
        
        
        #line rate vs cost
        self.linecard_cost_map = {}
        
        context = ApplicationContext(GlobalConfiguration.config_xml)
        #populate line card cost
        self.linecard_cost_map[ context.get_object("1GE")  ] = 1
        self.linecard_cost_map[ context.get_object("10GE") ] = 2.5
        self.linecard_cost_map[ context.get_object("100GE")] = 12
        #================================================                        
        
        self.aggregate_cost     = 0
    
    def calculate(self):
        
            self.calculate_linecard_cost()
            self.calculate_server_cost()
            self.calculate_muxponder_cost()
            
            return self.aggregate_cost
        
            
    def calculate_linecard_cost(self):
        noOfLinecardsAccountedFor = 0
        for band_width in self.linecard_cost_map:
            
            unit_cost = self.linecard_cost_map[band_width]
            
            linecards_of_same_band_width = [line_card for line_card in Network_Components.linecards if line_card.bandwidth == band_width]
            for linecard in linecards_of_same_band_width:
                if linecard.is_NFV and linecard.is_SDN:
                    raise ValueError("line card happens to be both NFV and SDN")
                elif linecard.is_SDN:
                    self.aggregate_cost += ( unit_cost / self.cost_reduction_fact_SDN )
                elif linecard.is_NFV:
                    self.aggregate_cost += ( unit_cost / self.cost_reduction_fact_NFV )
                else:
                    self.aggregate_cost += ( unit_cost )
                
                noOfLinecardsAccountedFor += 1
                
        if noOfLinecardsAccountedFor != len(  Network_Components.linecards  ):
            raise ValueError("Line cards for which cost is accounted {} doesnt equal actuals {}".format(noOfLinecardsAccountedFor, len(  Network_Components.linecards  )))
     
    def calculate_server_cost(self):
        noOfSinks = len(  Network_Components.sinks  )
        noOfHosts = len(  Network_Components.hosts  )
        
        self.aggregate_cost += (noOfSinks + noOfHosts) * self.server_cost
        
    def calculate_muxponder_cost(self):
        noOfMuxponders = len(  Network_Components.muxs  )

        self.aggregate_cost +=  noOfMuxponders * self.muxponder_cost
        