#============================================================
# "Job Root Directory" path relative to the python script (entry point)
root_dir="../../jobs/template/"

#create / clear log file
> result.log
cat result.log
echo "Job,Load,Dropped,Generated,Average_delay,delay_detriment_SDN,delay_detriment_NFV" > result.log

final_results="${root_dir}result.log"
#---

#create / clear job_stats file
> job_stats.log
cat job_stats.log
echo "Job,Desc,CapEx,OpEx,SDN,NFV,cost_benefit_SDN,cost_benefit_NFV" > job_stats.log

job_stats="${root_dir}job_stats.log"

graph_path="${root_dir}"

> progress.log
cat progress.log
progress_log_path="${root_dir}progress.log"

#=============================================================

#path to python code entry point
cd ../../code/src/

declare -a arr=("${root_dir}baseline")
#_sdn_edge")


#declare -a arr=("${root_dir}baseline"
#		"${root_dir}baseline_sdn_agg"
#		"${root_dir}baseline_sdn_core"
#		"${root_dir}baseline_sdn_edge"
#		"${root_dir}streamline"
#		"${root_dir}streamline_sdn_core"
#		"${root_dir}streamline_sdn_edge"
#		"${root_dir}eeipc"
#		"${root_dir}eeipc_sdn_edge")

declare -i job_id=7

for job_path in "${arr[@]}"
do
   #python start.py "$job_id" "$job_path" "$final_results" "$job_stats"
   stdbuf -oL python start.py "$job_id" "$job_path" "$final_results" "$job_stats" #> "$progress_log_path"
   job_id=$((job_id+1))
done

#python analyze.py "$final_results" "$job_stats" "$graph_path"
