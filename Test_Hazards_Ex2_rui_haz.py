#!/usr/bin/env python3

import shutil
import glob
from getpass import getpass
from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = ("/home/jovyan/notebooks/SAR_Training/English/Hazards/"
       "Exercise2-RGBandMetricsVisualization.ipynb")
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = 'path = Path("/home/jovyan/notebooks/SAR_Training/English/Hazards/data_Ex2-4_S1-MadreDeDios")'
_replacement = 'path = Path("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/hazards_test_Ex2_S1-MadreDeDios")'
test.replace_line(_to_replace, _to_replace, _replacement)

# Fix bad date format that only happens when running the test script
_to_replace = "!ls {path}/tiffs/*_VV.tiff | sort | sed 's/[^0-9]*//g' | cut -c 4-11 > {path}/raster_stack_VV.dates"
_replacement = "!ls {path}/tiffs/*_VV.tiff | sort | sed 's/[^0-9]*//g' | cut -c 3-10 > {path}/raster_stack_VV.dates"
test.replace_line(_to_replace, _to_replace, _replacement)

# Fix bad date format that only happens when running the test script
_to_replace = "!ls {path}/tiffs/*_VH.tiff | sort | sed 's/[^0-9]*//g' | cut -c 4-11 > {path}/raster_stack_VH.dates"
_replacement = "!ls {path}/tiffs/*_VH.tiff | sort | sed 's/[^0-9]*//g' | cut -c 3-10 > {path}/raster_stack_VH.dates"
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
if Path(f"{time_series}").exists():
    test.log_test('p', f"{time_series} successfully copied from {time_series_path}")
else:
    test.log_test('f', f"{time_series} NOT copied from {time_series_path}")
"""
test.add_test_cell("!aws --region=us-east-1 --no-sign-request s3 cp $time_series_path $time_series", test_s3_copy)

# Check that 156 tiffs were extracted from the tarball
test_extract = """
test_tiff_path = (f"{path}/tiffs/*.tiff")
test_len = len(glob.glob(str(test_tiff_path)))
if test_len == 156:
    test.log_test('p', f"{test_len} tifs extracted from {time_series}")
else:
    test.log_test('f', f"Expected 156 tifs extracted from tarball, found {test_len}")
"""
test.add_test_cell("asfn.asf_unzip(str(path), time_series)", test_extract)

# Check that raster_stack.vrt was created
test_vv_vrt = """    
if Path(f"{path}/raster_stack.vrt").exists():
    test.log_test('p', f"Extracted raster_stack.vrt")
else:
    test.log_test('f', f"raster_stack.vrt not found")    
"""
test.add_test_cell("!gdalbuildvrt -separate {path}/raster_stack.vrt {path}/tiffs/*_VV.tiff", test_vv_vrt)

# Check that raster_stack_VV.dates was created
test_vv_dates = """
if Path(f"{path}/raster_stack_VV.dates").exists():
    test.log_test('p', f"Extracted raster_stack_VV.dates")
else:
    test.log_test('f', f"raster_stack_VV.dates not found")
"""
test.add_test_cell("tindex_VV = pd.DatetimeIndex(dates_VV)", test_vv_dates)

# Confirm that vrt was opened by gdal successfully
test_open_vrt = """
if type(img) == gdal.Dataset:
    test.log_test('p', f"type(img) == gdal.Dataset")
else:
    test.log_test('f', f"type(img) == {type(img)}, not gdal.Dataset")
"""
test.add_test_cell("img = gdal.Open(str(image_file_VV))", test_open_vrt)

# Confirm that raster0 is a numpy.ndarray with shape (1102, 1090)
test_raster0 = """
if type(raster0) == np.ndarray:
    test.log_test('p', f"type(raster0) == np.ndarray")
else:
    test.log_test('f', f"type(raster0) == {type(raster0)}, not np.ndarray")
if raster0.shape == (1102, 1090):
    test.log_test('p', f"raster0.shape == (1102, 1090)")
