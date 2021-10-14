#! /bin/sh
set -e
if [ ! -d "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs" ]; then
  mkdir /home/jovyan/opensarlab-notebook_testing/notebook_testing_logs
  mkdir /home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/old_logs
fi
if [ ! -d "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev" ]; then
  mkdir /home/jovyan/opensarlab-notebook_testing/notebook_testing_dev
fi
if [ ! -d "/home/jovyan/opensarlab-notebook_testing/reports" ]; then
  mkdir /home/jovyan/opensarlab-notebook_testing/reports
fi
# Remove old logs
for f in /home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/old_logs/*.log; do
    rm $f
done
## Re-install and activate rtc_analysis conda environment
conda init bash
source ~/.bashrc
conda env create -f '/home/jovyan/conda_environments/Environment_Configs/rtc_analysis_env.yml' --prefix "/home/jovyan/.local/envs/rtc_analysis" --force
conda run -n rtc_analysis kernda --display-name rtc_analysis -o /home/jovyan/.local/envs/rtc_analysis/share/jupyter/kernels/python3/kernel.json
conda activate /home/jovyan/.local/envs/rtc_analysis
## Run tests on notebooks that use rtc_analysis environment
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex1.py
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex2.py
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex3.py
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex4A.py
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex4B.py
python /home/jovyan/opensarlab-notebook_testing/Test_GEOS657_Lab4.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex1.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex2.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex3A.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex3B.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex4A.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex4B.py
python /home/jovyan/opensarlab-notebook_testing/Test_Master_Change_Detection_Amplitude_Time_Series_Example.py
python /home/jovyan/opensarlab-notebook_testing/Test_ASF_Projects_Subset_Data_Stack.py
python /home/jovyan/opensarlab-notebook_testing/Test_Master_Subset_Data_Stack.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Subset_Data_Stack.py
## Deactivate rtc_analysis environment
conda deactivate
##Re-install and activate insar_analysis conda environment
conda env create -f '/home/jovyan/conda_environments/Environment_Configs/insar_analysis_env.yml' --prefix "/home/jovyan/.local/envs/insar_analysis" --force
conda run -n insar_analysis kernda --display-name insar_analysis -o /home/jovyan/.local/envs/insar_analysis/share/jupyter/kernels/python3/kernel.json
conda init
source /home/jovyan/conda_environments/install_insar_analysis_pkgs.sh
conda activate /home/jovyan/.local/envs/insar_analysis
## Run tests on notebooks that use insar_analysis environment
python /home/jovyan/opensarlab-notebook_testing/Test_Master_InSAR_volcano_source_modeling.py
python /home/jovyan/opensarlab-notebook_testing/Test_GEOS657_Lab6.py
## Deactivate insar_analysis environment
conda deactivate
##Re-install and activate the machine learning conda environment
conda env create -f '/home/jovyan/conda_environments/Environment_Configs/machine_learning_env.yml' --prefix "/home/jovyan/.local/envs/machine_learning" --force
conda run -n machine_learning kernda --display-name machine_learning -o /home/jovyan/.local/envs/machine_learning/share/jupyter/kernels/python3/kernel.json
conda init
conda activate /home/jovyan/.local/envs/machine_learning
## Run tests on notebooks that use the machine_learning environment
python /home/jovyan/opensarlab-notebook_testing/Test_Master_CRNN_change_detection.py
## Deactivate machine_learning environment
conda deactivate
# ##Re-install and activate the train conda environment
# conda env create -f '/home/jovyan/conda_environments/Environment_Configs/train_env.yml' --prefix "/home/jovyan/.local/envs/train" --force
# conda run -n train kernda --display-name train -o /home/jovyan/.local/envs/train/share/jupyter/kernels/python3/kernel.json
# conda init
# conda activate /home/jovyan/.local/envs/train
# ## Run tests on notebooks that use the train environment
# python /home/jovyan/opensarlab-notebook_testing/Test_GEOS_657_2019_Lab9_InSARTimeSeriesAnalysis_Part1_DataDownload_HyP3_v2.py
# ## Deactivate train environment
# conda deactivate
echo 'Done running tests on the notebooks!'
echo 'Check the logs for exceptions and failures!'
## Get rid of spaces in log filenames
oldnames="/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/*.log"
for f in $oldnames
do
  new="${f// /_}"
  if [ "$new" != "$f" ]
  then
    if [ -e "$new" ]
    then
      echo not renaming \""$f"\" because \""$new"\" already exists
    else
      echo moving "$f" to "$new"
    mv "$f" "$new"
  fi
fi
done
now=$(date +'%m_%d_%Y')
issue_counter=0
FILES="/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/*.test.log"
for f in $FILES
   do
   fail_flag="FALSE"
   exception_flag="FALSE"
      echo "Checking file" $f >> test_report_$now.txt
      if  grep -q "**FAILED**" "$f"; then
         grep "**FAILED**" $f >> test_report_$now.txt
         fail_flag="TRUE"
         issue_counter=$((issue_counter+1));
      fi
      if  grep -q "EXCEPTION" "$f"; then
         grep "EXCEPTION" $f >> test_report_$now.txt
         exception_flag="TRUE"
         issue_counter=$((issue_counter+1));
      fi
      if  [ "$fail_flag" = "FALSE" ] && [ "$exception_flag" = "FALSE" ]; then
         if grep -q "PASSED" "$f"; then
            echo "Tests PASSED!" >> test_report_$now.txt
         fi
      fi
   mv $f  "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/old_logs/"
   done
infologs="/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/*.info.log"
for f in $infologs
do
   mv $f "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/old_logs/"
done
##mail -s "OSL Notebook Test Report" testern@alaska.edu <  test_report_$now.txt
mv test_report_$now.txt "/home/jovyan/opensarlab-notebook_testing/reports/"
echo 'Issues: '$issue_counter
