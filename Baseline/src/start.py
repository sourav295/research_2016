from springpython.config import XMLConfig
from configure import GlobalConfiguration

import numpy
import matplotlib.pyplot as plt

x_coord = []
y_coord = []

if GlobalConfiguration.test_run:
    GlobalConfiguration.end_rate        = GlobalConfiguration.start_rate + 1
    GlobalConfiguration.rate_increments = 2
    GlobalConfiguration.to_log          = True
else:
    GlobalConfiguration.to_log          = False


for arrv_rate in numpy.arange(GlobalConfiguration.start_rate, GlobalConfiguration.end_rate, GlobalConfiguration.rate_increments):#start, end, interval
    GlobalConfiguration.mean_arrv_rate = arrv_rate
    
    GlobalConfiguration.configure()
    GlobalConfiguration.simpyEnv.run(until= GlobalConfiguration.simulation_until)
    
    nOfPktdropped, nOfPktGenerated = GlobalConfiguration.getStats()
    
    print "Done for arrival rate: ", arrv_rate, nOfPktdropped, nOfPktGenerated
    
    x_coord.append(arrv_rate)
    y_coord.append(nOfPktdropped)
    
    

import SimComponents
if GlobalConfiguration.to_log:
    SimComponents.Packet.log_to_file()

plt.clf()
plt.plot(x_coord, y_coord)
plt.show()