else:
    test.log_test('f', f"raster0.shape == {raster0.shape}, not (1102, 1090)")
"""
test.add_test_cell("raster0 = band.ReadAsArray()", test_raster0)

# Confirm that rasterstack_VV is a numpy.ndarray with shape (78, 1102, 1090)
test_rasterstack_VV = """
if type(rasterstack_VV) == np.ndarray:
    test.log_test('p', f"type(rasterstack_VV) == np.ndarray")
else:
    test.log_test('f', f"type(rasterstack_VV) == {type(rasterstack_VV)}, not np.ndarray")
if rasterstack_VV.shape == (78, 1102, 1090):
    test.log_test('p', f"rasterstack_VV.shape == (78, 1102, 1090)")
else:
    test.log_test('f', f"rasterstack_VV.shape == {rasterstack_VV.shape}, not (78, 1102, 1090)")
"""
test.add_test_cell("raster0 = band.ReadAsArray()", test_rasterstack_VV)

# Confirm that a time series animation was created and stored at product_path
test_animation_created = """
if Path(f"{product_path}/animation.gif").exists():
    test.log_test('p', f"{product_path}/animation.gif found")
else:
    test.log_test('f', f"{product_path}/animation.gif NOT found")
"""
test.add_test_cell("ani.save(product_path/'animation.gif', writer='pillow', fps=2)", test_animation_created)

# Confirm the creation of a numpy.ma.core.MaskedArray with shape (78, 1102, 1090)
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
test.add_test_cell("rasterPwr = np.ma.array(rasterstack_VV,", test_rasterPwr)

# Confirm data structure types and shapes involved in creating rgb stack
test_rgb_stack = """
import datetime
if type(rgb_bands) == tuple:
    test.log_test('p', f"type(rgb_bands) == tuple")
else:
    test.log_test('f', f"type(rgb_bands) == {type(rgb_bands)}, not tuple")
if rgb_bands == (1, 39, 78):
    test.log_test('p', f"rgb_bands == (1, 39, 78)")
else:
    test.log_test('f', f"rgb_bands == {rgb_bands}, NOT (1, 39, 78)")
if type(rgb_idx) == np.ndarray:
    test.log_test('p', f"type(rgb_idx) == np.ndarray")
else:
    test.log_test('f', f"type(rgb_idx) == {type(rgb_idx)}, not np.ndarray")
if rgb_idx.shape == (3, ):
    test.log_test('p', f"rgb_idx.shape == (3, )")
else:
    test.log_test('f', f"rgb_idx.shape == {rgb_idx.shape}, NOT (3, )")
if type(rgb) == np.ma.core.MaskedArray:
    test.log_test('p', f"type(rgb) == np.ma.core.MaskedArray")
else:
    test.log_test('f', f"type(rgb) == {type(rgb)}, NOT np.ma.core.MaskedArray")
if rgb.shape == (1102, 1090, 3):
    test.log_test('p', f"rgb.shape == (1102, 1090, 3)")
else:
    test.log_test('f', f"rgb.shape == {rgb.shape}, NOT (1102, 1090, 3)")
if type(rgb_dates) == tuple:
    test.log_test('p', f"type(rgb_dates) == tuple")
else:
    test.log_test('f', f"type(rgb_dates) == {type(rgb_dates)}, NOT tuple")
if type(rgb_dates[0]) == datetime.date:
    test.log_test('p', f"type(rgb_dates[0]) == datetime.date")
else:
    test.log_test('f', f"type(rgb_dates[0]) == {type(rgb_dates[0])}, NOT datetime.date")   
"""
test.add_test_cell("rgb = np.dstack((rasterPwr[rgb_idx[0]]", test_rgb_stack)

# Confirm rgb_stretched.shape == (1102, 1090, 3)
test_rgb_stretched = """
if rgb_stretched.shape == (1102, 1090, 3):
    test.log_test('p', f"rgb_stretched.shape == (1102, 1090, 3)")
