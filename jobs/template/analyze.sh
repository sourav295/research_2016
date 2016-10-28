#============================================================
#create / clear log file

final_results="../../jobs/template/result.log"

#---

#create / clear job_stats file

job_stats="../../jobs/template/job_stats.log"

graph_path="../../jobs/template/"

#=============================================================

#path to python code entry point
cd ../../code/src/

job_list="1,2,3"


python analyze.py "$final_results" "$job_stats" "$graph_path" "$job_list"
