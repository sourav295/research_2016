import sys
import csv as csv
import matplotlib.pyplot as plt
import numpy as np

def plot_cost_graph(cost_tuple, N, file_name, desc):
    
    width = 0.35       # the width of the bars
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, cost_tuple, width, color='r')
    
    # add some text for labels, title and axes ticks
    ax.set_ylabel('Cost')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(x_labels)

    ax.legend(desc, loc='upper center', bbox_to_anchor=(1,0.5))
    fig.autofmt_xdate()

    plt.savefig(plot_path + file_name)


"""
******************************************************************************************
******************************************************************************************
"""



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
    
#===========JOB========================
#"Job,Desc,CapEx,OpEx,SDN,NFV"
index_job  = 0
#on the list
index_desc = 0
index_capex= 1
index_opex = 2
index_sdn  = 3
index_nfv  = 4


reader = csv.reader(open(jobs_path))
headers = reader.next()

job_results = {}
for row in reader:
    job_id = row[index_job]
    job_results[job_id] = row[1:]
    
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


reader = csv.reader(open(result_path))
headers = reader.next()

job_map = {}
for row in reader:
    job_id = row[index_job ]
    load   = row[index_load]
    
    if job_id not in job_map:
        #create new job entry
        job_map[job_id] = {}
    
    load_map        = job_map[job_id]
    load_map[load]  = row[2:]#insert all other columns to map
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


for job_id in job_id_list:
    
    xcoords = []
    ycoords = []
    coordinates = []
    
    stats = job_results[job_id]
    
    job_descriptions.append("{}".format(stats[index_desc]))
    load_map = job_map[job_id]
 
    for load in load_map:
        arrt_list = load_map[load]
        drp_count = arrt_list[index_drop]
        
        coordinates.append( (load, drp_count) )
        
    coordinates.sort(key=lambda x: float(x[0]))
    for x, y in coordinates:
        xcoords.append(x)
        ycoords.append(y)
    plt.plot(xcoords, ycoords)
plt.legend(job_descriptions, loc='upper left')
#plt.legend(job_descriptions, loc='upper center', bbox_to_anchor=(1,0.5))
plt.ylabel('Packets dropped')
plt.xlabel('Load')

plt.savefig(plot_path + "drop.png")

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
    
    stats = job_results[job_id]
    
    job_descriptions.append("{}".format(stats[index_desc]))
    load_map = job_map[job_id]
 
    for load in load_map:
        arrt_list = load_map[load]
        avg_delay = arrt_list[index_dely]
        
        coordinates.append( (load, avg_delay) )
        
    coordinates.sort(key=lambda x: float(x[0]))
    for x, y in coordinates:
        xcoords.append(x)
        ycoords.append(y)
    plt.plot(xcoords, ycoords)
plt.legend(job_descriptions, loc='upper left')
plt.ylabel('Average End to End Delay')
plt.xlabel('Load')
plt.savefig(plot_path + "delay.png")

plt.close()
plt.clf()

    
#-----------------------------------------------------------------------------


'''
=====================================================================================
PLOT CAPEX VS OPEX
=====================================================================================
'''

capex_bar = []
opex_bar  = []
x_labels  = []
for job_id in job_id_list:
    stats = job_results[job_id]
    
    capex_bar.append(float(stats[index_capex]))
    opex_bar.append(float(stats[index_opex]))
    
    x_labels.append(stats[index_desc])



capex_bar = tuple(capex_bar)
opex_bar  = tuple(opex_bar)
x_labels  = tuple(x_labels)

N = len(opex_bar)

ind = np.arange(N)  # the x locations for the groups

plot_cost_graph(capex_bar, N, "capex.png", ['CapEx'])
plot_cost_graph(opex_bar , N, "opex.png" , ['OpEx'])

    