else:
    test.log_test('f', f"rgb_stretched.shape == {rgb_stretched.shape}, NOT(1102, 1090, 3)")
"""
test.add_test_cell("for i in range(rgb_stretched.shape[2]):", test_rgb_stretched)

# Confirm coords == [[375150.0, 8590230.0], [407850.0, 8557170.0]]
test_coords = """
if coords == [[375150.0, 8590230.0], [407850.0, 8557170.0]]:
    test.log_test('p', f"coords == [[375150.0, 8590230.0], [407850.0, 8557170.0]]")
else:
    test.log_test('f', f"coords == {coords}, NOT [[375150.0, 8590230.0], [407850.0, 8557170.0]]")
"""
test.add_test_cell("coords = [vrt_info['cornerCoordinates']['upperLeft'],", test_coords)

# Confirm utm_zone = 32719
test_utm_zone = """
if utm_zone == '32719':
    test.log_test('p', f"utm_zone = '32719'")
else:
    test.log_test('f', f"utm_zone = {repr(utm_zone)}, NOT '32719'")
"""
test.add_test_cell("utm_zone = vrt_info['coordinateSystem']['wkt'].s", test_utm_zone)

# Confirm that rgb_stretched was converted to a geotiff, projected to the correct utm, and stored in product_path
test_MadreDeDios_multitemp_RGB_geotiff = """
if Path(f"{product_path}/MadreDeDios-multitemp-RGB.tiff").exists():
    test.log_test('p', f"{product_path}/MadreDeDios-multitemp-RGB.tiff found")    
else:
    test.log_test('f', f"{product_path}/MadreDeDios-multitemp-RGB.tiff NOT found")
test_rgb_geotiff_info = gdal.Info(f"{product_path}/MadreDeDios-multitemp-RGB.tiff", format='json')
if test_rgb_geotiff_info['driverLongName'] == 'GeoTIFF':
    test.log_test('p', f"{product_path}/MadreDeDios-multitemp-RGB.tiff is a GeoTIFF")    
else:
    test.log_test('f', f"{product_path}/MadreDeDios-multitemp-RGB.tiff is NOT a GeoTIFF")
test_utm = test_rgb_geotiff_info['coordinateSystem']['wkt'].split('ID[\"EPSG\",')[8][:-2]
if test_utm == utm_zone:
    test.log_test('p', f"MadreDeDios-multitemp-RGB.tiff utm == {utm_zone}")    
else:
    test.log_test('f', f"MadreDeDios-multitemp-RGB.tiff utm == {test_utm}, NOT {utm_zone}")
"""
test.add_test_cell("geotiff_from_plot(rgb_stretched, product_path/'MadreDeDios-multitemp-RGB', coords, utm_zone)", test_MadreDeDios_multitemp_RGB_geotiff)

# Confirm that raster_stack_VH.vrt was created, is projected to the correct utm, and saved to the analysis directory
test_raster_stack_VH = """
if Path(f"{path}/raster_stack_VH.vrt").exists():
    test.log_test('p', f"{path}/raster_stack_VH.vrt found")    
else:
    test.log_test('f', f"{path}/raster_stack_VH.vrt NOT found")
test_raster_stack_VH_info = gdal.Info(str(image_file_VH), format='json')
if test_raster_stack_VH_info['driverLongName'] == 'Virtual Raster':
    test.log_test('p', f"{path}/raster_stack_VH.vrt is a VRT")    
else:
    test.log_test('f', f"{path}/raster_stack_VH.vrt is NOT a VRT")
test_utm = test_raster_stack_VH_info['coordinateSystem']['wkt'].split('ID[\"EPSG\",')[8][:-2]
if test_utm == utm_zone:
    test.log_test('p', f"test_raster_stack_VH_info utm == {utm_zone}")    
