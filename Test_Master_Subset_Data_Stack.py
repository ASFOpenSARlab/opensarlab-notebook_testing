#!/usr/bin/env python3

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io
from pathlib import Path
import shutil

import opensarlab_lib as asfn
import os

# from pip._internal import main as pipmain
# pipmain(['install', 'astor'])

######### INITIAL SETUP #########

## If the test script fails, look for extra spaces in the notebook at the end of the line for the last magic !

# Define path to notebook and create ASFNotebookTest object
notebook_pth = "/home/jovyan/notebooks/SAR_Training/English/Master/Subset_Data_Stack.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Skip all cells inputing user defined values for filtering products to download
# or those involving conda environment checks
skip_em = ["notebookUrl = url_w.URLWidget()",
           "if env[0] != '/home/jovyan/.local/envs/rtc_analysis':",
           "option = asfn.select_parameter([option_key[1], option_key[2] , option_key[3],], '')",
           "display(Markdown(f'<text style=color:red>NOTE: As of now, your WKT/shapefile will work if it meets following conditions: </text>'))",
           "raise OSError('Directory that contains your .tif files are empty.')",
           "raise TypeError(f'{infile} is not a valid path.')",
           "# Gets EPSG from your infile",
           'print("Would you like to remove all instances of previous/unused shapely files?")',
           "if choice == 2 and shp_option.value == 'Yes':",
           "shp_name = input('Choose a name for your shapefly file: ')",
           "# Let user input WKT (option 2)",
           "display(Markdown(f'<text style=color:red>IT MAY CAUSE AN UNEXPECTED RESULTS.</text>'))",
           "shp = Path(shpfc.selected)",
           "# Extract wkt from shapefile:",
           "print('Items from previous run exists. Would you like to keep them or remove them to generate new items?')",
           "print('Cleaning previously generated subset file(s)...')",
           "# Display cropped image & place cropped image on top on original image.",
           "raise MemoryError('Subset file too big and will crash. Please regenerate your subset image using correct values.')",
           "# Run this cell to display links"]

for search_str in skip_em:
    test.replace_cell(search_str)

# Make a data directory for testing
test_replace_analysis_dir = '''
analysis_dir = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack"
try:
   shutil.rmtree(analysis_dir)
except:
   pass
analysis_dir = path = Path("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack")
analysis_dir.mkdir()
zip_path = analysis_dir/"jamalpur_stack_testing.zip"
'''
test.replace_cell("display(fc)", test_replace_analysis_dir)

test_replace_options = '''
choice = 1
'''
test.replace_cell('choice = option_key.index(option.value)', test_replace_options)

# Download the data
test_download = "!aws --region=us-east-1 --no-sign-request s3 cp s3://asf-jupyter-data/notebook_testing_data/jamalpur_stack_testing.zip /home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/jamalpur_stack_testing.zip"
test.replace_line('tiff_dir = Path(fc.selected_path)', 'tiff_dir = Path(fc.selected_path)', test_download)

# Unzip the data
test_unzip ='asfn.asf_unzip("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack", "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/jamalpur_stack_testing.zip")'
test.replace_line('analysis_dir = tiff_dir.parent','analysis_dir = tiff_dir.parent', test_unzip)

# Establish paths to tiffs line1
test_paths1 = 'tiff_dir = analysis_dir/"tiffs"'
test.replace_line('print(f"analysis_dir: {analysis_dir}")', 'print(f"analysis_dir: {analysis_dir}")', test_paths1)

# Establish paths to tiffs line2
test_paths2 = 'paths = tiff_dir/"*.tif"'
test.replace_line('paths = tiff_dir/"*.tif*"', 'paths = tiff_dir/"*.tif*"', test_paths2)

# hardcode AOI coordinates
test_set_coords = '''
try:
    aoi.x1 = 3056.2403225806447
    aoi.x2 = 4636.833870967743
    aoi.y1 = 3677.6806451612906
    aoi.y2 = 4780.803225806452
    aoi_coords = [xy_to_geocoord(aoi.x1, aoi.y1, geotrans, latlon=False), xy_to_geocoord(aoi.x2, aoi.y2, geotrans, latlon=False)]
    print(f"aoi_coords in EPSG {utm}: {aoi_coords}")
except TypeError:
    print('TypeError')
'''
test.replace_cell("aoi_coords = [xy_to_geocoord(aoi.x1, aoi.y1, geotrans, latlon=False), xy_to_geocoord(aoi.x2, aoi.y2, geotrans, latlon=False)]", test_set_coords)

