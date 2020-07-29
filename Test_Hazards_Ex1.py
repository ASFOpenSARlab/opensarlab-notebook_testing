#!/usr/bin/env python3

from getpass import getpass
import shutil

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

notebook_pth = "/home/jovyan/notebooks/SAR_Training/English/Hazards/Exercise1-ReadAnalyzeSARStack.ipynb"
log_pth = "/home/jovyan/notebooks/notebook_testing_dev"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = ("analysis_dir = f\"/home/jovyan/notebooks/SAR_Training/English/Hazards/{name}\"")
test_data_path = "/home/jovyan/notebooks/notebook_testing_dev/{name}"
_replacement = f"analysis_dir = \"{test_data_path}\""
test.replace_line("analysis_dir = f\"/home/jovyan/notebooks", _to_replace, _replacement)

# Erase data directory if already present
try:
   shutil.rmtree(test_data_path)
except:
   pass

######### TESTS ###########

# Check that the data was downloaded from the S3 bucket
test_s3_copy = """
if os.path.exists(f"{os.getcwd()}/{time_series_path}"):
    test.log_test('p', f"{time_series_path} successfully copied from {s3_path}")
else:
    test.log_test('f', f"{time_series_path} NOT copied from {s3_path}")
"""
test.add_test_cell("!aws s3 cp $s3_path $time_series_path", test_s3_copy)

# Check that 152 tiffs, 2 csvs, and 2 vrts were extracted from the tarball
test_extract = """
import glob
test_extracted_path = \"tiffstropical/*.tif\"
test_len = len(glob.glob(test_extracted_path))
if test_len == 152:
    test.log_test('p', f"{test_len} tifs extracted from {time_series_path}")
else:
    test.log_test('f', f"Expected 152 tifs extracted from tarball, found {test_len}")
    
test_csv_path = \"*.csv\"
test_vrt_path = \"*.vrt\"
test_csv_len = len(glob.glob(test_csv_path))
test_vrt_len = len(glob.glob(test_vrt_path))
if test_csv_len == test_vrt_len == 2:
    test.log_test('p', f"Extracted 2 csvs and vrts")
else:
    test.log_test('f', f"Expected 2 csvs and vrts. Found {test_csv_len} csv files and {test_vrt_len} vrt files.")    

"""
test.add_test_cell("!tar -xvzf tropical.tar.gz", test_extract)

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
test.add_test_cell("{pol: gdal.Open(imagefile[pol]) for pol in polarizations}", test_vrt_dict)

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
if os.path.exists(f\"{product_path}/animation.gif\"):
    test.log_test('p', f"{product_path}/animation.gif exists")
else:
    test.log_test('f', f"{product_path}/animation.gif does NOT exist")
"""
test.add_test_cell("ani.save(f\"{product_path}/animation.gif\", writer='pillow', fps=2)", test_animation)

# Confirm that the time-series of means histogram was created
test_rcs = """
if os.path.exists(f"{product_path}/RCSoverTime.png"):
    test.log_test('p', f"{product_path}/RCSoverTime.png exists")
else:
    test.log_test('f', f"{product_path}/RCSoverTime.png does NOT exist")
"""
test.add_test_cell("plt.savefig(f\"{product_path}/RCSoverTime.png\",", test_rcs)

# Confirm anmimation histogram was created
test_ani_hist = """
if os.path.exists(f"{product_path}/animation_histogram.gif"):
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
    