else:
    test.log_test('f', f"test_raster_stack_VH_info utm == {test_utm}, NOT {utm_zone}")
"""
test.add_test_cell("!gdalbuildvrt -separate {path}/raster_stack_VH.vrt {path}/tiffs/*_VH.tiff", test_raster_stack_VH)

# Confirm that tindex_VH pandas DateTimeIndex created and has length 78
test_tindex_VH = """
if type(tindex_VH) == pd.core.indexes.datetimes.DatetimeIndex:
    test.log_test('p', f"type(tindex_VH) == pd.core.indexes.datetimes.DatetimeIndex")    
else:
    test.log_test('f', f"type(tindex_VH) == {type(tindex_VH)}, NOT pd.core.indexes.datetimes.DatetimeIndex")
if len(tindex_VH) == 78:
    test.log_test('p', f"len(tindex_VH) == 78")    
else:
    test.log_test('f', f"len(tindex_VH) == {len(tindex_VH)}, NOT 78")   
"""
test.add_test_cell("tindex_VH = pd.DatetimeIndex(dates_VH)", test_tindex_VH)

# Confirm rasterPwr is a numpy.ma.core.MaskedArray of length 78
test_rasterPwr = """
if type(rasterPwr) == np.ma.core.MaskedArray:
    test.log_test('p', f"type(rasterPwr) == np.ma.core.MaskedArray")    
else:
    test.log_test('f', f"type(rasterPwr) == {type(rasterPwr)}, NOT np.ma.core.MaskedArray") 
if len(rasterPwr) == 78:
    test.log_test('p', f"len(rasterPwr) == 78")    
else:
    test.log_test('f', f"len(rasterPwr) == {len(rasterPwr)}, NOT 78")   
"""
test.add_test_cell("rasterPwr_VH = np.ma.array(rasterstack_VH", test_rasterPwr)

# Confirm rgb_stretched_POL is a numpy.ma.core.MaskedArray of length 1102
test_rgb_stretched_POL = """
if type(rgb_stretched_POL) == np.ma.core.MaskedArray:
    test.log_test('p', f"type(rgb_stretched_POL) == np.ma.core.MaskedArray")    
else:
    test.log_test('f', f"type(rgb_stretched_POL) == {type(rgb_stretched_POL)}, NOT np.ma.core.MaskedArray") 
if len(rgb_stretched_POL) == 1102:
    test.log_test('p', f"len(rgb_stretched_POL) == 1102")    
else:
    test.log_test('f', f"len(rgb_stretched_POL) == {len(rgb_stretched_POL)}, NOT 1102")   
"""
test.add_test_cell("rgb_stretched_POL[:,:,i] = exposure.", test_rgb_stretched_POL)

# Confirm that rgb_stretched_POL was converted to a geotiff, projected to the correct utm, and stored in product_path
test_MadreDeDios_multipol_RGB_geotiff = """
if Path(f"{product_path}/MadreDeDios-multipol-RGB.tiff").exists():
    test.log_test('p', f"{product_path}/MadreDeDios-multipol-RGB.tiff found")    
else:
    test.log_test('f', f"{product_path}/MadreDeDios-multipol-RGB.tiff NOT found")
test_rgb_geotiff_info = gdal.Info(f"{product_path}/MadreDeDios-multipol-RGB.tiff", format='json')
if test_rgb_geotiff_info['driverLongName'] == 'GeoTIFF':
    test.log_test('p', f"{product_path}/MadreDeDios-multipol-RGB.tiff is a GeoTIFF")    
else:
    test.log_test('f', f"{product_path}/MadreDeDios-multipol-RGB.tiff is NOT a GeoTIFF")
test_utm = test_rgb_geotiff_info['coordinateSystem']['wkt'].split('ID[\"EPSG\",')[8][:-2]
if test_utm == utm_zone:
    test.log_test('p', f"MadreDeDios-multipol-RGB.tiff utm == {utm_zone}")    
