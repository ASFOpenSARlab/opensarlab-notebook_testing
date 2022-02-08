#!/usr/bin/env python3

from getpass import getpass
import shutil
import glob

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io

######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = ("/home/jovyan/notebooks/SAR_Training/English/Ecosystems/"
       "Exercise3-ExploreSARTimeSeriesDeforestation.ipynb")
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = 'path = Path("/home/jovyan/notebooks/SAR_Training/English/Ecosystems/data_Ex2-4_S1-MadreDeDios")'
_replacement = 'path = Path("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/data_Ex2-4_S1-MadreDeDios")'
test.replace_line(_to_replace, _to_replace, _replacement)

# Erase data directory if already present
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/data_Ex2-4_S1-MadreDeDios"
try:
   shutil.rmtree(test_date_path)
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
_replacement = "sarloc = (1029, 949)"
test.replace_line(_to_replace, _to_replace, _replacement)

######### TESTS ###########

# Check that the data was downloaded from the S3 bucket
test_s3_copy = """
if Path(f"{time_series}").exists():
    test.log_test('p', f"{time_series} successfully copied from {time_series_path}")
else:
    test.log_test('f', f"{time_series} NOT copied from {time_series_path}")
"""
test.add_test_cell("!aws --region=us-east-1 --no-sign-request s3 cp $time_series_path $time_series", test_s3_copy)

# Confirm that all expected tiffs were extracted from the zip
test_zip_extraction = """
test_tiff_qty = len(glob.glob(str(path/"tiffs/*.*")))
if test_tiff_qty == 156:
    test.log_test('p', f"156 tiffs extracted, as expected")
else:
    test.log_test('f', f"{test_tiff_qty} tiffs extracted, NOT 156")
"""
test.add_test_cell("asfn.asf_unzip(str(path), time_series)", test_zip_extraction)

# Confirm the creation of VV and VH vrts and that they contain 79 files each
test_vrts = """
test_vv_vrt_info = gdal.Info(str(image_file_VV), format='json')
if test_vv_vrt_info['driverLongName'] == 'Virtual Raster':
    test.log_test('p', f"image_file_VV's driverLongName == 'Virtual Raster'")
else:
    test.log_test('f', (f"image_file_VV's driverLongName == "
                   f"{test_vv_vrt_info['driverLongName']}, NOT 'Virtual Raster'"))
if len(test_vv_vrt_info['files']) == 79:
    test.log_test('p', f"image_file_VV contains 79 files")
else:
    test.log_test('f', f"image_file_VV contains {len(test_vv_vrt_info['files'])} files, NOT 79")
             
test_vh_vrt_info = gdal.Info(str(image_file_VH), format='json')            
if test_vh_vrt_info['driverLongName'] == 'Virtual Raster':
    test.log_test('p', f"image_file_VH's driverLongName == 'Virtual Raster'")
else:
    test.log_test('f', (f"image_file_VH's driverLongName == "
                   f"{test_vh_vrt_info['driverLongName']}, NOT 'Virtual Raster'"))
if len(test_vh_vrt_info['files']) == 79:
    test.log_test('p', f"image_file_VH contains 79 files")
else:
    test.log_test('f', f"image_file_VH contains {len(test_vh_vrt_info['files'])} files, NOT 79")
"""
test.add_test_cell('image_file_VV = path/"raster_stack.vrt"', test_vrts)

# Check creation and size of VV and VH pandas.DatetimeIndex
test_vv_vh_datetimeindexes = """
if type(tindex_VV) == pd.core.indexes.datetimes.DatetimeIndex:
    test.log_test('p', f"type(tindex_VV) == pd.core.indexes.datetimes.DatetimeIndex")
else:
    test.log_test('f', (f"type(tindex_VV) == {type(tindex_VV)}, "
                        f"NOT pd.core.indexes.datetimes.DatetimeIndex"))
if len(tindex_VV) == 78:
    test.log_test('p', f"len(tindex_VV) == 78")
else:
    test.log_test('f', f"len(tindex_VV) == {len(tindex_VV)}, NOT 78")
if type(tindex_VH) == pd.core.indexes.datetimes.DatetimeIndex:
    test.log_test('p', f"type(tindex_VH) == pd.core.indexes.datetimes.DatetimeIndex")
else:
    test.log_test('f', (f"type(tindex_VH) == {type(tindex_VH)}, "
                        f"NOT pd.core.indexes.datetimes.DatetimeIndex"))
if len(tindex_VH) == 78:
    test.log_test('p', f"len(tindex_VH) == 78")
else:
    test.log_test('f', f"len(tindex_VH) == {len(tindex_VH)}, NOT 78")
"""
test.add_test_cell("tindex_VV = pd.DatetimeIndex(dates_VV)", test_vv_vh_datetimeindexes)

