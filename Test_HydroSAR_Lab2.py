#!/usr/bin/env python3

from getpass import getpass
from pathlib import Path
import shutil
import glob
import subprocess as sp

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

notebook_pth = r"/home/jovyan/notebooks/SAR_Training/English/HydroSAR/Lab2-SurfaceWaterExtentMapping.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = 'tiff_dir = path = Path(f"/home/jovyan/notebooks/SAR_Training/English/HydroSAR/{name}")'
_replacement = 'tiff_dir = path = Path("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2")'
test.replace_line(_to_replace, _to_replace, _replacement)

# Erase data directory if already present
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2"
try:
   shutil.rmtree(str(test_data_path))
except:
   pass

# Skip all cells inputing user defined values for filtering products to download
# or those involving conda environment checks
skip_em = ["notebookUrl = url_w.URLWidget()",
           "if env[0] != '/home/jovyan/.local/envs/hydrosar':",
           "display(delete)",
           "if 'Delete' in delete.value:",
           "def get_tiff_paths(paths: str) -> list:",
           "f = FileChooser(Path.cwd())"]

for search_str in skip_em:
    test.replace_cell(search_str)
    
# # Replace inline shell command with rglob
# _to_replace = '    tiff_paths = !ls $paths | sort -t_ -k5,5'
# _replacement = "    tiff_paths = sp.getoutput('ls {paths} | sort -t_ -k5,5')"
# test.replace_line(_to_replace, _to_replace, _replacement)

# Replace first case of get_tiff_paths
_to_replace = "mask_directory = tiff_dir/'Water_Masks'"
_replacement = """
mask_directory = tiff_dir/'Water_Masks'

if not mask_directory.exists():
    mask_directory.mkdir()
    
paths = tiff_dir/"*_V*.tif*"
if tiff_dir.exists():
    temp_tiff_paths = sp.getoutput('ls /home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/*_V*.tif* | sort -t_ -k5,5')
    tiff_paths = list(temp_tiff_paths.split())
"""
test.replace_cell(_to_replace, _replacement)


# Replace second and third cases of get_tiff_paths
_to_replace = "class SARDualPolError(Exception):"
_replacement = """
class SARDualPolError(Exception):
    '''
    Raise when expecting dual-pol SAR data
    but single-pol found instead
    '''
    pass

vv_wild = tiff_dir/'*_VV.tif*'
vh_wild = tiff_dir/'*_VH.tif*'

if tiff_dir.exists():
    temp_vh_paths = sp.getoutput('ls /home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/*_VH.tif* | sort -t_ -k5,5')
    vh_paths = list(temp_vh_paths.split())
    temp_vv_paths = sp.getoutput('ls /home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/*_VV.tif* | sort -t_ -k5,5')
    vv_paths = list(temp_vv_paths.split())

for i, pth in enumerate(vv_paths):
    vh = f"{pth.split('_V')[0]}_VH{Path(pth).suffix}"
    if vh not in vh_paths:
        raise SARDualPolError(f"Found {pth} but not {vh}")        
for i, pth in enumerate(vh_paths):
    vv = f"{pth.split('_V')[0]}_VV{Path(pth).suffix}"
    if vv not in vv_paths:
        raise SARDualPolError(f"Found {pth} but not {vv}")
        
print(f"Success: dual-pol data found")

"""
test.replace_cell(_to_replace, _replacement)

# Hard code the HAND layer
_to_replace = "HAND_file = Path(f.selected)"
_replacement = "HAND_file = '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/Bangladesh_Training_DEM_hand.tif'"
test.replace_line(_to_replace, _to_replace, _replacement)


######### TESTS ###########

# Confirm data directory exists
test_datadirectory = """
if Path(f"{path}").exists():
    test.log_test('p', f"{path} exists!")
else:
    test.log_test('f', f"{path} does NOT exist!")
"""
test.add_test_cell("if not tiff_dir.exists():", test_datadirectory)

# Check that the data was downloaded from the S3 bucket
test_s3_copy = """
if Path(f"{path}/20200603_VH.tiff").exists():
    test.log_test('p', f"Bangladesh.tar.gz successfully copied from {time_series_path}")
else:
    test.log_test('f', f"Bangladesh.tar.gz NOT copied from {time_series_path}")
"""
test.add_test_cell("!aws --region=us-east-1 --no-sign-request s3 cp $time_series_path $time_series", test_s3_copy)

# Confirm we have extracted 32 tiff files from the tarball
test_extract = """
test_extracted_path = f"{path}/*.tiff"
test_len = len(glob.glob(test_extracted_path))
if test_len == 32:
    test.log_test('p', f"{test_len} tiffs extracted from {time_series_path}")
else:
    test.log_test('f', f"Expected 32 tiffs extracted from tarball, found {test_len}")
"""
test.add_test_cell("!tar -xvzf {name}.tar.gz -C {path}", test_extract)

# Confirm existence of the DEM
test_dem = """
if Path(f"{path}/Bangladesh_Training_DEM_hand.tif").exists():
    test.log_test('p', f"Bangladesh_Training_DEM_hand.tif was successfully extracted from the tar.gz")
else:
    test.log_test('f', f"Bangladesh_Training_DEM_hand.tif does NOT exist!!!")
"""
test.add_test_cell("!tar -xvzf {name}.tar.gz -C {path}", test_dem)

# Verify creation of Water_Masks directory
test_water_mask = """
if Path(f"{path}/Water_Masks").exists():
    test.log_test('p', f"{path}/Water_Masks exists!")
else:
    test.log_test('f', f"{path}/Water_Masks does NOT exist!")
"""
test.add_test_cell("mask_directory = tiff_dir/'Water_Masks'", test_water_mask)

# Verify correct grouping of paths
test_grouped_paths = """
expected_grouped_paths = "{'/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200603_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200603_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200603_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200612_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200612_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200612_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200615_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200615_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200615_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200624_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200624_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200624_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200627_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200627_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200627_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200706_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200706_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200706_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200709_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200709_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200709_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200712_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200712_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200712_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200718_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200718_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200718_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200721_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200721_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200721_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200724_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200724_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200724_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200727_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200727_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200727_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200730_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200730_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200730_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200802_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200802_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200802_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200811_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200811_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200811_VV.tiff'], '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200814_': ['/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200814_VH.tiff', '/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_hydrosar_lab2/20200814_VV.tiff']}"
actual_grouped_paths = str(grouped_pths)
if actual_grouped_paths == expected_grouped_paths:
    test.log_test('p', f"Grouped paths are correct: {expected_grouped_paths}")
else:
    test.log_test('f', f"Grouped paths == {actual_grouped_paths}, NOT {expected_grouped_paths}")
"""
test.add_test_cell('grouped_pths = group_polarizations(tiff_paths)', test_grouped_paths)


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