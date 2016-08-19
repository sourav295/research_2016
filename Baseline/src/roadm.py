import graph
from configure import GlobalConfiguration
import simpy

class Optical_Link(object):
    """
    Links 2 roadms - used by spring xml for initializing the architecture
    this has no significanace on the network simulation, but important for the set up
    """
    def __init__(self, frm, to):
        self.frm = frm
        self.to  = to
        
    def connect(self):
        self.frm.connect(self.to)
        

class Optical_Signal(object):
    """object to traverse over the optical fiber"""
    def __init__(self, pck, lambd):
        self.pck    = pck
        self.lambd  = lambd
    def get_lambda(self):
        return self.lambd
    def get_pck(self):
        return self.pck

class Lambda(object):
    def __init__(self, category):
        self.category = category
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.category == other.category)
    def __repr__(self):
        return "Lambd {}".format(self.category)
        
class Lambda_Factory(object):
    
    N_lambdas   = GlobalConfiguration.N_Channels
    all_lambdas = []
    
    for category in range(N_lambdas):
        all_lambdas.append(Lambda(category))
    
    @staticmethod
    def generate_lambda(unavailable_lambdas):
        allowed_lambdas = [l for l in Lambda_Factory.all_lambdas if not l in unavailable_lambdas]
        if allowed_lambdas:#not an empty list
            return allowed_lambdas[0]
        else:
            raise ValueError('Not enough lambdas provisioned by the system')

class Optical_Fibre(object):
    
    def __init__(self):
        self.out = None
        self.lambda_to_channel_map = {}
        self.delay = 0
        '''Remove Hardcode'''
        for l in Lambda_Factory.all_lambdas:
            self.lambda_to_channel_map[l] = Channel(GlobalConfiguration.simpyEnv, l, self.delay)
            
        
    def put(self, value):
        
        #simulate propagation over channel
        sig = value
        lmd = sig.get_lambda()
        chn = self.lambda_to_channel_map[lmd]
        #make sure channel leads to the "out" end of the fiber
        chn.out = self.out
        chn.put(sig)
        

class Channel(object):
    """This class represents the propagation on a particular lambda"""
    
    def __init__(self, env, lambd, delay):
        self.env    = env
        self.delay  = delay
        self.store  = simpy.Store(env)
        self.lambd  = lambd
        self.out    = None

    def latency(self, value):
        temp_time = self.env.now
        
        yield self.env.timeout(self.delay)
    
        propagation_delay = self.env.now - temp_time
        value.get_pck().log("<<Progation Delay over optical channel: {} lambda category: {}>>".format(propagation_delay, value.get_lambda().category))
        self.out.put(value)

    def put(self, value):
        self.env.process(self.latency(value))
        
        
