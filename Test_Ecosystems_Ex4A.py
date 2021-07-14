#!/usr/bin/env python3

from getpass import getpass
import shutil

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

notebook_pth = "/home/jovyan/notebooks/SAR_Training/English/Ecosystems/Exercise4A-SARChangeDetectionMethods.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = "path = \"/home/jovyan/notebooks/SAR_Training/English/Ecosystems/data_Ex2-4_S1-MadreDeDios\""
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/data_Ex2-4_S1-MadreDeDios"
_replacement = f"path = \"{test_data_path}\""
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
if os.path.exists(f"{os.getcwd()}/{time_series}"):
    test.log_test('p', f"{time_series} successfully copied from {time_series_path}")
else:
    test.log_test('f', f"{time_series} NOT copied from {time_series_path}")
"""
test.add_test_cell("!aws --region=us-east-1 --no-sign-request s3 cp $time_series_path $time_series", test_s3_copy)

# Check that 156 tiffs were extracted from the tarball
test_extract = """
import glob
test_tiff_path = f"{os.getcwd()}/tiffs/*.tiff"
test_len = len(glob.glob(test_tiff_path))
if test_len == 156:
    test.log_test('p', f"{test_len} tifs extracted from {time_series}")
else:
    test.log_test('f', f"Expected 156 tifs extracted from tarball, found {test_len}")
