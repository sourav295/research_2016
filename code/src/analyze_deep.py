import matplotlib.pyplot as plt
import numpy as np

class Analyze(object):
    def __init__(self, plot_path, job_results, job_map, ids=None):
        self.plot_path      = plot_path
        self.job_results    = job_results
        self.job_map        = job_map
        self.job_filter     = ids
        
        #===========JOB========================
        #"Job,Desc,CapEx,OpEx,SDN,NFV"
        self.index_job  = 0
        #on the list
        self.index_desc = 0
        self.index_capex= 0
        self.index_opex = 1
        self.index_sdn  = 2
        self.index_nfv  = 3
        #===========RESULT========================
        #"Job,Load,Dropped,Generated,Average_delay"
        self.index_load= 1
        #on the list
        self.index_drop= 0
        self.index_genr= 1
        self.index_dely= 2
        self.index_sdn_delay_detriment  = 3
        self.index_nfv_delay_detriment  = 4


    def execute(self):
        #self.plot_for_x_1()
        #self.plot_cap_against_capex()
        #self.plot_cap_against_opex()
    
        self.plot_histogram_of_capacity()
        self.plot_delay()
        
        x=5
        #self.plot_network_load()
        
    
    def plot_cap_against_capex(self):
        job_capacity_map = self.find_thresholdmap()
        job_descriptions = []
        x= []
        y= []
        for job_id in job_capacity_map:
            stats = self.job_results[job_id]
            
            costmap     = stats[1]
            description = stats[self.index_desc]
            job_descriptions.append(description)
            
            unsorted_keys = costmap.keys()
            
            keys = sorted(unsorted_keys)
            
            for k in keys:
                cost_stats = costmap[k]
                capex = float(cost_stats[self.index_capex])
                x.append(capex)
                y.append(job_capacity_map[job_id])
        plt.scatter(x, y)
        for i, txt in enumerate(job_descriptions):
            if i==3:
               plt.annotate(txt, (x[i],y[i]),xytext=(x[i],float(y[i])+.1),rotation=20)
            else:
                plt.annotate(txt, (x[i],y[i]), rotation=-20)
             
        self.commit_plot("{}capex_vs_cap.png".format(self.plot_path), "", 'Capital Expenditure', 'Network Capacity', 'Network Capacity against Edge Architecture CAPEX')
        
    def plot_cap_against_opex(self):
        job_capacity_map = self.find_thresholdmap()
        job_descriptions = []
        x= []
        y= []
        for job_id in job_capacity_map:
            stats = self.job_results[job_id]
            
            costmap     = stats[1]
            description = stats[self.index_desc]
            job_descriptions.append(description)
            
            unsorted_keys = costmap.keys()
            
            keys = sorted(unsorted_keys)
            
            for k in keys:
                cost_stats = costmap[k]
                opex = float(cost_stats[self.index_opex])
                x.append(opex)
                y.append(job_capacity_map[job_id])
        plt.scatter(x, y)
        for i, txt in enumerate(job_descriptions):
            plt.annotate(txt, (x[i],y[i]), rotation=20)
        self.commit_plot("{}opex_vs_cap.png".format(self.plot_path), "", 'Operational Expenditure / year', 'Network Capacity', 'Network Capacity against Edge Architecture OPEX')
    
    def commit_plot(self, plot_path, legend_list, x_label, y_label, title):
        lgd = plt.legend(legend_list, loc='center left', bbox_to_anchor=(1,0.5))    
        plt.ylabel(y_label)
        plt.xlabel(x_label)

        plt.title(title)
        plt.grid()

        plt.savefig(plot_path, bbox_extra_artists=(lgd,), bbox_inches='tight')

        plt.close()
        plt.clf()
        
    def plot_for_x_1(self):

        job_descriptions = []
        
        for job_id in self.job_map:
            
            xcoords = []
            ycoords = []
            coordinates = []
            
            stats   = self.job_results[job_id]
            descrip = stats[self.index_desc]
            
            load_map = self.job_map[job_id]
         
            loadkeys        = load_map.keys()
            sdn_nfv_product = [(sdn_decriment, nfv_decriment) for _,sdn_decriment,nfv_decriment in loadkeys]
            
            dist_sdn_nfv_product  = list(set(sdn_nfv_product))
            
            #filtering
            filtrd_dist_sdn_nfv_product  = [sdn_nfv for sdn_nfv in dist_sdn_nfv_product if int(float(sdn_nfv[0]))==1]
            
            for z1,z2 in filtrd_dist_sdn_nfv_product  :
                job_descriptions.append("{}".format(descrip,z1,z2))
                        
                #the tuples that match the values for sdn decriment and nfv decriment
                load_keys = [this_key for this_key in loadkeys if z1==this_key[1] and z2==this_key[2]]
                for load_key in load_keys:
                    arrt_list = load_map[load_key]
                    drp_count = arrt_list[self.index_drop]
                    load,_,_ = load_key
                    coordinates.append( (load, drp_count) )
                    
                coordinates.sort(key=lambda x: float(x[0]))
                for x, y in coordinates:
                    xcoords.append(x)
                    ycoords.append(y)
                plt.plot(xcoords, ycoords)
        self.commit_plot("{}test.png".format(self.plot_path), job_descriptions, 'Load', 'Drop', 'Title')
        

    def find_thresholdmap(self):

        job_descriptions = []
        threhold = 500#310
        
        job_to_capacity = {}
        
        for job_id in self.job_map:
            coordinates = []
            load_map = self.job_map[job_id]
            loadkeys        = load_map.keys()
            sdn_nfv_product = [(sdn_decriment, nfv_decriment) for _,sdn_decriment,nfv_decriment in loadkeys]
            
            dist_sdn_nfv_product  = list(set(sdn_nfv_product))
            
            #filtering
            filtrd_dist_sdn_nfv_product  = [sdn_nfv for sdn_nfv in dist_sdn_nfv_product if int(float(sdn_nfv[0]))==1]
            
            for z1,z2 in filtrd_dist_sdn_nfv_product  :
                #the tuples that match the values for sdn decriment and nfv decriment
                load_keys = [this_key for this_key in loadkeys if z1==this_key[1] and z2==this_key[2]]
                for load_key in load_keys:
                    arrt_list = load_map[load_key]
                    drp_count = arrt_list[self.index_drop]
                    load,_,_ = load_key
                    coordinates.append( (load, drp_count) )
                #sort on rate
                coordinates.sort(key=lambda x: float(x[0]))
                for coord in coordinates:
                    if float(coord[1]) > float(threhold):
                        print coord[1]
                        job_to_capacity[job_id] = float(coord[0])
                        break
        return job_to_capacity
    
    
    def plot_histogram_of_capacity(self):
        job_capacity_map = self.find_thresholdmap()
        job_descriptions = []
        y= []
        opex  = []
        capex = [] 
        
        job_keys = job_capacity_map.keys()
        #job_keys = ['0','3','1','2','4','6','5']#,'7','8']
        job_keys = self.job_filter
        
        for job_id in job_keys:
            stats = self.job_results[job_id]
            
            costmap     = stats[1]
            description = stats[self.index_desc]
            job_descriptions.append(description)
            
            unsorted_keys = costmap.keys()
            
            keys = sorted(unsorted_keys)
            
            for k in keys:
                cost_stats = costmap[k]
                y.append(job_capacity_map[job_id])
                opex.append(float(cost_stats[self.index_opex]))
                capex.append(float(cost_stats[self.index_capex]))
                
        N = len(y)
        
        norm_y = [float(i)/max(y) for i in y]
        norm_capex = [float(i)/max(capex) for i in capex]
        norm_opex  = [float(i)/max(opex)  for i in opex ]
        
        ind     = np.arange(N)  # the x locations for the groups
        width   = 0.5       # the width of the bars
        plot_x  = ind#[(x_1+(width/2)) for x_1 in ind]
        
        '''CAPEX'''
        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, norm_y, width, color='r')

        
        # add some text for labels, title and axes ticks
        ax.set_ylabel('Network Capacity (Normalized)')
        ax.set_title('Network Capacity by model')
        ax.set_xticks(ind)
        plt.xticks(rotation=15)
        ax.set_xticklabels(job_descriptions)
        plt.grid()
        
        
        
        plt.savefig("{}capacity.png".format(self.plot_path))
        plt.close()
        plt.clf()
        
        #fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
        fig, ax = plt.subplots()
        plt.plot(plot_x, norm_capex, 'k--', label='CAPEX')
        ax.set_xticks(ind)
        plt.ylabel('Cost (Normalized)')
        plt.xticks(rotation=15)
        plt.grid()
        ax.set_xticklabels(job_descriptions)
        lgd = plt.legend(loc='center left', bbox_to_anchor=(1,0.5))
        plt.savefig("{}capacity_capex.png".format(self.plot_path), bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close()
        plt.clf()
        
        fig, ax = plt.subplots()
        plt.plot(plot_x, norm_opex , 'k--' , label='OPEX')
        plt.ylabel('Cost (Normalized)')
        ax.set_xticks(ind)
        plt.grid()
        plt.xticks(rotation=15)
        ax.set_xticklabels(job_descriptions)
        lgd = plt.legend(loc='center left', bbox_to_anchor=(1,0.5))
        plt.savefig("{}capacity_opex.png".format(self.plot_path), bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close()
        plt.clf()
    def plot_network_load(self):
        x = []
        y = []
        load_map = self.job_map['0']
        
        keys = load_map.keys()
        keys.sort(key=lambda tup: float(tup[0]))
        #keys = sorted(load_map.keys())
        print keys
        for load_key in keys:
            arrival_rate,_,_ = load_key
            load_list = load_map[load_key]
            pkt_generated = load_list[self.index_genr]
            print pkt_generated
            x.append(arrival_rate)
            y.append(pkt_generated)
        plt.plot(x,y)
        self.commit_plot("{}load.png".format(self.plot_path), "", 'Server Mean Packet Arrival Rate', 'Total packets inundated to the network', 'Traffic characteristics')
        
    
    def plot_delay(self):

        job_descriptions = []
        job_to_capacity = {}
        
        job_keys = self.job_map.keys()
        job_keys = self.job_filter
        
        all_coordinated = []
        
        for job_id in job_keys:
            coordinates = []
            load_map = self.job_map[job_id]
            loadkeys        = load_map.keys()
            sdn_nfv_product = [(sdn_decriment, nfv_decriment) for _,sdn_decriment,nfv_decriment in loadkeys]
            
            stats = self.job_results[job_id]
            
            description = stats[self.index_desc]
            job_descriptions.append(description)
            
            dist_sdn_nfv_product  = list(set(sdn_nfv_product))
            
            #filtering
            filtrd_dist_sdn_nfv_product  = [sdn_nfv for sdn_nfv in dist_sdn_nfv_product if int(float(sdn_nfv[0]))==1]
            
            for z1,z2 in filtrd_dist_sdn_nfv_product  :
                #the tuples that match the values for sdn decriment and nfv decriment
                load_keys = [this_key for this_key in loadkeys if z1==this_key[1] and z2==this_key[2]]
                for load_key in load_keys:
                    arrt_list = load_map[load_key]
                    delay     = float(arrt_list[self.index_dely])#/float(arrt_list[self.index_genr])
                    load,_,_ = load_key
                    coordinates.append( (load, delay) )
                #sort on rate
            coordinates.sort(key=lambda x: float(x[0]))
            all_coordinated.append(coordinates)
        raveled_list = [item for sublist in all_coordinated for item in sublist]
        max_delay    = max( raveled_list ,key=lambda item:item[1])[1]
         
        for c in all_coordinated:  
            x_coord = []
            y_coord = []
            for x1,y1 in c:
                x_coord.append(x1)
                y_coord.append(float(y1))#/max_delay)
            plt.plot(x_coord,y_coord)
        plt.grid()
        self.commit_plot("{}latency.png".format(self.plot_path), job_descriptions,'Host mean packet arrival rate (Thousands)','Average Latency (millisecond)', 'Latency Impact of SDN Penetration')
            