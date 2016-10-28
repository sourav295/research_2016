import sys
import csv as csv
import matplotlib.pyplot as plt
import numpy as np


result_path = sys.argv[1]
jobs_path   = sys.argv[2]
plot_path   = sys.argv[3]

partial_analysis = False
job_id_filter = []#input 1,4,5, job id


if len(sys.argv) == 5:
    partial_analysis    = True
    job_id_filter       = (sys.argv[4]).split(',')
    
    
for job_id in job_id_filter:
    print job_id
#===========================================

'''
job_id
    **LIST**
    -- job description
    -- costmap hashmap with key = (cost_benefit_sdn, cost_benefit_nfv)
        -- capex
        -- opex
        -- sdn components
        -- nfv components

'''    
#===========JOB========================
#"Job,Desc,CapEx,OpEx,SDN,NFV"
index_job  = 0
#on the list
index_desc = 0
index_capex= 0
index_opex = 1
index_sdn  = 2
index_nfv  = 3


reader = csv.reader(open(jobs_path))
headers = reader.next()

job_results = {}
for row in reader:
    job_id = row[0]
    #job_results[job_id] = row[1:]
    
    if job_id not in job_results:
        #create new job entry
        job_results[job_id] = [row[1],{}] #job_desc and an empty hash map to store (cost benefit sdn,nfv)
    
    cost_ben_sdn = row[6]
    cost_ben_nfv = row[7]
    key         = (cost_ben_sdn, cost_ben_nfv)
    job         = job_results[job_id]
    costs_map   = job[1]
    
    costs_map[key] = row[2:6]
    
#===========================================

'''
job_id
    -- load
        -- drops
        -- genr
        -- delay
        -- etc
{
 job_id : 
    {
     load : [ , , ], 
     load : [ , , ]
    }
}
'''
#===========RESULT========================
#"Job,Load,Dropped,Generated,Average_delay"
index_job = 0
index_load= 1
#on the list
index_drop= 0
index_genr= 1
index_dely= 2
index_sdn_delay_detriment  = 3
index_nfv_delay_detriment  = 4

reader = csv.reader(open(result_path))
headers = reader.next()

job_map = {}
for row in reader:
    job_id = row[index_job ]
    load   = row[index_load]
    
    sdn_decriment = row[5]
    nfv_decriment = row[6]
    
    load_key = (load, sdn_decriment, nfv_decriment)
    
    if job_id not in job_map:
        #create new job entry
        job_map[job_id] = {}
    
    load_map            = job_map[job_id]
    load_map[load_key]  = row[2:5]#insert all other columns to map
#===========================================


'''
=====================================================================================
PLOT PACKETS DROPPED VS ARRIVAL RATE
=====================================================================================
'''
plt.clf()
job_descriptions = []


job_id_list = []
if partial_analysis:
    job_id_list = [job_id for job_id in job_map if job_id in job_id_filter] 
else:
    job_id_list = [job_id for job_id in job_map] 

#job_id_list = ['1','5','0','3','2','4']

all_coordinated = []

for job_id in job_id_filter:
    
    coordinates = []
    
    stats   = job_results[job_id]
    descrip = stats[index_desc]
    
    load_map = job_map[job_id]
 
    loadkeys        = load_map.keys()
    sdn_nfv_product = [(sdn_decriment, nfv_decriment) for _,sdn_decriment,nfv_decriment in loadkeys]
    
    dist_sdn_nfv_product  = list(set(sdn_nfv_product))

    
    
    for z1,z2 in dist_sdn_nfv_product:
        load, sdn_decriment, nfv_decriment = load_key
        #job_descriptions.append("{} z1:{} z2:{}".format(descrip,z1,z2))
        job_descriptions.append("{}".format(descrip))        
        #the tuples that match the values for sdn decriment and nfv decriment
        load_keys = [this_key for this_key in loadkeys if z1==this_key[1] and z2==this_key[2]]
        for load_key in load_keys:
            arrt_list = load_map[load_key]
            drp_count = float(arrt_list[index_drop])#/float(arrt_list[index_genr])
            load,_,_ = load_key
            coordinates.append( (load, drp_count) )
            
    coordinates.sort(key=lambda x: float(x[0]))
    all_coordinated.append(coordinates)
raveled_list = [item for sublist in all_coordinated for item in sublist]
max_drop    = max( raveled_list ,key=lambda item:item[1])[1]
         
for c in all_coordinated:  
    x_coord = []
    y_coord = []
    for x1,y1 in c:
        x_coord.append(x1)
        y_coord.append(float(y1)/max_drop)
    plt.plot(x_coord,y_coord)
        

lgd = plt.legend(job_descriptions, loc='center left', bbox_to_anchor=(1,0.5))    
#plt.legend(job_descriptions, loc='upper left')
plt.grid()
plt.ylabel('Packets dropped (Normalized)')
plt.xlabel('Host mean packet arrival rate (Thousands)')
plt.title('Network Performance against varied traffic characteristics')

