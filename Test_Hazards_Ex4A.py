#!/usr/bin/env python3

from getpass import getpass
import shutil
import glob
import os

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = "/home/jovyan/notebooks/SAR_Training/English/Hazards/Exercise4A-SARChangeDetectionMethods.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = "path = Path(f'/home/jovyan/notebooks/SAR_Training/English/Hazards/{name}')"
_replacement = "path = Path(f'/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/hazards_test_Ex4A')"
test.replace_line(_to_replace, _to_replace, _replacement)

# Erase data directory if already present
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/hazards_test_Ex4A"
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
test_tiff_qty = len(glob.glob(f"{path}/tiffsfuego/*.tif"))
if test_tiff_qty == 60:
    test.log_test('p', f"60 tiffs extracted, as expected")
else:
    test.log_test('f', f"{test_tiff_qty} tiffs extracted, NOT 60")
if Path(f"{path}/stackfuego_VV.vrt").exists():
    test.log_test('p', f"{path}/stackfuego_VV.vrt found")
else:
    test.log_test('f', f"{path}/stackfuego_VV.vrt NOT found")
if Path(f"{path}/datesfuego_VV.csv").exists():
    test.log_test('p', f"{path}/datesfuego_VV.csv found")
else:
    test.log_test('f', f"{path()}/datesfuego_VV.csv NOT found")

if Path(f"{path}/stackfuego_VH.vrt").exists():
    test.log_test('p', f"{path}/stackfuego_VH.vrt found")
else:
    test.log_test('f', f"{path}/stackfuego_VH.vrt NOT found")
if Path(f"{path}/datesfuego_VH.csv").exists():
    test.log_test('p', f"{path}/datesfuego_VH.csv found")
else:
    test.log_test('f', f"{path}/datesfuego_VH.csv NOT found")
"""
test.add_test_cell("!tar -xvzf {time_series} -C {path}", test_tarball_extraction)

# Confirm creation of dtype and size of tindex
test_tindex = """
if tindex.size == 30:
    test.log_test('p', f"tindex.size == 30")
else:
    test.log_test('f', f"tindex.size == {tindex.size}, NOT 30")
if tindex.dtype == 'datetime64[ns]':
    test.log_test('p', f"tindex.dtype == 'datetime64[ns]'")
else:
    test.log_test('p', f"tindex.dtype == {repr(tindex.dtype)}, NOT 'datetime64[ns]'")
"""
test.add_test_cell("tindex = pd.DatetimeIndex(o", test_tindex)
    
# Confirm rasterstack type and shape
test_rasterstack = """
if type(rasterstack) == np.ndarray:
    test.log_test('p', f"type(rasterstack) == np.ndarray")
else:
    test.log_test('f', f"type(rasterstack) == {type(rasterstack)}, NOT np.ndarray")
if rasterstack.shape == (30, 475, 544):
    test.log_test('p', f"rasterstack.shape == (30, 475, 544)")
else:
    test.log_test('f', f"rasterstack.shape == {rasterstack.shape}, NOT (30, 475, 544)")
"""
test.add_test_cell("rasterstack = img.ReadAsArray()", test_rasterstack)

# Confirm creation of plots_and_animations directory
test_product_path = """
if Path(f"{product_path}").exists():
    test.log_test('p', f"{product_path} found")
else:
    test.log_test('f', f"{product_path} NOT found")
"""
test.add_test_cell("product_path = path/'plots_and_animations'", test_product_path)

# Confirm creation of time series animation
test_ts_animation = """
if Path(f"{product_path}/animation_{labeldB}.gif").exists():
    test.log_test('p', f"{product_path}/animation_{labeldB}.gif found")
else:
    test.log_test('f', f"{product_path}/animation_{labeldB}.gif NOT found")
"""
test.add_test_cell("ani.save(product_path/f'animation_{labeldB}.gif', writer='pillow', fps=2)", test_ts_animation)

# Confirm metric_keys

test_metrics_keys = """
if set(metrics.keys()) == {'mean', 'p95', 'max', 'var', 
                           'min', 'std', 'median', 'p5', 
                           'prange', 'range', 'CV'}:
    test.log_test('p', f"set(metrics.keys()) == {set(metrics.keys())}")
else:
    test.log_test('f', (f"set(metrics.keys()) == {set(metrics.keys())}, NOT"
                       " {'mean', 'p95', 'max', 'var', 'min', 'std'"
                        ", 'median', 'p5', 'prange', 'range', 'CV'}"))
    
"""
test.add_test_cell("metrics.keys()", test_metrics_keys)

# Confirm creation of prange histogram
test_prange_histogram = """
if os.path.exists(os.path.join(product_path, f'prange_{labeldB}_histogram.png')):
    test.log_test('p', f"{os.path.join(product_path, f'prange_{labeldB}_histogram.png')} found")
else:
    test.log_test('f', f"{os.path.join(product_path, f'prange_{labeldB}_histogram.png')} NOT found")
