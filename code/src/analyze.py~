import sys
import csv as csv
import matplotlib.pyplot as plt



result_path = sys.argv[1]
jobs_path   = sys.argv[2]
plot_path   = sys.argv[3]

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






#plot observations
plt.clf()
job_descriptions = []
for job_id in job_map:
    
    xcoords = []
    ycoords = []
    coordinates = []
    
    stats = job_results[job_id]
    
    job_descriptions.append("{} - Cost CapEx {} OpEx {}".format(stats[index_desc], stats[index_capex], stats[index_opex]))
    load_map = job_map[job_id]
 
    for load in load_map:
        arrt_list = load_map[load]
        drp_count = arrt_list[index_drop]
        
        coordinates.append( (load, drp_count) )
        
    coordinates.sort(key=lambda x: x[0])
    for x, y in coordinates:
        xcoords.append(x)
        ycoords.append(y)
    plt.plot(xcoords, ycoords)
plt.legend(job_descriptions, loc='upper left')
plt.savefig(plot_path)
plt.show()
    
    