import numpy

print  (1500*numpy.logspace(1,3,5)).astype(int)


'''
import random
import functools

f = functools.partial(random.expovariate, 1.0/576.0)

x = []
y = []
for i in range(300):
    
    
    MTU = 1
    
    rand = MTU + 1
    while rand > MTU:
        rand = f()
    x.append(i)
    y.append(rand)
    
    
import matplotlib.pyplot as plt
plt.plot(x,y)

plt.show()
'''