"""
test.add_test_cell("asf_unzip(os.getcwd(), time_series)", test_extract)

# Check that raster_stack.vrt was created
test_vv_vrt = """    
if os.path.exists(\"raster_stack.vrt\"):
    test.log_test('p', f"Extracted raster_stack.vrt")
else:
    test.log_test('f', f"raster_stack.vrt not found")    
"""
test.add_test_cell("!gdalbuildvrt -separate raster_stack.vrt", test_vv_vrt)

# Confirm size and type of datetime index 
test_tindex_VH = """
if type(tindex_VH) == pd.core.indexes.datetimes.DatetimeIndex:
    test.log_test('p', f"type(tindex_VH) == {type(tindex_VH)}")
else:
    test.log_test('f', f"type(tindex_VH) == {type(tindex_VH)},  NOT pd.core.indexes.datetimes.DatetimeIndex")
if len(tindex_VH) == 78:
    test.log_test('p', f"len(tindex_VH) == 78")
else:
    test.log_test('f', f"len(tindex_VH) == {len(tindex_VH)},  NOT 78")
"""
test.add_test_cell("tindex_VH = pd.DatetimeIndex(dates_VH)", test_tindex_VH)

# Confirm type and shape of rasterstack_VH
test_rasterstack_VH = """
if type(rasterstack_VH) == np.ndarray:
    test.log_test('p', f"type(rasterstack_VH) == {type(rasterstack_VH)}")
else:
    test.log_test('f', f"type(rasterstack_VH) == {type(rasterstack_VH)},  NOT np.ndarray")
if rasterstack_VH.shape == (78, 1102, 1090):
    test.log_test('p', f"rasterstack_VH.shape) == (78, 1102, 1090)")
else:
    test.log_test('f', f"rasterstack_VH.shape) == {rasterstack_VH.shape},  NOT (78, 1102, 1090)")
"""
test.add_test_cell("rasterstack_VH = img.ReadAsArray()", test_rasterstack_VH)

# Confirm creation of plots_and_animations directory
test_product_path = """
if os.path.exists(f"{path}/{product_path}"):
    test.log_test('p', f"{path}/{product_path} found")
else:
    test.log_test('f', f"{path}/{product_path} NOT found")
"""
test.add_test_cell("product_path = 'plots_and_animations'", test_product_path)

# Confirm the creation of animation_VH.gif
test_animation_VH_gif = """
if os.path.exists(f'{product_path}/animation_VH.gif'):
    test.log_test('p', f"{product_path}/animation_VH.gif found")
else:
    test.log_test('f', f"{product_path}/animation_VH.gif NOT found")
"""
test.add_test_cell("ani.save(f'{product_path}/animation_VH", test_animation_VH_gif)

# Confirm rasterPwr type and shape
test_rasterPwr = """
if type(rasterPwr) == np.ma.core.MaskedArray:
    test.log_test('p', f"type(rasterPwr) == np.ma.core.MaskedArray")
else:
    test.log_test('f', f"type(rasterPwr) == {type(rasterPwr)}, NOT np.ma.core.MaskedArray")
if rasterPwr.shape == (78, 1102, 1090):
    test.log_test('p', f"rasterPwr.shape == (78, 1102, 1090)")
else:
    test.log_test('f', f"rasterPwr.shape == {rasterPwr.shape}, NOT (78, 1102, 1090)")    
"""
test.add_test_cell("rasterPwr = np.ma.array(rasterstack_VH", test_rasterPwr)

# Confirm metric_keys
test_metric_keys = """
if set(metric_keys) == set(['mean', 'max', 'min', 
                            'range','median', 'p5', 'p95', 
                            'prange', 'var', 'cov']):
    test.log_test('p', f"metric_keys == {metric_keys}")
else:
    test.log_test('f', (f"metric_keys == {metric_keys}, NOT"
                       "dict_keys(['mean', 'max', 'min', 'range'"
                        ", 'median', 'p5', 'p95', 'prange', 'var', 'cov'])"))
    
"""
test.add_test_cell("metric_keys = metrics.keys()", test_metric_keys)

# Confirm creation of changes_percentilerange_threshold.png
test_changes_percentilerange_threshold_png = """
if os.path.exists(f"{path}/{product_path}/changes_percentilerange_threshold.png"):
    test.log_test('p', f"{path}/{product_path}/changes_percentilerange_threshold.png found")
else:
    test.log_test('f', f"{path}/{product_path}/changes_percentilerange_threshold.png NOT found")
"""
test.add_test_cell("plt.savefig(f'{product_path}/changes_percentilerange", 
                   test_changes_percentilerange_threshold_png)

# Confirm creation of changes_var_threshold.png
test_changes_var_threshold_png = """
if os.path.exists(f"{path}/{product_path}/changes_var_threshold.png"):
    test.log_test('p', f"{path}/{product_path}/changes_var_threshold.png found")
else:
    test.log_test('f', f"{path}/{product_path}/changes_var_threshold.png NOT found")
"""
test.add_test_cell("plt.savefig(f'{product_path}/changes_var_threshold.png'", 
                   test_changes_var_threshold_png)

# Confirm creation of changes_CV_threshold.png"
test_changes_CV_threshold_png = """
if os.path.exists(f"{path}/{product_path}/changes_CV_threshold.png"):
    test.log_test('p', f"{path}/{product_path}/changes_CV_threshold.png found")
else:
    test.log_test('f', f"{path}/{product_path}/changes_CV_threshold.png NOT found")
"""
test.add_test_cell("plt.savefig(f\"{product_path}/changes_CV_threshold.png\"", 
                   test_changes_CV_threshold_png)

# Confirm shape of tsmean
test_tsmean = """
if tsmean.shape == (78,):
    test.log_test('p', f"tsmean.shape == (78,)")
else:
    test.log_test('f', f"tsmean.shape == {tsmean.shape}, NOT (78,)")
"""
test.add_test_cell("tsmean = 10*np.log10(np.", test_tsmean)

# Confirm ts type and shape
test_ts = """
if type(ts) == pd.core.series.Series:
    test.log_test('p', f"type(ts) == pd.core.series.Series")
else:
    test.log_test('f', f"type(ts) == {type(ts)}, NOT pd.core.series.Series")
if ts.shape == (78,):
    test.log_test('p', f"ts.shape == (78,)")
else:
    test.log_test('f', f"ts.shape == {ts.shape}, NOT (78,)")
"""
test.add_test_cell("ts = pd.Series(tsmean, index=tindex_VH)", test_ts)

# Confirm type and shape of r
test_r = """
if type(r) == np.ma.core.MaskedArray:
    test.log_test('p', f"type(r) == np.ma.core.MaskedArray")
else:
    test.log_test('f', f"type(r) == {type(r)}, NOT np.ma.core.MaskedArray")
if r.shape == (1102, 1090):
    test.log_test('p', f"r.shape == (1102, 1090)")
else:
    test.log_test('f', f"r.shape == {r.shape}, NOT (1102, 1090)")
"""
test.add_test_cell("r = np.log10(cross_pol_new / cross_pol_ref)", test_r)

# Confirm creation of thresh_percentilerange_histogram.png"
test_thresh_percentilerange_histogram_png = """
if os.path.exists(f"{path}/{product_path}/thresh_percentilerange_histogram.png"):
    test.log_test('p', f"{path}/{product_path}/thresh_percentilerange_histogram.png found")
else:
    test.log_test('f', f"{path}/{product_path}/thresh_percentilerange_histogram.png NOT found")
"""
test.add_test_cell("plt.savefig(os.path.join(product_path, 'thresh_", 
                   test_thresh_percentilerange_histogram_png)

# Confirm creation of changes_CV_threshold.png"
test_changes_CV_threshold_png = """
if os.path.exists(f"{path}/{product_path}/changes_CV_threshold.png"):
    test.log_test('p', f"{path}/{product_path}/changes_CV_threshold.png found")
else:
    test.log_test('f', f"{path}/{product_path}/changes_CV_threshold.png NOT found")
"""
test.add_test_cell("plt.savefig(f\"{product_path}/changes_CV_threshold.png\"", 
                   test_changes_CV_threshold_png)

# Check geotrans and proj
test_geotrans_and_proj = """
if geotrans == [375150.0, 30.0, 0.0, 8590230.0, 0.0, -30.0]:
    test.log_test('p', f"geotrans == [375150.0, 30.0, 0.0, 8590230.0, 0.0, -30.0]")
else:
    test.log_test('f', f"geotrans == {geotrans}, NOT [375150.0, 30.0, 0.0, 8590230.0, 0.0, -30.0]")
if type(proj) == str and len(proj) > 8:
    if proj[-8:-3] == '32719':
        test.log_test('p', f"proj[-8:-3] == '32719'")
    else:
        test.log_test('f', f"proj[-8:-3] == {proj[-8:-3]}, NOT '32719'")
else:
    test.log_test('f', f"Invalid projection information: {proj}")
"""
test.add_test_cell("geotrans = list(img.GetGeoTransform())", test_geotrans_and_proj)

# Confirm creation of raster_stack_tsmetrics directory
test_raster_stack_tsmetrics = """
if os.path.exists(f"{path}/raster_stack_tsmetrics"):
    test.log_test('p', f"{path}/raster_stack_tsmetrics found")
else:
    test.log_test('f', f"{path}/raster_stack_tsmetrics NOT found")
"""
test.add_test_cell("dirname = image_file_VH.repl", test_raster_stack_tsmetrics)

# Confirm creation of metrics GeoTiffs
test_metrics_geotiffs = """
for name in names:
    if os.path.exists(f"{path}/{name}"):
        test.log_test('p', f"{path}/{name} found")
    else:
        test.log_test('f', f"{path}/{name} NOT found")
"""
test.add_test_cell("create_geotiff(name, metrics[i],", test_metrics_geotiffs)

# Confirm creation of metrics vrt
test_metric_vrt = """
test_metrics_vrt_info = gdal.Info(f"{dirname}.vrt", format='json')
if test_metrics_vrt_info['driverLongName'] == 'Virtual Raster':
    test.log_test('p', f"{dirname}.vrt is a VRT")
else:
    test.log_test('f', f"{dirname}.vrt is a {test_metrics_vrt_info['driverLongName']}, NOT a VRT")
if len(test_metrics_vrt_info['files']) == 11:
    test.log_test('p', f"{dirname}.vrt contains 11 files")
else:
    test.log_test('f', f"{dirname}.vrt contains {len(test_metrics_vrt_info['files'])} files, NOT 11")
"""
test.add_test_cell("cmd = 'gdalbuildvrt -separate -overwrite -vrtnodata nan", test_metric_vrt)

    
# Confirm creation of GeoTiffs from 4 change detection attempts
test_final_geotiffs = """
test_geotiffs = [imagenamepdiff, imagenamevar, imagenamecov, imagenamelr]
for tiff in test_geotiffs:
    test_tiff_info = gdal.Info(tiff, format='json')
    if test_tiff_info['driverLongName'] == 'GeoTIFF':
        test.log_test('p', f"{tiff} is a GeoTIFF")
    else:
        test.log_test('p', f"{tiff} is NOT a GeoTIFF")
    if test_tiff_info['coordinateSystem']['wkt'][-7:-2] == '32719':
        test.log_test('p', f"{tiff} EPSG == '32719'")
    else:
        test.log_test('f', f"{tiff} EPSG == {repr(test_tiff_info['coordinateSystem']['wkt'][-7:-2])}, NOT '32719'")
"""
test.add_test_cell("create_geotiff(imagenamepdiff,", test_final_geotiffs)
       
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
    
