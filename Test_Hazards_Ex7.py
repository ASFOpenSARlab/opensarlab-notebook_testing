#!/usr/bin/env python3

from getpass import getpass
import shutil

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = "/home/jovyan/opensarlab-notebooks/SAR_Training/English/Hazards/Exercise7-PairwiseInSARWithSNAP.ipynb"
log_pth = "/home/jovyan/notebooks/notebook_testing_dev"
test = ASFNotebookTest(notebook_pth, log_pth)

# Input tester's Earthdata creds
username = input("Earthdata Username: ")
password = getpass("Earthdata Password: ")

# Replace Earthdata login prompt with login based on tester's creds 
test.replace_cell("login = EarthdataLogin()",
                  f"login = EarthdataLogin(username='{username}', password='{password}')")

# Change data path for testing
_to_replace = "path = \"/home/jovyan/notebooks/SAR_Training/English/Hazards/data_CBCInSAR\""
test_data_path = "/home/jovyan/notebooks/notebook_testing_dev/data_CBCInSAR"
_replacement = f"path = f\"{test_data_path}\""
test.replace_line(_to_replace, _to_replace, _replacement)

# Erase data directory if already present
try:
   shutil.rmtree(test_data_path)
except:
   pass


######### TESTS ###########

# Confirm products were downloaded from ASF Data Search
test_download = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A.zip"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A.zip found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A.zip NOT found")
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699.zip"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699.zip found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699.zip NOT found")
"""
test.add_test_cell('cmd = get_wget_cmd(pre_event_info["downloadUrl"], login)', 
                   test_download)

# Confirm successful topsar_split of pre-event zip
test_pre_event_topsar_split = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS.data"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS.data found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS.data NOT found")
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS.dim"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS.dim found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS.dim NOT found")
"""
test.add_test_cell("pre_event_split = topsar_split(pre_event, 'IW1', os.getcwd(), '')",
                   test_pre_event_topsar_split)

# Confirm successful topsar_split of post-event zip
test_post_event_topsar_split = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS.data"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS.data found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS.data NOT found")
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS.dim"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS.dim found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS.dim NOT found")
"""
test.add_test_cell("post_event_split = topsar_split(post_event, 'IW1', os.getcwd(), '')",
                   test_post_event_topsar_split)

# Confirm successful apply_orbit call on pre-event data
test_pre_event_apply_orbit = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB.data"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB.data found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB.data NOT found")
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB.dim"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB.dim found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB.dim NOT found")
"""
test.add_test_cell("pre_event_orbit_output = apply_orbit(pre_event_split, os.getcwd())",
                   test_pre_event_apply_orbit)

# Confirm successful apply_orbit call on post-event data
test_post_event_apply_orbit = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS_OB.data"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS_OB.data found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS_OB.data NOT found")
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS_OB.dim"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS_OB.dim found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170401T114956_20170401T115026_015950_01A4D5_C699_TS_OB.dim NOT found")
"""
test.add_test_cell("post_event_orbit_output = apply_orbit(post_event_split, os.getcwd())",
                   test_post_event_apply_orbit)

# Confirm successful back geocoding of pre and post event orbit output
test_back_geocoding = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG.data"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG.data found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG.data NOT found")
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG.dim"):
    test.log_test('p', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG.dim found")
else:
    test.log_test('f', f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG.dim NOT found")
"""
test.add_test_cell("back_geocoded_output = back_geocoding(pre_event_orbit_output, post_ev",
             test_back_geocoding)

# Confirm successful co-registration of images with ESD
test_apply_esd = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG_ESD.dim"):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD.dim NOT found"))
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG_ESD.data"):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD.data NOT found"))
"""
test.add_test_cell("esd_output = apply_ESD(back_geocoded_output, os.getcwd())",
             test_apply_esd)

# Confirm successful creation of interferogram
test_create_interferogram = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG_ESD_INT.dim"):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT.dim NOT found"))
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG_ESD_INT.data"):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT.data NOT found"))
"""
test.add_test_cell("interferogram_output = create_interferogram(esd_output, os.getcwd())",
             test_create_interferogram)

