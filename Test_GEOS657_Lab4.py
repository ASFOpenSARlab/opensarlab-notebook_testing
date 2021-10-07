#!/usr/bin/env python3

from getpass import getpass
import shutil

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = r"/home/jovyan/GEOS_657_Labs/2019/GEOS 657-Lab4-SARTimeSeriesAnalysis.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = "path = \"/home/jovyan/notebooks/ASF/GEOS_657_Labs/2019/lab_4_data\""
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/data_lab_4"
_replacement = f"path = f\"{test_data_path}\""
test.replace_line(_to_replace, _to_replace, _replacement)

# Change data directory for product files
_to_replace = "datadirectory = \'/home/jovyan/notebooks/ASF/GEOS_657_Labs/2019/lab_4_data/time_series/S32644X696260Y3052060sS1-EBD\'"
test_data_directory = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/data_lab_4/time_series/S32644X696260Y3052060sS1-EBD"
_replacement = f"datadirectory = f\"{test_data_directory}\""
test.replace_line(_to_replace, _to_replace, _replacement)

# Erase data directory if already present
try:
   shutil.rmtree(test_data_path)
except:
   pass

# Skip all cells inputing user defined values for filtering products to download
# or those involving conda environment checks
skip_em = ["var kernel = Jupyter.notebook.kernel;",
           "if env[0] != '/home/jovyan/.local/envs/rtc_analysis':"]

for search_str in skip_em:
    test.replace_cell(search_str)




######### TESTS ###########

# Check that the data was downloaded from the S3 bucket
test_s3_copy = """
if os.path.exists(f"{os.getcwd()}/time_series.zip"):
    test.log_test('p', f"time_series.zip successfully copied from s3://asf-jupyter-data/time_series.zip")
else:
    test.log_test('f', f"time_series.zip NOT copied from s3://asf-jupyter-data/time_series.zip")
"""
test.add_test_cell("!aws --region=us-east-1 --no-sign-request s3 cp $time_series_path $time_series", test_s3_copy)


# Confirm that all expected files were extracted from the zip
test_zip_extraction = """
import glob
test_vrt_qty = len(glob.glob("time_series/S32644X696260Y3052060sS1-EBD/*.vrt"))
if test_vrt_qty == 18:
    test.log_test('p', f"18 vrts extracted, as expected")
else:
    test.log_test('f', f"{test_vrt_qty} vrts extracted, NOT 18") 
test_tif_qty = len(glob.glob("time_series/S32644X696260Y3052060sS1-EBD/*.tif"))
if test_tif_qty == 5:
    test.log_test('p', f"5 tifs extracted, as expected")
else:
    test.log_test('f', f"{test_tif_qty} tifs extracted, NOT 5")     
test_dates_qty = len(glob.glob("time_series/S32644X696260Y3052060sS1-EBD/*.dates"))
if test_dates_qty == 17:
    test.log_test('p', f"17 dates files extracted, as expected")
else:
    test.log_test('f', f"{test_dates_qty} dates files extracted, NOT 17")    
"""
test.add_test_cell("asf_unzip(os.getcwd(), time_series)", test_zip_extraction)

# Confirm creation of tindex
test_tindex = """
if type(tindex) == pd.core.indexes.datetimes.DatetimeIndex:
    test.log_test('p', f"type(tindex) == pd.core.indexes.datetimes.DatetimeIndex")
else:
    test.log_test('f', f"type(tindex) == {type(tindex)}, NOT pd.core.indexes.datetimes.DatetimeIndex")
if tindex.size == 70:
    test.log_test('p', f"tindex.size == 70")
else:
    test.log_test('f', f"tindex.size == {tindex.size}, NOT 70")
"""
test.add_test_cell("tindex = pd.DatetimeIndex(dates)", test_tindex)

# Confirm raster_stack == (1270, 1547)
test_raster = """
if raster.shape == (1270, 1547):
    test.log_test('p', f"raster.shape == (1270, 1547)")
else:
    test.log_test('f', f"raster.shape == {raster.shape}, NOT (1270, 1547)")
"""
test.add_test_cell("raster = band.ReadAsArray()", test_raster)

# Confirm creation of plots_and_products directory
test_product_path = """
if os.path.exists(f"{test_data_path}/{product_path}"):
    test.log_test('p', f"{test_data_path}/{product_path} directory found")
else:
    test.log_test('f', f"{test_data_path}/{product_path} directory NOT found")
"""
test.add_test_cell("product_path = 'plots_and_animations'", test_product_path)

# Confirm creation of animation.gif
test_animation_gif = """
if os.path.exists(f"{test_data_path}/{product_path}/animation.gif"):
    test.log_test('p', f"{test_data_path}/{product_path}/animation.gif found")
else:
    test.log_test('f', f"{test_data_path}/{product_path}/animation.gif NOT found")
"""
test.add_test_cell("ani.save('animation.gif', writer='pillow', fps=2)", test_animation_gif)
#test.add_test_cell("ani.save('NepalTimeSeriesAnimation.gif', writer='pillow', fps=2)", test_animation_gif)

# Confirm rs_means_pwr.shape == (70,)
test_rs_means_pwr = """
if rs_means_pwr.shape == (70,):
    test.log_test('p', f"rs_means_pwr.shape == (70,)")
else:
    test.log_test('f', f"rs_means_pwr.shape == {rs_means_pwr.shape}, NOT (70,)")
"""
test.add_test_cell("rs_means_pwr.shape", test_rs_means_pwr)

# Confirm creation of time_series_means.png
test_time_series_means_png = """
if os.path.exists(f"{test_data_path}/{product_path}/time_series_means.png"):
    test.log_test('p', f"{test_data_path}/{product_path}/time_series_means.png found")
else:
    test.log_test('f', f"{test_data_path}/{product_path}/time_series_means.png NOT found")
"""
test.add_test_cell("plt.savefig('time_series_means', dpi=72, transparent='true')",
                   test_time_series_means_png)

# Confirm creation of animation_histogram.gif
test_animation__histogram_gif = """
if os.path.exists(f"{test_data_path}/{product_path}/animation_histogram.gif"):
    test.log_test('p', f"{test_data_path}/{product_path}/animation_histogram.gif found")
else:
    test.log_test('f', f"{test_data_path}/{product_path}/animation_histogram.gif NOT found")
"""
#test.add_test_cell("ani.save('NepalTSAnimation_means.gif', writer='pillow', fps=2)", test_animation__histogram_gif)
test.add_test_cell("ani.save('animation_histogram.gif', writer='pillow', fps=2)", test_animation__histogram_gif)


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