class Roadm(object):
    
    
    def __init__(self,hostname, n_of_degrees, is_border = False):
        self.n_of_degrees = int(n_of_degrees)
        self.degrees = []
        self.LFIB = {}
        
        self.id = hostname
        self.is_border = is_border
        
        self.add_drop_module = Add_Drop_Module(self.LFIB)
        
        
        
        #init all degrees on this roadm
        for id in range(self.n_of_degrees):
            new_degree_id = "{}_{}".format(str(self.id), str(id))
            new_degree = Degree(new_degree_id, self.add_drop_module, is_border = self.is_border, LFIB = self.LFIB)
            
            self.degrees.append(new_degree)
            
            
    '''SETUP'''
    def connect(self, other_roadm):
        if other_roadm == self:
            return
        
        #roadm degrees not yet connected to anything
        avble_degree_on_self  = self.get_an_unconnected_degree()
        avble_degree_on_other = other_roadm.get_an_unconnected_degree()
        
        if ( not avble_degree_on_self ) or ( not avble_degree_on_other ):
            raise ValueError('Not enough degrees on RoadM on {} or {}'.format(self, other_roadm))
        else:
            of1 = Optical_Fibre()
            of2 = Optical_Fibre()
            
            #1 : connect self (out) to fiber and then fiber to other roadm port (in)
            avble_degree_on_self.out_port.out   = of1
            of1.out                             = avble_degree_on_other.in_port
            
            #2 : connect other roadm port (out) to fiber and then fiber self roadm port (in)
            avble_degree_on_other.out_port.out  = of2
            of2.out                             = avble_degree_on_self.in_port
            
            
    def get_an_unconnected_degree(self):
        #while connecting roadms, we want a degree which has not been connected yet
        available_degress = [ d for d in self.degrees if d.out_port.out == None]
        return available_degress[0] if available_degress else None
    
    def find_degree_to_reach_next_Roadm(self, other_roadm):
        #given another roadm find a plausable degree on my self to reach the target
        for self_degree in self.degrees:
            try:
                self_out_port   = self_degree.out_port
                connected_fiber = self_out_port.out
                nxt_port        = connected_fiber.out # port on other roadm
                
                other_degrees = [other_degree for other_degree in other_roadm.degrees if nxt_port == other_degree.in_port]
                if len(other_degrees) > 0:
                    #plausdible to reach the other_road via this self_degree / connected_fiber
                    return self_degree, other_degrees[0] #out degree to reach other roadm and in degree where the signal in the other roadm will be received
            except AttributeError:
                print "out doesnt exist"
        raise ValueError('No direct link to the next roadm')
    
    '''Distribute switching info'''
    def register_FEC_to_LFIB(self, fec, out_port, lambd):
        #FEC = destination roadM
        self.LFIB[fec] = (out_port, lambd)
        
    #used only by ingress roadm
    def distribute_labels(self, fec, path):
        out_degrees_in_path  = []
        
        this_out_next_in_map = {}
        for i in range(len(path)-1):#exclude the last path element (roadm)
            this_roadm = path[i]
            next_roadm = path[i+1]

            out_degree_this_roadm, in_degree_next_roadm  = this_roadm.find_degree_to_reach_next_Roadm( next_roadm )
            this_out_next_in_map [out_degree_this_roadm] = in_degree_next_roadm
            
            out_degrees_in_path.append(out_degree_this_roadm)
            
        
        #Find available resource
        unavailable_resources_on_path   = []#[uavail_res for uavail_res in degree.out_port.resources_reserved for degree in out_degrees_in_path]
        for out_degree in out_degrees_in_path:
            in_degree = this_out_next_in_map[out_degree]
            
            unavailable_resources_on_path.extend(  out_degree.out_port.resources_reserved  )
            unavailable_resources_on_path.extend(  in_degree.in_port.resources_reserved    )
        
        available_resource = Lambda_Factory.generate_lambda(unavailable_resources_on_path)
        
        #Reserve resource on each out_port on this path and create entry in wss
        for out_degree in out_degrees_in_path:
            out_degree.out_port.reserve_resource(available_resource)
            out_degree.wss.set_lambda_to_select(available_resource)
            
        for out_degree in out_degrees_in_path[:-1]:#Skip last element
            in_degree = this_out_next_in_map[out_degree]
            
            index_of_next_out_degree = out_degrees_in_path.index(out_degree) + 1
            next_out_degree          = out_degrees_in_path[index_of_next_out_degree]
            
            in_degree.in_port.reserve_resource(available_resource)
            in_degree.splitter.set_lambda_direction(available_resource, next_out_degree.out_port)
        
    
        #Register to LFIB on this roadm
        last_in_degree = this_out_next_in_map[  out_degrees_in_path[-1]  ]
        last_in_degree.splitter.set_lambda_direction(available_resource, fec.add_drop_module.Rx)
        
        target_out_port_on_self = out_degrees_in_path[0].out_port #out port on roadm this signal is supposed to go through
        self.register_FEC_to_LFIB(fec, target_out_port_on_self, available_resource)
        
    @staticmethod
    def get_border_roadms(all_roadms):
        border_roadms = [roadm for roadm in all_roadms if roadm.is_border == True]
        return border_roadms if border_roadms else None
    @staticmethod
    def expel_inner_roadms_from_path(explicit_path):
        #if first condition is false, then only it evals the second condition assuming it is a roadm (short circuiting)
        return [net_comp for net_comp in explicit_path if not isinstance(net_comp,Roadm) or net_comp.is_border == True]
        
    def __repr__(self):
        return "{}".format(self.id)
        #construct map {incoming port, incoming lambda} -> {outgoing port, outport lambda}
        
