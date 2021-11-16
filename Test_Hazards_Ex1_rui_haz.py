#!/usr/bin/env python3

from getpass import getpass
import shutil

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

notebook_pth = "/home/jovyan/notebooks/SAR_Training/English/Hazards/Exercise1-ReadAnalyzeSARStack.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = 'analysis_dir = Path(f"/home/jovyan/notebooks/SAR_Training/English/Hazards/{name}")'
_replacement = 'analysis_dir = Path(f"/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/hazards_test_Ex1")'
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
if Path(f"{analysis_dir/time_series_path}").exists():
    test.log_test('p', f"{time_series_path} successfully copied from {s3_path}")
else:
    test.log_test('f', f"{time_series_path} NOT copied from {s3_path}")
"""
test.add_test_cell("!aws --region=us-east-1 --no-sign-request s3 cp $s3_path {analysis_dir/time_series_path}", test_s3_copy)

# Check that 152 tiffs, 2 csvs, and 2 vrts were extracted from the tarball
test_extract = """
import glob
test_extracted_path = analysis_dir/"tiffstropical/*.tif"
test_len = len(glob.glob(str(test_extracted_path)))
if test_len == 152:
    test.log_test('p', f"{test_len} tifs extracted from {time_series_path}")
else:
    test.log_test('f', f"Expected 152 tifs extracted from tarball, found {test_len}")
    
test_csv_path = analysis_dir/"*.csv"
test_vrt_path = analysis_dir/"*.vrt"
test_csv_len = len(glob.glob(str(test_csv_path)))
test_vrt_len = len(glob.glob(str(test_vrt_path)))
if test_csv_len == test_vrt_len == 2:
    test.log_test('p', f"Extracted 2 csvs and vrts")
else:
    test.log_test('f', f"Expected 2 csvs and vrts. Found {test_csv_len} csv files and {test_vrt_len} vrt files.")    

"""
test.add_test_cell("!tar -xvzf {analysis_dir/'tropical.tar.gz'} -C {analysis_dir}", test_extract)

# Check that a gdal dataset has been opened for a vrt in each polarization and then stored in a dictionary
test_vrt_dict = """
for test_polar in polarizations:
    try:
        if type(img[test_polar]) == gdal.Dataset:
            test.log_test('p', f"type(img['{test_polar}']) == gdal.Dataset")
        else:
            test.log_test('f', f"type(img['{test_polar}']) == {type(img[test_polar])}. Expected gdal.Dataset")
    except KeyError:
            test.log_test('f', f"Invalid key '{test_polar}'")

"""
test.add_test_cell("img = {pol: gdal.Open(str(imagefile[pol])) for pol in polarizations}", test_vrt_dict)

# Confirm raster shape = (921, 1069)
test_raster_shape = """
if raster.shape == (921, 1069):
    test.log_test('p', f"raster.shape == {raster.shape}")
else:
    test.log_test('f', f"raster.shape == {raster.shape}. Expected (921, 1069)")
"""
test.add_test_cell("raster = band.ReadAsArray()", test_raster_shape)

# Confirm that time series animation was created
test_animation = """
if Path(f"{product_path}/animation.gif").exists():
    test.log_test('p', f"{product_path}/animation.gif exists")
else:
    test.log_test('f', f"{product_path}/animation.gif does NOT exist")
"""
test.add_test_cell("ani.save(f\"{product_path}/animation.gif\", writer='pillow', fps=2)", test_animation)

# Confirm that the time-series of means histogram was created
test_rcs = """
if Path(f"{product_path}/RCSoverTime.png").exists():
    test.log_test('p', f"{product_path}/RCSoverTime.png exists")
else:
    test.log_test('f', f"{product_path}/RCSoverTime.png does NOT exist")
"""
test.add_test_cell("plt.savefig(f\"{product_path}/RCSoverTime.png\",", test_rcs)

# Confirm anmimation histogram was created
test_ani_hist = """
if Path(f"{product_path}/animation_histogram.gif").exists():
    test.log_test('p', f"{product_path}/animation_histogram.gif exists")
else:
    test.log_test('f', f"{product_path}/animation_histogram.gif does NOT exist")
"""
test.add_test_cell("ani.save(f\"{product_path}/animation_histogram.gif\",", test_ani_hist)

######## RUN THE NOTEBOOK AND TEST CODE #########

all_the_code = test.assemble_code(include_tests=True)
for cell_index in all_the_code:
    test.output(all_the_code[cell_index], cell_index, terminal=True, log=True)
    with std_out_io() as stdio:
        try:
            exec(all_the_code[cell_index])
        except Exception as e:
            test.log_test('e', e) 
    print(f"Output: {stdio.getvalue()}")
    test.log_info(f"Output: {stdio.getvalue()}")
    