# Confirm successful call of tosar_deburst on interferogram
test_topsar_deburst = """
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG_ESD_INT_DB.dim"):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB.dim NOT found"))
if os.path.exists(f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_TS_OB_BG_ESD_INT_DB.data"):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB.data NOT found"))
"""
test.add_test_cell("topsar_deburst_output = topsar_deburst(interferogram_output, os.getcwd())",
             test_topsar_deburst)

# Confirm successful call of topo_phase_remove on deburst interferogram
test_topo_phase_remove = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo.dim")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo.dim NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo.data")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo.data NOT found"))
"""
test.add_test_cell("topo_phase_remove_output = topo_phase_remove(topsar_deburst_output,os.getcwd(),'')",
             test_topo_phase_remove)

# Confirm successful call of multi_look on deburst interferogram with phase removed
test_multi_look = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML.dim")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML.dim NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML.data")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML.data NOT found"))
"""
test.add_test_cell("multi_look_output = multi_look(topo_phase_remove_output, os.getcwd())",
             test_multi_look)

# Confirm successful call of goldstein_filter on multilooked data
test_goldstein_filter = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF.dim")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF.dim NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF.data")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF.data NOT found"))
"""
test.add_test_cell("goldstein_filter_output = goldstein_filter(multi_look_output, os.getcwd())",
             test_goldstein_filter)

# Confirm successful phase unwrapping
test_phase_unwrap = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                        f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                        f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_UNW.dim")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_UNW.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_UNW.dim NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_UNW.data")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_UNW.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_UNW.data NOT found"))
"""
test.add_test_cell("phase_unwrap_output = phase_unwrap(multi_look_output, os.getcwd())",
             test_phase_unwrap)

# Confirm successful terrain correction on phase filtered data
test_terrain_correction_phase_filtered = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.dim")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.dim NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data NOT found"))
"""
test.add_test_cell("filtered_terrain_correction_output = terrain_correction(goldstein_filter_output",
             test_terrain_correction_phase_filtered)
             
# Confirm successful terrain correction on unfiltered data
test_terrain_correction_unfiltered = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_TC.dim")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_TC.dim found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_TC.dim NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_"
                   f"015775_019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_"
                        f"019FA4_097A_TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data NOT found"))
"""
test.add_test_cell("unfiltered_terrain_correction_output = terrain_correction(multi_look_output",
             test_terrain_correction_unfiltered)

# Confirm creation of interferogram from phase filtered, terrain corrected data
test_GF_TC_interferogram = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/amplitude.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/amplitude.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/amplitude.tif NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/phase.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/phase.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/phase.tif NOT found"))
"""
test.add_test_cell('cmd = f"cd {os.getcwd()}/{pre_event_base_granule}*GF_TC.data',
                  test_GF_TC_interferogram)

# Confirm creation of interferogram from unfiltered, terrain corrected data
test_Topo_ML_TC_interferogram = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/amplitude.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/amplitude.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/amplitude.tif NOT found"))
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/phase.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/phase.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/phase.tif NOT found"))
"""
test.add_test_cell('cmd = f"cd {os.getcwd()}/{pre_event_base_granule}*Topo_ML_TC.data',
                  test_Topo_ML_TC_interferogram)

# Confirm creation of phase filtered, terrain corrected geotiffs
test_GF_TC_geotiff = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/coh-{re.split('/',os.getcwd())[-1]}.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/coh-{re.split('/',os.getcwd())[-1]}.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/coh-{re.split('/',os.getcwd())[-1]}.tif NOT found"))
"""
test.add_test_cell('cmd = f"cd {os.getcwd()}/{pre_event_base_granule}*GF_TC.data;gdal_translate',
                   test_GF_TC_geotiff)

# Confirm creation of multi-looked, terrain corrected geotiffs
test_ML_TC_geotiff = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/coh-unfiltered-data_CBCInSAR.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/coh-unfiltered-data_CBCInSAR.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/coh-unfiltered-data_CBCInSAR.tif NOT found"))
"""
test.add_test_cell('cmd = f"cd {os.getcwd()}/{pre_event_base_granule}*Topo_ML_TC.data;gdal_translate',
                   test_ML_TC_geotiff)
    