# Confirm rasterstack_VV.shape == (78, 1102, 1090)
test_rasterstack_VV = """
if rasterstack_VV.shape == (78, 1102, 1090):
    test.log_test('p', f"rasterstack_VV.shape == (78, 1102, 1090)")
else:
    test.log_test('f', f"rasterstack_VV.shape ==  {rasterstack_VV.shape}, NOT (78, 1102, 1090)")
"""
test.add_test_cell("rasterstack_VV = img.ReadAsArray()", test_rasterstack_VV)

# Confirm db_mean.shape == (1102, 1090)
test_db_mean = """
if db_mean.shape == (1102, 1090):
    test.log_test('p', f"db_mean.shape == (1102, 1090)")
else:
    test.log_test('f', f"db_mean.shape == {db_mean.shape}, NOT (1102, 1090)")
"""
test.add_test_cell("db_mean = np.min(rasterstack_VV, axis=0)", test_db_mean)

# Check xsize, ysize, geotrans, bands, and projection for image_file_VV and image_file_VH
test_size_geotrans_bands_proj = """
if xsize == [1090, 1090]:
    test.log_test('p', f"xsize == [1090, 1090]")
else:
    test.log_test('f', f"xsize == {xsize}, NOT [1090, 1090]")
if ysize == [1102, 1102]:
    test.log_test('p', f"ysize == [1102, 1102]")
else:
    test.log_test('f', f"ysize == {ysize}, NOT [1102, 1102]")
if geotrans == [(375150.0, 30.0, 0.0, 8590230.0, 0.0, -30.0), 
               (375150.0, 30.0, 0.0, 8590230.0, 0.0, -30.0)]:
    test.log_test('p', f"geotrans == {geotrans}")
else:
    test.log_test('f', (f"geotrans == {geotrans}, NOT "
                        "[(375150.0, 30.0, 0.0, 8590230.0, 0.0, -30.0), "
                        "(375150.0, 30.0, 0.0, 8590230.0, 0.0, -30.0)]"))
if bands == [78, 78]:
    test.log_test('p', f"bands == [78, 78]")
else:
    test.log_test('f', f"bands == {bands}, NOT [78, 78]")
if proj[0][-8:-3] == '32719':
    test.log_test('p', f"image_file_VV projection == '32719'")
else:
    test.log_test('f', f"image_file_VV projection == {repr(proj[0][-8:-3])}, NOT '32719'")
if proj[1][-8:-3] == '32719':
    test.log_test('p', f"image_file_VH projection == '32719'")
else:
    test.log_test('f', f"image_file_VH projection == {repr(proj[1][-8:-3])}, NOT '32719'")
"""
test.add_test_cell("proj.append(img_handle[-1].GetP", test_size_geotrans_bands_proj)

# Check ref_x and ref_y values
test_ref_x_ref_y = """
if ref_x == 406020.0:
    test.log_test('p', f"ref_x == 406020.0")
else:
    test.log_test('f', f"ref_x == {ref_x}, NOT 406020.0")
if ref_y == 8561760.0:
    test.log_test('p', f"ref_y == 8561760.0")
else:
    test.log_test('f', f"ref_y == {ref_y}, NOT 8561760.0")
"""
test.add_test_cell("ref_y = geotrans[0][3]", test_ref_x_ref_y)

# Confirm s_ts is a list of pandas.core.series.Series objects of dtype float64 and length 78
test_s_ts = """
for i, _test_ts in enumerate(s_ts):
    if type(_test_ts) == pd.core.series.Series:
        test.log_test('p', f"type(s_ts[i]) == pd.core.series.Series")
    else:
        test.log_test('f', f"type(s_ts[i]) == {type(_test_ts)}, NOT pd.core.series.Series")
    if _test_ts.size == 78:
        test.log_test('p', f"s_ts[i].size == 78")
    else:
        test.log_test('f', f"s_ts[i].size == {_test_ts.size}, NOT 78")
    if _test_ts.dtype == 'float64':
        test.log_test('p', f"s_ts[i].dtype == 'float64'")
    else:
        test.log_test('f', f"s_ts[i].dtype == {repr(_test_ts.dtype)}, NOT 'float64'")
"""
test.add_test_cell("s_ts.append(pd.Series(means", test_s_ts)

# Confirm creation of plots_and_animations directory
test_product_path = """
if Path(f"{product_path}").exists():
    test.log_test('p', f"{product_path} found")
else:
    test.log_test('f', f"{product_path} NOT found")
"""
test.add_test_cell("product_path = path/'plots_and_animations'", test_product_path)

# Confirm creation of time series backscatter histogram png
test_histogram = """
if Path(f"{product_path}/{figname}").exists():
    test.log_test('p', f"{product_path}/{figname} found")
else:
    test.log_test('f', f"{product_path}/{figname} NOT found")
"""
test.add_test_cell('figname = f"RCSTimeSeries-{ref_x:.0f}_{ref_y:.0f}.png"', test_histogram)

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