from springpython.config import XMLConfig
from configure import GlobalConfiguration

import numpy
import matplotlib.pyplot as plt
import sys


GlobalConfiguration.parse_options(sys.argv)

if GlobalConfiguration.test_run:
    GlobalConfiguration.end_rate        = GlobalConfiguration.start_rate + 1
    GlobalConfiguration.rate_increments = 2
    GlobalConfiguration.to_log          = True
else:
    GlobalConfiguration.to_log          = False

f = open(GlobalConfiguration.result_log, 'a')

for arrv_rate in numpy.arange(GlobalConfiguration.start_rate, GlobalConfiguration.end_rate, GlobalConfiguration.rate_increments):#start, end, interval
    GlobalConfiguration.mean_arrv_rate = arrv_rate

    list_nOfPktdropped          = []
    list_nOfPktGenerated        = []
    list_mean_end_to_end_delay  = []

    for run in range(GlobalConfiguration.nOfRuns):
        
        temp_nOfPktdropped          = 0
        temp_nOfPktGenerated        = 0
        temp_mean_end_to_end_delay  = 0    
        
        GlobalConfiguration.configure()
        try:
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
    content = "{},{},{},{},{}".format(GlobalConfiguration.job_id, \
                                        arrv_rate, nOfPktdropped, \
                                        nOfPktGenerated,          \
                                        mean_end_to_end_delay     \
                                     )

    print status
    f.write(content + '\n')
    
f.close()    

f_job = open(GlobalConfiguration.job_stat_log, 'a')

from cost import CostMap
cost_map = CostMap()

capex, opex = cost_map.calculate()
print "Cost", capex , opex

from routing import Network_Components 

SDN = '|'.join( str(x) for x in [r for r in Network_Components.routers if r.is_SDN] )
NFV = '|'.join( str(x) for x in [r for r in Network_Components.routers if r.is_NFV] )

#header produced by script files - "Job,Desc,CapEx,OpEx,SDN,NFV"
content = "{},{},{},{},{},{}".format(GlobalConfiguration.job_id,            \
                                     GlobalConfiguration.job_description,   \
                                     capex,                                 \
                                     opex,                                  \
                                     SDN,                                   \
                                     NFV                                    )

f_job.write(content + '\n')
f_job.close()

import SimComponents
if GlobalConfiguration.to_log:
    SimComponents.Packet.log_to_file()
