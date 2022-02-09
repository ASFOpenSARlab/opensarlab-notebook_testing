#!/usr/bin/env python3

from getpass import getpass
import shutil

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = r"/home/jovyan/GEOS_657_Labs/2019/GEOS 657-Lab6-VolcanoSourceModelingfromInSAR.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = 'path = f"{os.getcwd()}/lab_6_data"'
_replacement = 'path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_data_GEOS657lab_6"'
test.replace_line(_to_replace, _to_replace, _replacement)

# remove template code cells for HW problems
test.replace_cell("# ------------ Change Variables HERE --------------- #")
test.replace_cell("# !!!! MODIFY THIS SCRIPT TO PERFORM A GRID SEARCH OVER zs AND V: !!!!")

# Erase data directory if already present
try:
   shutil.rmtree(test_data_path)
except:
   pass

# Skip all cells inputing user defined values for filtering products to download
# or those involving conda environment checks
skip_em = ["import url_widget as url_w",
           "if env[0] != '/home/jovyan/.local/envs/insar_analysis':"]

for search_str in skip_em:
    test.replace_cell(search_str)
    
######### TESTS ###########

# Check that the data was downloaded from the S3 bucket
test_s3_copy = """
if os.path.exists(deformation_map):
    test.log_test('p', f"{deformation_map} successfully copied from {deformation_map_path}")
else:
    test.log_test('f', f"{deformation_map} NOT successfully copied from {deformation_map_path}")
"""
#test.add_test_cell("subprocess.check_call(['aws', 's3', 'cp',  deformation_map_path, deformation_map])",
#                   test_s3_copy)
test.add_test_cell("!aws --region=us-west-2 --no-sign-request s3 cp $deformation_map_path $deformation_map", test_s3_copy)

# Confirm observed_deformation_map.shape == (980, 1100)
test_observed_deformation_map = """
if observed_deformation_map.shape == (980, 1100):
    test.log_test('p', f"observed_deformation_map.shape == (980, 1100)")
else:
    test.log_test('f', f"observed_deformation_map.shape == {observed_deformation_map.shape}, NOT (980, 1100)")   
"""
test.add_test_cell("observed_deformation_map = np.reshape(coh, (line, sample))",
                   test_observed_deformation_map)

# Confirm nans removed from observed_deformation_map
test_observed_deformation_map_nans = """
test_nans = np.isnan(observed_deformation_map)
if True not in test_nans:
    test.log_test('p', f"nans removed from observed_deformation_map")
else:
    test.log_test('f', f"nans NOT removed from observed_deformation_map")
"""
test.add_test_cell("observed_deformation_map[where_are_NaNs] = 0",
                   test_observed_deformation_map_nans)

# Confirm type and shape of observed_deformation_map_m
test_observed_deformation_map_m = """
if type(observed_deformation_map_m) == np.ma.core.MaskedArray:
    test.log_test('p', f"type(observed_deformation_map_m) == np.ma.core.MaskedArray")
else:
    test.log_test('f', f"type(observed_deformation_map_m) == {type(observed_deformation_map_m)}, NOT np.ma.core.MaskedArray")
if observed_deformation_map_m.shape == (980, 1100):
    test.log_test('p', f"observed_deformation_map_m.shape == (980, 1100)")
else:
    test.log_test('f', f"observed_deformation_map_m.shape == {observed_deformation_map_m.shape}, NOT (980, 1100)")
"""
test.add_test_cell("observed_deformation_map_m = np.ma.masked_where(observed_deformation_map==0, observed_deformation_map)",
                   test_observed_deformation_map_m)

# Confirm creation of plots directory
test_product_path = """
if os.path.exists(f"{path}/{product_path}"):
    test.log_test('p', f"{path}/{product_path} found")
else:                  
    test.log_test('f', f"{path}/{product_path} NOT found")
"""
test.add_test_cell("product_path = 'plots'",
                   test_product_path)

