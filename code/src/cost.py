from routing import Network_Components
from configure import GlobalConfiguration

from springpython.config import XMLConfig
from springpython.context import ApplicationContext


class CostMap(object):
    
    
    def __init__(self, sdn_cost_benefit, nfv_cost_benefit):
            
        #====== COST CONFIGURATION ======================
        
        '''===================CAPEX==========================='''
        self.capex_muxponder_cost  = 10
        self.capex_server_cost     = 1
        
        #COST REDUCTIONS - amended cost = traditional cost / cost reduction
        self.capex_cost_reduction_fact_SDN = sdn_cost_benefit        #REDUCTION ON SDN
        self.capex_cost_reduction_fact_NFV = nfv_cost_benefit        #REDUCTION ON NFV
        
        
        #line rate vs cost
        self.capex_linecard_cost_map = {}
        
        context = ApplicationContext(GlobalConfiguration.config_xml)
        #populate line card cost
        self.capex_linecard_cost_map[ context.get_object("1GE")  ] = 1
        self.capex_linecard_cost_map[ context.get_object("10GE") ] = 2.5
        self.capex_linecard_cost_map[ context.get_object("100GE")] = 12
        
        '''===================OPEX============================='''
        self.opex_muxponder_cost  = 100
        self.opex_server_cost     = 50
        
        #COST REDUCTIONS - amended cost = traditional cost / cost reduction
        self.opex_cost_reduction_fact_SDN = sdn_cost_benefit    #REDUCTION ON SDN
        self.opex_cost_reduction_fact_NFV = nfv_cost_benefit    #REDUCTION ON NFV
        
        
        #line rate vs cost
        self.opex_linecard_cost_map = {}
        
        context = ApplicationContext(GlobalConfiguration.config_xml)
        #populate line card cost
        self.opex_linecard_cost_map[ context.get_object("1GE")  ] = 200
        self.opex_linecard_cost_map[ context.get_object("10GE") ] = 300
        self.opex_linecard_cost_map[ context.get_object("100GE")] = 500
        
        #explicit cost
        self.ip_router_chassis = 800
        self.ethernet_switch   = 300
        
        #================================================                        
        
    
    def calculate(self):
        
            capex = 0
            opex  = 0
        
            capex += self.calculate_linecard_cost(self.capex_linecard_cost_map,         \
                                                  self.capex_cost_reduction_fact_SDN,   \
                                                  self.capex_cost_reduction_fact_NFV    )
            
            opex  += self.calculate_linecard_cost(self.opex_linecard_cost_map,         \
                                                  self.opex_cost_reduction_fact_SDN,   \
                                                  self.opex_cost_reduction_fact_NFV    ) 
            
            capex += self.calculate_server_cost(self.capex_server_cost)
            opex  += self.calculate_server_cost(self.opex_server_cost )
            
            capex += self.calculate_muxponder_cost(self.capex_muxponder_cost)
            opex  += self.calculate_muxponder_cost(self.opex_muxponder_cost )
            
            opex  += self.calculate_explicit_router_switch_cost(self.ip_router_chassis, self.ethernet_switch)
            
            return capex, opex
        
            
    def calculate_linecard_cost(self, linecard_cost_map, cost_reduction_fact_SDN, cost_reduction_fact_NFV):
        noOfLinecardsAccountedFor = 0
        
        temp_cost = 0
        for band_width in linecard_cost_map:
            
            unit_cost = linecard_cost_map[band_width]
            
            linecards_of_same_band_width = [line_card for line_card in Network_Components.linecards if line_card.bandwidth == band_width]
            for linecard in linecards_of_same_band_width:
                if linecard.is_NFV and linecard.is_SDN:
                    raise ValueError("line card happens to be both NFV and SDN")
                elif linecard.is_SDN:
                    temp_cost += ( unit_cost / cost_reduction_fact_SDN )
                elif linecard.is_NFV:
                    temp_cost += ( unit_cost / cost_reduction_fact_NFV )
                else:
                    temp_cost += ( unit_cost )
                
                noOfLinecardsAccountedFor += 1

        if noOfLinecardsAccountedFor != len(  Network_Components.linecards  ):
            raise ValueError("Line cards for which cost is accounted {} doesnt equal actuals {}".format(noOfLinecardsAccountedFor, len(  Network_Components.linecards  )))

        return temp_cost
    
    def calculate_server_cost(self, server_cost):
        noOfSinks = len(  Network_Components.sinks  )
        noOfHosts = len(  Network_Components.hosts  )
        #cost is on server -  not on host and sink
        return float(((noOfSinks + noOfHosts) * server_cost)/2)
        
    def calculate_muxponder_cost(self, muxponder_cost):
        noOfMuxponders = len(  Network_Components.muxs  )
        return  noOfMuxponders * muxponder_cost
    
    def calculate_explicit_router_switch_cost(self, ip_router_cost, ethernet_switch_cost):
        temp_cost = 0
        for router_or_switch in Network_Components.routers:
            if not router_or_switch.is_ethernet_switch:
                temp_cost += ip_router_cost
            else:
                temp_cost += ethernet_switch_cost
        return temp_cost

        