from itertools import cycle

class queue(object):
    
    def __init__(self, name):
        self.list = []
        self.x = None
        self.name = name
        
    def put(self, value):
        print "received msg: ", self.name, value
        self.list.append(value)
        self.x.wait.succeed()
        self.x.wait = self.x.env.event()
        

class port(object):
    
    def __init__(self, env):
        self.env = env
        self.all_queues = []
        self.wait = env.event()
        self.action = env.process(self.run())
        
    
    def run(self):
        print self.all_queues
        nq = len(self.all_queues)
        failed_attmpts= 0
        for q_index in cycle(range(nq)):
            q_selected = self.all_queues[q_index]
            msq_retreived = False
            
            if q_selected.list:
                msq_retreived = True
                msg = q_selected.list[0]
                q_selected.list.remove(msg)
                print "msg selected", self.env.now
            else:
                failed_attmpts += 1
                print "failed attempt"
                
            if msq_retreived:
                print "transmitting msg"
                failed_attmpts = 0
                yield self.env.timeout(40)
                print "transmission over"
            elif failed_attmpts == nq:
                print "waiting"
                yield self.wait
                print "wait over"
                
                