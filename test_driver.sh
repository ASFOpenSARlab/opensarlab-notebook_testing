#! /bin/sh

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
python Test_Hazardss_Ex1.py
echo 'Running Test_Hazards_Ex2.py'
python Test_Hazardss_Ex2.py
echo 'Activating insar_analysis env'
conda activate /home/jovyan/.local/envs/insar_analysis
echo 'Running Test_Master_InSAR_volcano_source_modeling.py'
python Test_Master_InSAR_volcano_source_modeling.py
echo 'Running Test_GEOS657_Lab6.py'
python Test_GEOS657_Lab6.py
echo 'Done'