# Define subset directory
test_sub_name = '    sub_name = "subset"'
test.replace_line('    sub_name = input()', '    sub_name = input()', test_sub_name)

# Make sure we're getting the correct tiff paths here
correct_tiff_paths = '''
paths = analysis_dir/"tiffs/*.tif"
tiff_paths = get_tiff_paths(paths)
for p in tiff_paths:
    print(p)
'''
test.replace_cell('print(p)', correct_tiff_paths)

# Skip file clean up widget cells
test.replace_cell("cleanup = asfn.select_parameter(")
test.replace_cell("if cleanup.value ==")


######### TESTS ###########

# Confirm utm == '32646'
test_utm = '''
if utm == '32646':
    test.log_test('p', f"utm == '32646'")
else:
    test.log_test('f', f"utm == {utm}, NOT '32646'")
'''
test.add_test_cell("utm = info.split('ID')[-1].split(',')[1][0:-2]", test_utm)


# Confirm tiff_paths contains expected paths
test_tiff_paths = '''
test_tiff_pths = "[PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170530T120429_DVP_RTC30_G_gpuned_1BC3_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170611T120430_DVP_RTC30_G_gpuned_110E_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170623T120431_DVP_RTC30_G_gpuned_F322_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170705T120431_DVP_RTC30_G_gpuned_E078_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170717T120432_DVP_RTC30_G_gpuned_4B27_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170729T120433_DVP_RTC30_G_gpuned_6F19_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170810T120434_DVP_RTC30_G_gpuned_D26B_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170822T120434_DVP_RTC30_G_gpuned_6C6E_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170903T120435_DVP_RTC30_G_gpuned_08BD_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170915T120435_DVP_RTC30_G_gpuned_C402_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170927T120435_DVP_RTC30_G_gpuned_ACF8_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20171009T120436_DVP_RTC30_G_gpuned_616C_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20171021T120436_DVP_RTC30_G_gpuned_C4E5_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20171102T120436_DVP_RTC30_G_gpuned_1F2B_VH.tif'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20171114T120435_DVP_RTC30_G_gpuned_093B_VH.tif')]"
if str(tiff_paths) == test_tiff_pths:
    test.log_test('p', f"tiff_paths == {test_tiff_pths}")
else:
    test.log_test('f', f"tiff_paths == {tiff_paths}, NOT {test_tiff_pths}")
'''
test.add_test_cell('to_merge = {}', test_tiff_paths)


# Confirm merge_paths contains expected path/s
# Note: merge_paths starts with a space
test_merge_paths = '''
test_merge_pths = " /home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/tiffs/S1A_IW_20170530T120429_DVP_RTC30_G_gpuned_1BC3_VH.tif"
if merge_paths == test_merge_pths:
    test.log_test('p', f"merge_paths == {test_merge_pths}")
else:
    test.log_test('f', f"merge_paths == {merge_paths}, NOT {test_merge_pths}")
'''
test.add_test_cell("if str_coords not in to_merge:", test_merge_paths)


# Confirm full_scene tiff file type and band, line, and pixel size
test_full_scene = '''
full_scene = str(full_scene)
test_full_scene_info = gdal.Info(full_scene, format='json')
if test_full_scene_info['driverLongName'] == 'GeoTIFF':
    test.log_test('p', f"full_scene driverLongName == 'GeoTIFF'")
else:
    test.log_test('f', f"full_scene driverLongName == {test_full_scene_info['driverLongName']}, NOT 'GeoTIFF'")
test_full_scene_file = gdal.Open(full_scene)
if test_full_scene_file.RasterCount == 1:
    test.log_test('p', f"full_scene has 1 band")
else:
    test.log_test('f', f"full_scene has {test_full_scene_file.RasterCount} band/s, NOT 1")
if test_full_scene_file.RasterXSize == 9570:
    test.log_test('p', f"full_scene has 9570 pixels")
else:
    test.log_test('f', f"full_scene has {test_full_scene_file.RasterXSize} pixels, NOT 9570")
if test_full_scene_file.RasterYSize == 7060:
    test.log_test('p', f"full_scene has 7060 lines")
else:
    test.log_test('f', f"full_scene has {test_full_scene_file.RasterYSize} lines, NOT 7060")
'''
test.add_test_cell('gdal_command = f"gdal_merge.py -o {full_scene} {merge_paths}"', test_full_scene)


