#============================================================
#create / clear log file
> result.log
cat result.log
echo "Job,Load,Dropped,Generated,Average_delay" > result.log

final_results="../../jobs/template/result.log"

#---

#create / clear job_stats file
> job_stats.log
cat job_stats.log
echo "Job,Desc,CapEx,OpEx,SDN,NFV" > job_stats.log

job_stats="../../jobs/template/job_stats.log"

graph_path="../../jobs/template/plot.png"

#=============================================================

#path to python code entry point
cd ../../code/src/




declare -a arr=("../../jobs/template/baseline_sdn_agg"
		"../../jobs/template/baseline"
		"../../jobs/template/baseline_sdn_core"
		"../../jobs/template/baseline_sdn_edge"
		"../../jobs/template/streamline"
		"../../jobs/template/streamline_sdn_core"
		"../../jobs/template/streamline_sdn_edge")

declare -i job_id=0

for job_path in "${arr[@]}"
do
   python start.py "$job_id" "$job_path" "$final_results" "$job_stats"
   job_id=$((job_id+1))
done

python analyze.py "$final_results" "$job_stats" "$graph_path"
