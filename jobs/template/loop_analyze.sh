#============================================================
#create / clear log file

final_results="../../jobs/template/result.log"

#---

#create / clear job_stats file

job_stats="../../jobs/template/job_stats.log"

graph_path="../../jobs/template/"

#=============================================================

#path to python code entry point



declare -a arr=("0,4"		#Baseline vs Streamline Traditional
		"1,3,2"		#Baseline
		"4,5,6"		#Streamline
		"2,5"		#Core Comparison
		"3,6"		#Edge Comparison
		"1,5"		#Baseline AGG vs Streamline Core
		"1,2,5"		#Baseline AGG + Core vs Streamline Core
		"0,4,7"		#Baseline Streamline EEIPC - Traditional Hardware
		"3,6,8"		#Edge comparison of all topologies
		"7,8"		#EEIPC
		) 

for job_list in "${arr[@]}"
do

   cd ../../code/src/
   stdbuf -oL python analyze.py "$final_results" "$job_stats" "$graph_path" "$job_list"
   cd ../../jobs/template/
   
   rm -rf "./new_reports/${job_list}"
   mkdir "./new_reports/${job_list}"

   cp capacity_capex.png capacity_opex.png capacity.png latency.png drop.png "./new_reports/${job_list}/"
   


done