# Confirm raster_stack.vrt file type, band, line, and pixel size, and rasterstack.shape
test_full_scene = '''
test_img_info = gdal.Info(img, format='json')
if test_img_info['driverLongName'] == 'Virtual Raster':
    test.log_test('p', f"img driverLongName == 'Virtual Raster'")
else:
    test.log_test('f', f"img driverLongName == {test_img_info['driverLongName']}, NOT 'Virtual Raster'")
if img.RasterCount == 1:
    test.log_test('p', f"img has 1 band")
else:
    test.log_test('f', f"img has {img.RasterCount} band/s, NOT 1")
if img.RasterXSize == 9570:
    test.log_test('p', f"img has 9570 pixels")
else:
    test.log_test('f', f"img has {img.RasterXSize} pixels, NOT 9570")
if img.RasterYSize == 7060:
    test.log_test('p', f"img has 7060 lines")
else:
    test.log_test('f', f"img has {img.RasterYSize} lines, NOT 7060")
if rasterstack.shape == (7060, 9570):
    test.log_test('p', f"rasterstack.shape == (7060, 9570)")
else:
    test.log_test('f', f"rasterstack.shape == {rasterstack.shape}, NOT (7060, 9570)")
'''
test.add_test_cell('img = gdal.Open(image_file)', test_full_scene)


# Confirm geotrans == (74760.0, 30.0, 0.0, 2841660.0, 0.0, -30.0)
test_geotrans = '''
if geotrans == (74760.0, 30.0, 0.0, 2841660.0, 0.0, -30.0):
    test.log_test('p', f"geotrans == (74760.0, 30.0, 0.0, 2841660.0, 0.0, -30.0)")
else:
    test.log_test('f', f"geotrans == {geotrans}, NOT (74760.0, 30.0, 0.0, 2841660.0, 0.0, -30.0)")
'''
test.add_test_cell("geotrans = img.GetGeoTransform()", test_geotrans)


# Confirm aoi_coords == [[166447.20967741933, 2731329.580645161], [213865.01612903227, 2698235.9032258065]]
test_aoi_coords = '''
if aoi_coords == [[166447.20967741933, 2731329.580645161], [213865.01612903227, 2698235.9032258065]]:
    test.log_test('p', f"aoi_coords == [[166447.20967741933, 2731329.580645161], [213865.01612903227, 2698235.9032258065]]")
else:
    test.log_test('f', f"aoi_coords == {aoi_coords}, NOT [[166447.20967741933, 2731329.580645161], [213865.01612903227, 2698235.9032258065]]")
'''
test.add_test_cell("aoi_coords = [xy_to_geocoord(aoi.x1, aoi.y1, geotrans, latlon=False), xy_to_geocoord(aoi.x2, aoi.y2, geotrans, latlon=False)]", test_aoi_coords)


# Confirm creation of subset_dir
test_subset_dir = '''
if Path("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset").exists():
    test.log_test('p', "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset found")
else:
    test.log_test('f', "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset NOT found")
'''
test.add_test_cell('if not subset_dir.exists():', test_subset_dir)


# Confirm updated tiff_paths contain subset tiffs
test_subset_tiff_paths = '''
test_subset_tiff_pths = "[PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170530_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170611_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170623_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170705_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170717_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170729_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170810_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170822_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170903_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170915_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20170927_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20171009_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20171021_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20171102_VH.tiff'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/master_data_Test_Subset_Data_Stack/subset/20171114_VH.tiff')]"
if str(tiff_paths) == test_subset_tiff_pths:
    test.log_test('p', f"tiff_paths == {test_subset_tiff_pths}")
else:
    test.log_test('f', f"tiff_paths == {tiff_paths}, NOT {test_subset_tiff_pths}")
'''
test.add_test_cell("tiff_paths = get_tiff_paths(subset_paths)", test_subset_tiff_paths)


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
    