"""
test.add_test_cell("plot_histogram_cdf(metric='prange')", test_prange_histogram)

# Confirm creation of changes_prange_dB.png
test_changes_prange_db_png = """
if os.path.exists(f"{product_path}/changes_prange_dB.png"):
    test.log_test('p', f"{product_path}/changes_prange_dB.png found")
else:
    test.log_test('f', f"{product_path}/changes_prange_dB.png NOT found")
"""
test.add_test_cell("metric = 'prange'", test_changes_prange_db_png)

# Confirm creation of std_dB_histogram.png
test_std_dB_histogram_png = """ 
if os.path.exists(f"{product_path}/std_dB_histogram.png"):
    test.log_test('p', f"{product_path}/std_dB_histogram.png found")
else:
    test.log_test('f', f"{product_path}/std_dB_histogram.png NOT found")
"""
test.add_test_cell("plot_histogram_cdf(metric='std')", test_std_dB_histogram_png)

# Confirm creation of changes_std_dB.png
test_changes_std_dB_png = """ 
if os.path.exists(f"{product_path}/changes_std_dB.png"):
    test.log_test('p', f"{product_path}/changes_std_dB.png found")
else:
    test.log_test('f', f"{product_path}/changes_std_dB.png NOT found")
"""
test.add_test_cell("masks[metric] = plot_threshold_classifier(metric=metric)", test_changes_std_dB_png)

# Confirm creation of CV_dB_histogram.png
test_CV_dB_histogram_png = """ 
if os.path.exists(f"{product_path}/CV_dB_histogram.png"):
    test.log_test('p', f"{product_path}/CV_dB_histogram.png found")
else:
    test.log_test('f', f"{product_path}/CV_dB_histogram.png NOT found")
"""
test.add_test_cell("plot_histogram_cdf(metric='CV')", test_CV_dB_histogram_png)

# Confirm creation of logratio_2018-05-27_2018-05-27.png
test_logratio_png = """ 
if os.path.exists(os.path.join(product_path, f'{logratiolabel}.png')):
    test.log_test('p', f"{os.path.join(product_path, f'{logratiolabel}.png')} found")
else:
    test.log_test('f', f"{os.path.join(product_path, f'{logratiolabel}.png')} NOT found")
"""
test.add_test_cell("plt.savefig(product_path/f'{logratiolabel}.png',", test_logratio_png)

# Confirm geotrans == [724170.0, 30.0, 0.0, 1602960.0, 0.0, -30.0]
test_geotrans = """
if geotrans == [724170.0, 30.0, 0.0, 1602960.0, 0.0, -30.0]:
    test.log_test('p', f"geotrans == [724170.0, 30.0, 0.0, 1602960.0, 0.0, -30.0], as expected")
else:
    test.log_test('f', f"geotrans == {geotrans}, not [724170.0, 30.0, 0.0, 1602960.0, 0.0, -30.0]")
"""
test.add_test_cell("geotrans = list(img.GetGeoTransform())", test_geotrans)

# Confirm creation of fuego_tsmetrics directory
test_tsmetrics_dir = """
if Path(f"{path}/fuego_tsmetrics"):
    test.log_test('p', "fuego_tsmetrics directory found")
else:
    test.log_test('f', "fuego_tsmetrics directory NOT found")
"""
test.add_test_cell("dirname = path/f'{name}_tsmetrics'", test_tsmetrics_dir)


# Confirm creation of metric geotiffs
test_metric_geotiffs = """
for metric in metrics:
    name_ = os.path.join(dirname, f'{metric}_{labeldB}.tif')
    if os.path.exists(name_):
        test.log_test('p', f"{name_} found")
    else:
        test.log_test('f', f"{name_} NOT found")
"""
test.add_test_cell("fnmetric = str(dirname/f'{name}_{labeldB}_{metric}_thresholds.tif')", test_metric_geotiffs)

# Confirm creation of ts_metrics_dB.vrt
test_ts_metrics_dB_vrt = """
if Path(f"{dirname}_{labeldB}.vrt").exists():
    test.log_test('p', f"{dirname}_{labeldB}.vrt found")
else:
    test.log_test('f', f"{dirname}_{labeldB}.vrt NOT found")
"""
test.add_test_cell("cmd='gdalbuildvrt -separate -overwrite -vrtnodata", test_ts_metrics_dB_vrt)

# Confirm creation of geotiffs based on 4 change detection threshold masks
test_threshold_tifs = """
for metric in masks:
    fnmetric = os.path.join(dirname, f'{name}_{labeldB}_{metric}_thresholds.tif')
    if Path(fnmetric).exists():
        test.log_test('p', f"{fnmetric} found")
    else:
        test.log_test('f', f"{fnmetric} NOT found")
"""
test.add_test_cell("fnmetric = str(dirname/f'{name}_{labeldB}_{metric}_thresholds.tif')", test_threshold_tifs)

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
    
    

