#!/usr/bin/env python3

from getpass import getpass
import shutil
import glob
import os

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

notebook_pth = r"/home/jovyan/notebooks/SAR_Training/English/HydroSAR/Lab1-ExploreSARTimeSeries.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = 'path = path = f"/home/jovyan/notebooks/SAR_Training/English/HydroSAR/{name}"'
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/hydrosar_data_time_series_example/Bangladesh"
_replacement = f"    path = \"{test_data_path}\""
test.replace_line('path = path = f"/home/jovyan/notebooks/SAR_Training/English/HydroSAR/{name}"', _to_replace, _replacement)

# Erase data directory if already present
try:
   shutil.rmtree(test_data_path)
except:
   pass

# Skip all cells inputing user defined values for filtering products to download
# or those involving conda environment checks
skip_em = ["var kernel = Jupyter.notebook.kernel;",
           "if env[0] != '/home/jovyan/.local/envs/rtc_analysis':"] #This didn't work,
#            "def get_dates_sub(path):",#This didn't work
#            'tiff_paths = f"{path}/tiffsflood/*.tif*"']

for search_str in skip_em:
    test.replace_cell(search_str)
    
# Change cell that calls module into a cell that runs the necessary code. This didn't work
# replace_function_cell = """
# tiff_paths = f"{path}/tiffsflood/*.tif*"
# pths = glob(tiff_paths)
# pths.sort()
# dates = []
# for pth in pths:
#     date = os.path.basename(pth).split('_')[0]
#     date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
#     dates.append(date)
# print(dates)
# """
# test.replace_cell('tiff_paths = f"{path}/tiffsflood/*.tif*"',replace_function_cell)

######### TESTS ###########

# Confirm we are in datadirectoy
test_datadirectory = """
if os.getcwd() == f"{test_data_path}":
    test.log_test('p', f"os.getcwd() == {test_data_path}")
else:
    test.log_test('f', f"os.getcwd() == {os.getcwd()}, NOT {test_data_path}")
"""
test.add_test_cell("os.chdir(path)", test_datadirectory)

# Check that the data was downloaded from the S3 bucket
test_s3_copy = """
if os.path.exists(f"{os.getcwd()}/{time_series}"):
    test.log_test('p', f"{time_series} successfully copied from {time_series_path}")
else:
    test.log_test('f', f"{time_series} NOT copied from {time_series_path}")
"""
test.add_test_cell("!aws --region=us-east-1 --no-sign-request s3 cp $time_series_path $time_series", test_s3_copy)

# Confirm we have extracted 16 tiff files from the tarball
test_extract = """
import glob
test_extracted_path = \"tiffsflood/*.tiff\"
test_len = len(glob.glob(test_extracted_path))
if test_len == 16:
    test.log_test('p', f"{test_len} tiffs extracted from {time_series_path}")
else:
    test.log_test('f', f"Expected 16 tiffs extracted from tarball, found {test_len}")
"""
test.add_test_cell("!tar -xvzf {name}.tar.gz", test_extract)

# Confirm dates hold correct values Cell 19 is giving "EXCEPTION: cell 19, 'module' object is not callable"
test_dates = """
test_dates_1 = ['2020-06-03', '2020-06-12', '2020-06-15', '2020-06-24', '2020-06-27', '2020-07-06', '2020-07-09', '2020-07-12', '2020-07-18', '2020-07-21', '2020-07-24', '2020-07-27', '2020-07-30', '2020-08-02', '2020-08-11', '2020-08-14']
if dates == test_dates:
    test.log_test('p', f"dates == {test_dates_1}")
else:
    test.log_test('f', f"dates == {dates}, NOT {test_dates_1}")
"""
test.add_test_cell("    dates = get_dates_sub(tiff_paths)", test_dates)

# Confirm stackBangladesh_VV.vrt is a vrt, has 16 bands, 3382 pixels, and 3255 lines
test_img = """
test_img_info = gdal.Info(img, format='json')
if test_img_info['driverLongName'] == 'Virtual Raster':
    test.log_test('p', f"img's driverLongName == 'Virtual Raster'")
else:
    test.log_test('f', f"img's driverLongName == {test_img_info['driverLongName']}, NOT 'Virtual Raster'")
if img.RasterCount == 16:
    test.log_test('p', f"img.RasterCount == 16")
else:
    test.log_test('f', f"img.RasterCount {img.RasterCount}, NOT == 16")
if img.RasterXSize == 3382:
    test.log_test('p', f"img.RasterXSize == 3382")
else:
    test.log_test('f', f"img.RasterXSize == {img.RasterXSize}, NOT 3382")
if img.RasterYSize == 3255:
    test.log_test('p', f"img.RasterYSize == 3255")
else:
    test.log_test('f', f"img.RasterYSize == {img.RasterYSize}, NOT 3255")
"""
test.add_test_cell("img = gdal.Open(image_file)", test_img)

## Confirm raster is in dB # Figure out how to do this
#test_caldB = """
#if raster.shape == (16, 600, 600):
#    test.log_test('p', f"raster.shape == (16, 600, 600)")
#else:
#    test.log_test('f', f"raster.shape == {caldB.shape}, NOT (16, 600, 600)")
#"""
#test.add_test_cell("use_dB = True", test_caldB)


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