# Confirm creation of Okmok-inflation-observation.png
test_Okmok_inflation_observation_png = """
if os.path.exists(f"{path}/{product_path}/Okmok-inflation-observation.png"):
    test.log_test('p', f"{path}/{product_path}/Okmok-inflation-observation.png found")
else:
    test.log_test('f', f"{path}/{product_path}/Okmok-inflation-observation.png NOT found")
"""
test.add_test_cell("output_filename='Okmok-inflation-observation.png', dpi=200)",
                   test_Okmok_inflation_observation_png)
                   
# Confirm creation of Model-samples-3by3.png
test_Model_samples_3by3_png = """
if os.path.exists(f"{path}/{product_path}/Model-samples-3by3.png"):
    test.log_test('p', f"{path}/{product_path}/Model-samples-3by3.png found")
else:
    test.log_test('f', f"{path}/{product_path}/Model-samples-3by3.png NOT found")
"""
test.add_test_cell("plt.savefig('Model-samples-3by3.png', dpi=200, transparent='false')",
                   test_Model_samples_3by3_png) 

# Confirm creation of Misfit-samples-3by3.png
test_Misfit_samples_3by3_png = """
if os.path.exists(f"{path}/{product_path}/Misfit-samples-3by3.png"):
    test.log_test('p', f"{path}/{product_path}/Misfit-samples-3by3.png found")
else:
    test.log_test('f', f"{path}/{product_path}/Misfit-samples-3by3.png NOT found")
"""
test.add_test_cell("plt.savefig('Misfit-samples-3by3.png', dpi=200, transparent='false')",
                   test_Misfit_samples_3by3_png) 

# Confirm Mogi source location
test_mogi_source_location = """
if xs[mmf[0]][0] == 20.599999999999994:
    test.log_test('p', f"xs[mmf[0]][0] == 20.599999999999994")
else:
    test.log_test('f', f"xs[mmf[0]][0] == {xs[mmf[0]][0]}, NOT 20.599999999999994")
if ys[mmf[1]][0] == 21.799999999999997:
    test.log_test('p', f"ys[mmf[1]][0] == 21.799999999999997")
else:
    test.log_test('f', f"ys[mmf[1]][0] == {ys[mmf[1]][0]}, NOT 21.799999999999997")
"""
test.add_test_cell("mmf = np.where(misfit == np.min(misfit))",
                   test_mogi_source_location)

# Confirm creation of Misfit-function.png
test_Misfit_function_png = """
if os.path.exists(f"{path}/{product_path}/Misfit-function.png"):
    test.log_test('p', f"{path}/{product_path}/Misfit-function.png found")
else:
    test.log_test('f', f"{path}/{product_path}/Misfit-function.png NOT found")
"""
test.add_test_cell("plt.savefig('Misfit-function.png', dpi=200, transparent='false')",
                   test_Misfit_function_png) 

# Confirm creation of BestFittingMogiDefo.png
test_BestFittingMogiDefo_png = """
if os.path.exists(f"{path}/{product_path}/BestFittingMogiDefo.png"):
    test.log_test('p', f"{path}/{product_path}/BestFittingMogiDefo.png found")
else:
    test.log_test('f', f"{path}/{product_path}/BestFittingMogiDefo.png NOT found")
"""
test.add_test_cell("plt.savefig('BestFittingMogiDefo.png', dpi=200, transparent='false')",
                   test_BestFittingMogiDefo_png) 

# Confirm creation of Residuals-ObsMinusMogi.png
test_Residuals_ObsMinusMogi_png = """
if os.path.exists(f"{path}/{product_path}/Residuals-ObsMinusMogi.png"):
    test.log_test('p', f"{path}/{product_path}/Residuals-ObsMinusMogi.png found")
else:
    test.log_test('f', f"{path}/{product_path}/Residuals-ObsMinusMogi.png NOT found")
"""
test.add_test_cell("plt.savefig('Residuals-ObsMinusMogi.png', dpi=200, transparent='false')",
                   test_Residuals_ObsMinusMogi_png) 


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