class Degree(object):
    
    def __init__(self, id, central_add_drop_module, is_border = False, LFIB = None):
        self.id = id
        self.LFIB = LFIB
        self.in_port    = Roadm_Port("{}_in".format(self.id), LFIB = self.LFIB)
        self.out_port   = Roadm_Port("{}_out".format(self.id))
        
        self.splitter = Splitter()
        self.wss = WSS()
            
        self.in_port.out = self.splitter
        self.wss.out     = self.out_port
        
        self.central_add_drop_module = central_add_drop_module 
        
    def __repr__(self):
        return "(Degree){}".format(self.id)

'''==================ADD DROP MODULE======================================'''

class Add_Drop_Module(object):
    
    def __init__(self, LFIB):
        out = []
        self.Tx = Add_Side(LFIB)
        self.Rx = Drop_Side(LFIB)
        
class Add_Side(object):
    
    def __init__(self, LFIB):
        self.LFIB = LFIB
        self.out  = None
        
    def put(self, value):
        pck = value
        fec = pck.next_hop()

        pck.log("--~~--")
        pck.log("Packet arrived at Optical Network Ingress: {}".format(self))
        out_port, lambd = self.LFIB[fec]#query LFIB
        pck.log("Lambda Category Assigned: {} For FEC: {}".format(lambd.category, fec))
        pck.log("--~~--")

        pck.increment_explicit_path_pointer()
        out_port.put(  Optical_Signal(pck, lambd)  )

class Drop_Side(object):
    
    def __init__(self, LFIB):
        self.LFIB = LFIB
        self.out  = None
        
    def put(self, value):
        sig = value
        pck = sig.get_pck()
        pck.increment_explicit_path_pointer()
        
        pck.log("--~~--")
        pck.log("Packet arrived at Optical Network Egress: {}, Lambda removed".format(self))
        pck.log("--~~--")
        
        self.out.put(pck)
'''========================================================================================='''
class Roadm_Port(object):
     
    def __init__(self, id, LFIB = None):
        #self.env = env
        self.id = id
        self.out = None
        self.LFIB = LFIB #LFIB[fec] --to--> (out_port, lambd) MAP
        
        self.resources_reserved = []
        
    def put(self, value):
        self.out.put(value)
            
    
    def reserve_resource(self, resource):
        #just to keep track
        if not resource in self.resources_reserved:
            self.resources_reserved.append(resource)
            return True
        else:
            return False
    
    def get_reserved_resources(self):
        return self.resources_reserved
    
    
    def __repr__(self):
        return "(Roadm_port){}".format(self.id)    
        
        
class WSS(object): #wavelength selective switch
    
    def __init__(self):
        self.out = None
        self.lambda_to_select = []
        

    def put(self, value):
        if value.get_lambda() in self.lambda_to_select:
            self.out.put(value)
        else:
            print "WSS dropped packet"
    
    def set_lambda_to_select(self, resource):
        #just to keep track
        if not resource in self.lambda_to_select:
            self.lambda_to_select.append(resource)
            return True
        else:
            return False
    
    def get_lambda_to_select(self):
        return self.lambda_to_select    
        
class Splitter(object):
    
    def __init__(self):
        self.lambda_direction_map = {}
        
    def set_lambda_direction(self, lambd, next_out_degree):
        self.lambda_direction_map[lambd] = next_out_degree
        
    def put(self, value):
        self.lambda_direction_map[  value.get_lambda()  ].put(value)
        