plt.savefig(plot_path + "drop.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

plt.close()
plt.clf()

#-----------------------------------------------------------------------------

'''
=====================================================================================
MEAN END TO END DELAY VS ARRIVAL RATE
=====================================================================================
'''
plt.clf()
job_descriptions = []


job_id_list = []
if partial_analysis:
    job_id_list = [job_id for job_id in job_map if job_id in job_id_filter] 
else:
    job_id_list = [job_id for job_id in job_map] 


for job_id in job_id_list:
    
    xcoords = []
    ycoords = []
    coordinates = []
    
    stats   = job_results[job_id]
    descrip = stats[index_desc]
    
    load_map = job_map[job_id]
 
    loadkeys        = load_map.keys()
    sdn_nfv_product = [(sdn_decriment, nfv_decriment) for _,sdn_decriment,nfv_decriment in loadkeys]
    
    dist_sdn_nfv_product  = list(set(sdn_nfv_product))

    

    for z1,z2 in dist_sdn_nfv_product:
        load, sdn_decriment, nfv_decriment = load_key
        job_descriptions.append("{} z1:{} z2:{}".format(descrip,z1,z2))
        #job_descriptions.append("{}".format(descrip))
        #the tuples that match the values for sdn decriment and nfv decriment
        load_keys = [this_key for this_key in loadkeys if z1==this_key[1] and z2==this_key[2]]
        for load_key in load_keys:
            arrt_list = load_map[load_key]
            avg_delay = arrt_list[index_dely]
        
            coordinates.append( (load, avg_delay) )
            
        coordinates.sort(key=lambda x: float(x[0]))
        for x, y in coordinates:
            xcoords.append(x)
            ycoords.append(y)
        plt.plot(xcoords, ycoords)
    
lgd = plt.legend(job_descriptions, loc='center left', bbox_to_anchor=(1,0.5))    
#plt.legend(job_descriptions, loc='upper left')
plt.ylabel('Average End to End Delay')
plt.xlabel('Load')
plt.savefig(plot_path + "delay.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

plt.close()
plt.clf()

    
#-----------------------------------------------------------------------------


'''
=====================================================================================
PLOT CAPEX
=====================================================================================
'''

job_descriptions = []
for job_id in job_id_list:
    stats = job_results[job_id]
    
    costmap     = stats[1]
    description = stats[index_desc]
    job_descriptions.append(description)
    
    x_coords = []
    y_coords_capex = []
    
    unsorted_keys   = costmap.keys()
    x               = range(len(unsorted_keys))
    x_ticks         = []
    
    keys = sorted(unsorted_keys)
    
    
    for k in keys:
        #x_ticks.append("({})".format(','.join(k)))
        x_ticks.append(k[0])
        cost_stats = costmap[k]
        
        y_coords_capex.append(float(cost_stats[index_capex]))
    #plt.xticks(x, x_ticks, rotation='vertical')
    #plt.xticks(x, x_ticks)
    plt.plot(y_coords_capex, x)



plt.xlabel('Overall Network CAPEX realized in USD (Thousand)')
plt.ylabel('Perceived Cost Benefit for migrating a network element to SDN')

lgd = plt.legend(job_descriptions, loc='center left', bbox_to_anchor=(1,0.5))
plt.title("CAPEX")
plt.grid()
plt.savefig(plot_path + "capex.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

plt.close()
plt.clf()


'''
=====================================================================================
PLOT OPEX
=====================================================================================
'''

job_descriptions = []
for job_id in job_id_list:
    stats = job_results[job_id]
    
    costmap     = stats[1]
    description = stats[index_desc]
    job_descriptions.append(description)
    
    x_coords = []
    y_coords_opex  = []
    
    unsorted_keys   = costmap.keys()
    x               = range(len(unsorted_keys))
    x_ticks         = []
    
    keys = sorted(unsorted_keys)
    
    
    for k in keys:
        #x_ticks.append("({})".format(','.join(k)))
        cost_stats = costmap[k]
        
        y_coords_opex.append(float(cost_stats[index_opex]))
    #plt.xticks(x, x_ticks, rotation='vertical')
    y_coords_opex_thousands = map(lambda op: float(op)/1000, y_coords_opex)
    plt.plot(y_coords_opex_thousands, x)



plt.xlabel('Overall Network OPEX realized in USD(Thousand)/year')
plt.ylabel('Perceived Cost Benefit for migrating a network element to SDN')

lgd = plt.legend(job_descriptions, loc='center left', bbox_to_anchor=(1,0.5))
plt.title("OPEX")
plt.grid()
plt.savefig(plot_path + "opex.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

plt.close()
plt.clf()
from analyze_deep import Analyze
a = Analyze(plot_path, job_results, job_map) if not partial_analysis else Analyze(plot_path, job_results, job_map, ids=job_id_filter)
a.execute()

    