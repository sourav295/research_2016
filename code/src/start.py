from springpython.config import XMLConfig
from configure import GlobalConfiguration

import numpy
import matplotlib.pyplot as plt
import sys
import itertools


GlobalConfiguration.parse_options(sys.argv)
GlobalConfiguration.init()



a = GlobalConfiguration.arrival_rates
b = (GlobalConfiguration.MTU*numpy.logspace(GlobalConfiguration.buffer_factor_start,    \
                                            GlobalConfiguration.buffer_factor_end,      \
                                            GlobalConfiguration.buffer_factor_count)    \
    ).astype(int)


ab_prod = []

for element_a in a:
    for element_b in b:
        ab_prod.append((element_a, element_b))


for arrv_rate, buffer_fact in ab_prod:
    GlobalConfiguration.mean_arrv_rate = arrv_rate
    GlobalConfiguration.buffer_factor  = buffer_fact

    list_nOfPktdropped          = []
    list_nOfPktGenerated        = []
    list_mean_end_to_end_delay  = []



    delay_combinations = list(itertools.product(    GlobalConfiguration.delay_detriment_SDN_list    ,\
                                                    GlobalConfiguration.delay_detriment_NFV_list    ))
    cost_combinations  = list(itertools.product(    GlobalConfiguration.cost_benefit_SDN_list       ,\
                                                    GlobalConfiguration.cost_benefit_NFV_list       ))
                                            
    
    for delay_detriment_sdn, delay_detriment_nfv in delay_combinations:
        GlobalConfiguration.delay_fact_SDN = delay_detriment_sdn
        GlobalConfiguration.delay_fact_NFV = delay_detriment_nfv
        
        


        for run in range(GlobalConfiguration.nOfRuns):
            
            temp_nOfPktdropped          = 0
            temp_nOfPktGenerated        = 0
            temp_mean_end_to_end_delay  = 0    
            
            GlobalConfiguration.configure()
            try:
                x='dont run'
                GlobalConfiguration.simpyEnv.run(until= GlobalConfiguration.simulation_until)
            except KeyboardInterrupt:
                break
            
            temp_nOfPktdropped, temp_nOfPktGenerated, temp_mean_end_to_end_delay = GlobalConfiguration.getStats()
            print temp_nOfPktdropped
            list_nOfPktdropped.append(temp_nOfPktdropped)
            list_nOfPktGenerated.append(temp_nOfPktGenerated)
            list_mean_end_to_end_delay.append(temp_mean_end_to_end_delay)
            
        nOfPktdropped           = numpy.mean(list_nOfPktdropped)
        nOfPktGenerated         = numpy.mean(list_nOfPktGenerated)
        mean_end_to_end_delay   = numpy.mean(list_mean_end_to_end_delay)
        
        status = "Arrv Rate: {:10} | Pkt Dropped {:10} | Pkt Generated {:10} | End to end delay {:20}".format(arrv_rate, nOfPktdropped, nOfPktGenerated, mean_end_to_end_delay)

        #header produced by script files - "Job,Load,Dropped,Generated,Average_delay"
        content = "{},{},{},{},{},{},{}, {}".format(GlobalConfiguration.job_id, \
                                                arrv_rate, nOfPktdropped, \
                                                nOfPktGenerated,          \
                                                mean_end_to_end_delay,    \
                                                delay_detriment_sdn,    \
                                                delay_detriment_nfv,    \
                                                GlobalConfiguration.buffer_factor, \
                                                )

        print status
        
        f = open(GlobalConfiguration.result_log, 'a')
        f.write(content + '\n')
        f.close()    

f_job = open(GlobalConfiguration.job_stat_log, 'a')

from cost import CostMap

for cost_benefit_SDN, cost_benefit_NFV in cost_combinations:


    cost_map = CostMap(cost_benefit_SDN, cost_benefit_NFV)

    capex, opex = cost_map.calculate()
    print "Cost", capex , opex

    from routing import Network_Components 

    SDN = '|'.join( str(x) for x in [r for r in Network_Components.routers if r.is_SDN] )
    NFV = '|'.join( str(x) for x in [r for r in Network_Components.routers if r.is_NFV] )

    #header produced by script files - "Job,Desc,CapEx,OpEx,SDN,NFV"
    content = "{},{},{},{},{},{},{},{}".format(  GlobalConfiguration.job_id,            \
                                                 GlobalConfiguration.job_description,   \
                                                 capex,                                 \
                                                 opex,                                  \
                                                 SDN,                                   \
                                                 NFV,                                   \
                                                 cost_benefit_SDN,                      \
                                                 cost_benefit_NFV                       )

    f_job.write(content + '\n')

f_job.close()

import SimComponents
if GlobalConfiguration.to_log:
    SimComponents.Packet.log_to_file()
