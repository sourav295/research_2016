from springpython.config import XMLConfig
from configure import GlobalConfiguration

import numpy
import matplotlib.pyplot as plt

x_coord = []
y_coord = []

print GlobalConfiguration.achitecture

if GlobalConfiguration.test_run:
    GlobalConfiguration.end_rate        = GlobalConfiguration.start_rate + 1
    GlobalConfiguration.rate_increments = 2
    GlobalConfiguration.to_log          = True
else:
    GlobalConfiguration.to_log          = False

f = open(GlobalConfiguration.final_result_log_folder + 'final_result.txt', 'w')

for arrv_rate in numpy.arange(GlobalConfiguration.start_rate, GlobalConfiguration.end_rate, GlobalConfiguration.rate_increments):#start, end, interval
    GlobalConfiguration.mean_arrv_rate = arrv_rate

    GlobalConfiguration.configure()
    try:
        GlobalConfiguration.simpyEnv.run(until= GlobalConfiguration.simulation_until)
    except KeyboardInterrupt:
        break
    
    nOfPktdropped, nOfPktGenerated, mean_end_to_end_delay = GlobalConfiguration.getStats()
    
    status = "Arrv Rate: {:10} | Pkt Dropped {:10} | Pkt Generated {:10} | End to end delay {:20}".format(arrv_rate, nOfPktdropped, nOfPktGenerated, mean_end_to_end_delay)

    print status
    f.write(status + '\n')
    
    
    x_coord.append(arrv_rate)
    y_coord.append(nOfPktdropped)
    
    

import SimComponents
if GlobalConfiguration.to_log:
    SimComponents.Packet.log_to_file()

#============= PLOT pkt dropped vs arrv ============
plt.clf()
plt.plot(x_coord, y_coord)
plt.savefig(  GlobalConfiguration.final_result_log_folder  + "pkts_dropped vs arrv rate.png")
#===================================================


#============= COST ================================    
from cost import CostMap
cost_map = CostMap()

cost_str = "Cost {}".format( cost_map.calculate() )
print cost_str
f.write(cost_str + '\n')
#===================================================

#============ SDN/NFV ==============================
from routing import Network_Components

SDN = [r for r in Network_Components.routers if r.is_SDN]
NFV = [r for r in Network_Components.routers if r.is_NFV]
f.write("SDN - {}".format(SDN) + '\n')
f.write("NFV - {}".format(NFV) + '\n')
#===================================================


f.close()