else:
    test.log_test('f', f"MadreDeDios-multipol-RGB.tiff utm == {test_utm}, NOT {utm_zone}")
"""
test.add_test_cell("geotiff_from_plot(rgb_stretched_POL,", test_MadreDeDios_multipol_RGB_geotiff)

# Confirm rs_means_pwr_VH and rs_means_pwr_VV are numpy.ma.core.MaskedArrays of length 78
test_rs_means_pwr = """
if type(rs_means_pwr_VH) == np.ma.core.MaskedArray:
    test.log_test('p', f"type(rs_means_pwr_VH) == np.ma.core.MaskedArray")    
else:
    test.log_test('f', f"type(rs_means_pwr_VH) == {type(rs_means_pwr_VH)}, NOT np.ma.core.MaskedArray") 
if len(rs_means_pwr_VH) == 78:
    test.log_test('p', f"len(rs_means_pwr_VH) == 78")    
else:
    test.log_test('f', f"len(rs_means_pwr_VH) == {len(rs_means_pwr_VH)}, NOT 78")   
if type(rs_means_pwr_VV) == np.ma.core.MaskedArray:
    test.log_test('p', f"type(rs_means_pwr_VV) == np.ma.core.MaskedArray")    
else:
    test.log_test('f', f"type(rs_means_pwr_VV) == {type(rs_means_pwr_VV)}, NOT np.ma.core.MaskedArray") 
if len(rs_means_pwr_VV) == 78:
    test.log_test('p', f"len(rs_means_pwr_VV) == 78")    
else:
    test.log_test('f', f"len(rs_means_pwr_VV) == {len(rs_means_pwr_VV)}, NOT 78")   
"""
test.add_test_cell("rs_means_pwr_VH = np.mean(ra", test_rs_means_pwr)

# Confirm expected metrics keys and np.ndarray lengths
test_metrics = """
if metric_keys == ['mean', 'max', 'min', 'range', 'median', 'p5', 'p95', 'prange', 'var', 'CV']:
    test.log_test('p', f"metric_keys == {metric_keys}")    
else:
    test.log_test('f', f"metric_keys == {metric_keys}, NOT ['mean', 'max', 'min', 'range', 'median', 'p5', 'p95', 'prange', 'var', 'CV']")
for key in metrics:
    if len(metrics[key]) == 1102:
        test.log_test('p', f"len(metrics['{key}'] == 1102")
    else:
        test.log_test('f', f"len(metrics['{key}'] == {len(metrics[key])}, NOT 1102")
"""
test.add_test_cell("metric_keys = list(metrics.keys())", test_metrics)

# Confirm Geotiff creation from each metric
test_metric_geotiffs = """
for key in metrics:
    if Path(f"{product_path}/MadreDeDios-{key}.tiff").exists():
        test.log_test('p', f"{path}/{product_path}/MadreDeDios-{key}.tiff found") 
    else:
        test.log_test('f', f"{product_path}/MadreDeDios-{key}.tiff NOT found")
    test_metric_geotiff_info = gdal.Info(f"{product_path}/MadreDeDios-{key}.tiff", format='json')
    if test_metric_geotiff_info['driverLongName'] == 'GeoTIFF':
        test.log_test('p', f"{product_path}/MadreDeDios-{key}.tiff is a GeoTIFF")    
    else:
        test.log_test('f', f"{product_path}/MadreDeDios-{key}.tiff is NOT a GeoTIFF")
    test_utm = test_metric_geotiff_info['coordinateSystem']['wkt'].split('ID[\"EPSG\",')[8][:-2]
    if test_utm == utm_zone:
        test.log_test('p', f"MadreDeDios-{key}.tiff utm == {utm_zone}")    
    else:
        test.log_test('f', f"MadreDeDios-{key}.tiff utm == {test_utm}, NOT {utm_zone}")
"""
test.add_test_cell("geotiff_from_plot(metrics[i],", test_metric_geotiffs)



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
    