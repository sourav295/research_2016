import simpy
from SimComponents import PacketGenerator, PacketSink
import ocx

from random import expovariate


def constArrival(): # Constant arrival distribution for generator 1
    return 10

def constArrival2(): # Constant arrival distribution for generator 2
    return 15

def distSize(): # Random packet size distribution
    return expovariate(0.01)


env = simpy.Environment()  # Create the SimPy environment
# Create the packet generators and sink
ps = PacketSink(env, debug=True)  # debugging enable for simple output
pg = PacketGenerator(env, "EE283", constArrival, distSize)
pg2 = PacketGenerator(env, "SJSU", constArrival2, distSize)
# Wire packet generators and sink together
q1 = ocx.queue("q1")
q2 = ocx.queue("q2")


pg.out  = q1
pg2.out = q2

p = ocx.port(env)
p.all_queues = [q1,q2]
q1.x = p
q2.x = p
# Run it
env.run(until=200)