# Confirm renaming of phase filtered, terrain corrected phase.tif
test_phase_data_CBCInSAR_tif = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/phase-data_CBCInSAR.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/phase-data_CBCInSAR.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/phase-data_CBCInSAR.tif NOT found"))
"""
test.add_test_cell('cmd = f"cd {os.getcwd()}/{pre_event_base_granule}*GF_TC.data;mv phase.tif',
                   test_phase_data_CBCInSAR_tif)

# Confirm renaming of multi-looked, terrain corrected phase.tif
test_unfiltered_phase_data_CBCInSAR_tif = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/phase-unfiltered-data_CBCInSAR.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/phase-unfiltered-data_CBCInSAR.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/phase-unfiltered-data_CBCInSAR.tif NOT found"))
"""
test.add_test_cell('cmd = f"cd {os.getcwd()}/{pre_event_base_granule}*Topo_ML_TC.data;mv phase.tif',
                   test_unfiltered_phase_data_CBCInSAR_tif)

# Confirm renaming of phase filtered, terrain corrected amplitude.tif
test_amp_data_CBCInSAR_tif = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/amp-data_CBCInSAR.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/amp-data_CBCInSAR.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_GF_TC.data/amp-data_CBCInSAR.tif NOT found"))
"""
test.add_test_cell('cmd = f"cd {os.getcwd()}/{pre_event_base_granule}*GF_TC.data;mv amplitude.tif',
                   test_amp_data_CBCInSAR_tif)

# Confirm renaming of multi-looked, terrain corrected amplitude.tif
test_unfiltered_amp_data_CBCInSAR_tif = """
if os.path.exists((f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/amplitude-unfiltered-data_CBCInSAR.tif")):
    test.log_test('p', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/amplitude-unfiltered-data_CBCInSAR.tif found"))
else:
    test.log_test('f', (f"{path}/S1A_IW_SLC__1SDV_20170320T114956_20170320T115025_015775_019FA4_097A_"
                   f"TS_OB_BG_ESD_INT_DB_Topo_ML_TC.data/amplitude-unfiltered-data_CBCInSAR.tif NOT found"))
"""
test.add_test_cell('cmd = f"cd {os.getcwd()}/{pre_event_base_granule}*Topo_ML_TC.data;mv amplitude.tif',
                   test_unfiltered_amp_data_CBCInSAR_tif)

# Confirm creation of tifs directory
test_tif_dir = """
if os.path.exists(f"{path}/{tifs_path}"):
    test.log_test('p', f"{path}/{tifs_path} found")
else:
    test.log_test('f', f"{path}/{tifs_path} NOT found")
"""
test.add_test_cell("tifs_path = 'tifs'", test_tif_dir)

# Confirm all tifs moved to tifs directory
test_move_tifs = """
test_tifs = {f"{path}/{tifs_path}/amp-data_CBCInSAR.tif", 
             f"{path}/{tifs_path}/phase-data_CBCInSAR.tif", 
             f"{path}/{tifs_path}/coh-unfiltered-data_CBCInSAR.tif", 
             f"{path}/{tifs_path}/phase-unfiltered-data_CBCInSAR.tif", 
             f"{path}/{tifs_path}/coh-data_CBCInSAR.tif", 
             f"{path}/{tifs_path}/amplitude-unfiltered-data_CBCInSAR.tif"}
if set(glob.glob(f"{path}/{tifs_path}/*.tif")) == test_tifs:
    test.log_test('p', f"tifs moved to {path}/{tifs_path}")
else:
    test.log_test('f', f"tifs NOT moved to {path}/{tifs_path}")
"""
test.add_test_cell("!mv */*.tif ./tifs", test_move_tifs)

######## RUN THE NOTEBOOK AND TEST CODE #########

all_the_code = test.assemble_code(include_tests=True)
for cell_index in all_the_code:
    test.output(all_the_code[cell_index], cell_index, terminal=True, log=True)
    with std_out_io() as stdio:
        try:
            exec(all_the_code[cell_index])
        except Exception as e:
            test.log_test('e', f"cell {cell_index}, {e}") 
    print(f"Output: {stdio.getvalue()}")
    test.log_info(f"Output: {stdio.getvalue()}")
    
    

