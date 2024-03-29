#!/usr/bin/env python3

from getpass import getpass
import shutil
import numpy
import glob

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io

######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = ("/home/jovyan/notebooks/SAR_Training/English/Hazards/"
       "Exercise3A-ExploreSARTimeSeriesFlood.ipynb")
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = "path = Path(f'/home/jovyan/notebooks/SAR_Training/English/Hazards/{name}')"
_replacement = "path = Path(f'/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/hazards_test_Ex3_flood')"
test.replace_line(_to_replace, _to_replace, _replacement)

# Erase data directory if already present
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/hazards_test_Ex3_flood"
try:
   shutil.rmtree(test_data_path)
except:
   pass

# Skip all cells inputing user defined values for filtering products to download
# or those involving conda environment checks
skip_em = ["notebookUrl = url_w.URLWidget()",
           "if env[0] != '/home/jovyan/.local/envs/rtc_analysis':"]

for search_str in skip_em:
    test.replace_cell(search_str)

# Replace manually input coords from matplotlib plot with hardcoded test coords
_to_replace = "sarloc = (ceil(my_plot.x), ceil(my_plot.y))"
_replacement = "sarloc = (456, 892)"
test.replace_line(_to_replace, _to_replace, _replacement)

# Replace manually input coords from matplotlib plot with hardcoded test coords
_to_replace = "flevent = 2      # Options: 1 - Guayaquil flood of 2016-2017   |    2 - 2020 Bangladesh & Eastern India Event"
_replacement = "flevent = 1      # Options: 1 - Guayaquil flood of 2016-2017   |    2 - 2020 Bangladesh & Eastern India Event"
test.replace_line(_to_replace, _to_replace, _replacement)

######### TESTS ###########

# Check that the data was downloaded from the S3 bucket
test_s3_copy = """
if Path(f"{time_series}").exists():
    test.log_test('p', f"{time_series} successfully copied from {time_series_path}")
else:
    test.log_test('f', f"{time_series} NOT copied from {time_series_path}")
"""
test.add_test_cell("!aws --region=us-west-2 --no-sign-request s3 cp $time_series_path $time_series", test_s3_copy)

# Confirm that all expected tiffs were extracted from the tarball
test_tarball_extraction = """
test_tiff_qty = len(glob.glob(f"{path}/tiffsflood/*.tif"))
if test_tiff_qty == 17:
    test.log_test('p', f"17 tiffs extracted, as expected") 
else:
    test.log_test('f', f"{test_tiff_qty} tiffs extracted, NOT 17")
if Path(f"{path}/stackflood_VV.vrt").exists():
    test.log_test('p', f"{path}/stackflood_VV.vrt found")
else:
    test.log_test('f', f"{path}/stackflood_VV.vrt NOT found")
if Path(f"{path}/datesflood_VV.csv").exists():
    test.log_test('p', f"{path}/datesflood_VV.csv found")
else:
    test.log_test('f', f"{path}/datesflood_VV.csv NOT found")
"""
test.add_test_cell("!tar -xvzf {time_series} -C {path}", test_tarball_extraction)

# Confirm len(dates) == 17
test_dates = """
if len(dates) == 17:
    test.log_test('p', f"len(dates) == 17")
else:
    test.log_test('f', f"len(dates) == {len(dates)}, NOT 17")
"""
test.add_test_cell("else get_dates_sub(path, 'tiffsflood/*.tif*')", test_dates)

# Confirm rasterstack type and shape
test_rasterstack = """
if type(rasterstack) == np.ndarray:
    test.log_test('p', f"type(rasterstack) == np.ndarray")
else:
    test.log_test('f', f"type(rasterstack) == {type(rasterstack)}, NOT np.ndarray")
if rasterstack.shape == (17, 1033, 1483):
    test.log_test('p', f"rasterstack.shape == (17, 1033, 1483)")
else:
    test.log_test('f', f"rasterstack.shape == {rasterstack.shape}, NOT (17, 1033, 1483)")
"""
test.add_test_cell("rasterstack = img.ReadAsArray()", test_rasterstack)

# Confirm temporal min type and shape
test_temporal_min = """
if type(temporal_min) == numpy.ma.core.MaskedArray:
    test.log_test('p', f"type(temporal_min) == <class 'numpy.ma.core.MaskedArray'>")
else:
    test.log_test('f', f"type(temporal_min) == {type(temporal_min)}, NOT <class 'numpy.ma.core.MaskedArray'>")
if temporal_min.shape == (1033, 1483):
    test.log_test('p', f"temporal_min.shape == (1033, 1483)")
else:
    test.log_test('f', f"temporal_min.shape == {temporal_min.shape}, NOT (1033, 1483)")
"""
test.add_test_cell("temporal_min = np.nanmin(convert", test_temporal_min)

# Check geotrans, xsize, ysiz, bands, and projstring
test_img_stats = """
if geotrans == (639030.0, 30.0, 0.0, 9823110.0, 0.0, -30.0):
    test.log_test('p', f"geotrans == (639030.0, 30.0, 0.0, 9823110.0, 0.0, -30.0)")
else:
    test.log_test('f', f"geotrans == {geotrans}, NOT (639030.0, 30.0, 0.0, 9823110.0, 0.0, -30.0)")
if xsize == 1483:
    test.log_test('p', f"xsize == 1483")
else:
    test.log_test('f', f"xsize == {xsize}, NOT 1483")
if ysize == 1033:
    test.log_test('p', f"ysize == 1033")
else:
    test.log_test('f', f"ysize == {ysize}, NOT 1033")
if bands == 17:
    test.log_test('p', f"bands == 16")
else:
    test.log_test('f', f"bands == {bands}, NOT 16")
if projstring == '32717':
    test.log_test('p', f"projstring == '32717'")
else:
    test.log_test('f', f"projstring == {repr(projstring)}, NOT '32717'")
"""
test.add_test_cell("geotrans = img_handle.GetGeoTransform()", test_img_stats)
    
# Confirm creation of RCSTimeSeries--1.842° -79.627°.png
test_rcstimeseries_png = """
if Path(f"{path}/{figname}").exists():
    test.log_test('p', f"{figname} found")
else:
    test.log_test('f', f"{figname} NOT found")
"""
test.add_test_cell("plt.savefig(path/figname, dpi=300, transparent='true')", test_rcstimeseries_png)


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