#! /bin/sh
oldlogs="/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/old_logs/*.log"
for f in $oldlogs
do
   rm $f
done
# Activate rtc_analysis conda environment
conda init bash
source ~/.bashrc
conda activate /home/jovyan/.local/envs/rtc_analysis
# Run tests on notebooks that use rtc_analysis environment
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex1.py
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex2.py
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex3.py
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex4A.py
python /home/jovyan/opensarlab-notebook_testing/Test_Ecosystems_Ex4B.py
python /home/jovyan/opensarlab-notebook_testing/Test_GEOS657_Lab4.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex1.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex2.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex3B.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex4A.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Ex4B.py
python /home/jovyan/opensarlab-notebook_testing/Test_Master_Change_Detection_Amplitude_Time_Series_Example.py
python /home/jovyan/opensarlab-notebook_testing/Test_ASF_Projects_Subset_Data_Stack.py
python /home/jovyan/opensarlab-notebook_testing/Test_Master_Subset_Data_Stack.py
python /home/jovyan/opensarlab-notebook_testing/Test_Hazards_Subset_Data_Stack.py
# Deactive rtc_analysis environment
conda deactivate
# Activate insar_analysis conda environment
conda activate /home/jovyan/.local/envs/insar_analysis
# Run tests on notebooks that use insar_analysis environment
python /home/jovyan/opensarlab-notebook_testing/Test_Master_InSAR_volcano_source_modeling.py
python /home/jovyan/opensarlab-notebook_testing/Test_GEOS657_Lab6.py
# Deactive insar_analysis environment
conda deactivate
echo 'Done running tests on the notebooks!'
echo 'Check the logs for exceptions and failures!'
# Get rid of spaces in log filenames
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
#mail -s "OSL Notebook Test Report" testern@alaska.edu <  test_report_$now.txt
mv test_report_$now.txt "/home/jovyan/opensarlab-notebook_testing/reports/"
echo 'Issues: '$issue_counter
