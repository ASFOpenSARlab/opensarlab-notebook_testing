#! /bin/sh
oldlogs="/home/jovyan/notebooks/notebook_testing_logs/old_logs/*.log"
for f in $oldlogs
do
   rm $f
done
echo 'Activating rtc_analysis env'
conda activate /home/jovyan/.local/envs/rtc_analysis
echo 'Running Test_Ecosystems_Ex1.py'
python Test_Ecosystems_Ex1.py
echo 'Running Test_Ecosystems_Ex2.py'
python Test_Ecosystems_Ex2.py
echo 'Running Test_Ecosystems_Ex3.py'
python Test_Ecosystems_Ex3.py
echo 'Running Test_Ecosystems_Ex4A.py'
python Test_Ecosystems_Ex4A.py
echo 'Running Test_Ecosystems_Ex4B.py'
python Test_Ecosystems_Ex4B.py
echo 'Running Test_GEOS657_Lab4.py'
python Test_GEOS657_Lab4.py
echo 'Running Test_Hazards_Ex1.py'
python Test_Hazards_Ex1.py
echo 'Running Test_Hazards_Ex2.py'
python Test_Hazards_Ex2.py
echo 'Running Test_Hazards_Ex3B.py'
python Test_Hazards_Ex3B.py
echo 'Running Test_Hazards_Ex4A.py'
python Test_Hazards_Ex4A.py
echo 'Running Test_Hazards_Ex4B.py'
python Test_Hazards_Ex4B.py
echo 'Running Test_Master_Change_Detection_Amplitude_Time_Series_Example.py'
python Test_Master_Change_Detection_Amplitude_Time_Series_Example.py
echo 'Deactivating rtc_analysis env'
conda deactivate
echo 'Activating insar_analysis env'
conda activate /home/jovyan/.local/envs/insar_analysis
echo 'Running Test_Master_InSAR_volcano_source_modeling.py'
python Test_Master_InSAR_volcano_source_modeling.py
echo 'Running Test_GEOS657_Lab6.py'
python Test_GEOS657_Lab6.py
conda deactivate
echo 'Done running tests on the notebooks!'
echo 'Check the logs for exceptions and failures!'
# Get rid of spaces in log filenames
oldnames="/home/jovyan/notebooks/notebook_testing_logs/*.log"
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
FILES="/home/jovyan/notebooks/notebook_testing_logs/*.test.log"
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
   mv $f  "/home/jovyan/notebooks/notebook_testing_logs/old_logs/"
   done
infologs="/home/jovyan/notebooks/notebook_testing_logs/*.info.log"
for f in $infologs
do
   mv $f "/home/jovyan/notebooks/notebook_testing_logs/old_logs/"
done
mv test_report_$now.txt "/home/jovyan/opensarlab-notebook_testing/reports/"
echo 'Issues: '$issue_counter
#echo "hello world" | mail -s "a subject" testern@alaska.edu