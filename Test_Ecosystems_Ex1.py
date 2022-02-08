#!/usr/bin/env python3

from getpass import getpass
import shutil
import glob
import os

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

notebook_pth = r"/home/jovyan/notebooks/SAR_Training/English/Ecosystems/Exercise1-ExploreSARTimeSeries_Example.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = 'path = Path("/home/jovyan/notebooks/SAR_Training/English/Ecosystems/data_time_series_example")'
_test_data_path = 'path = Path("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/data_time_series_example")'
test.replace_line(_to_replace, _to_replace, _test_data_path)

# Erase data directory if already present
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/data_time_series_example"
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
if Path(f"{time_series_path}").exists():
    test.log_test('p', f"{time_series_path} successfully copied from {s3_path}")
else:
    test.log_test('f', f"{time_series_path} NOT copied from {s3_path}")
"""
test.add_test_cell("!aws --region=us-east-1 --no-sign-request s3 cp $s3_path $time_series_path", test_s3_copy)

# Confirm we have extracted 828 files from the zip
test_extract = """
test_zip_extract_length = 0
for _, _, test_filenames in os.walk(str(path/"time_series")):
    test_zip_extract_length += len(test_filenames)
if test_zip_extract_length == 828:
    test.log_test('p', f"828 files were extracted from the zip")
else:
    test.log_test('f', f"{test_zip_extract_length} files were extracted from the zip, NOT 828")              
"""
test.add_test_cell("asfn.asf_unzip(str(path), time_series_path)", test_extract)

# Confirm we are in datadirectoy
test_datadirectory = """
if Path(f"{datadirectory}").exists():
    test.log_test('p', f"{datadirectory} Exists")
else:
    test.log_test('f', f"{datadirectory} does NOT Exist")
"""
test.add_test_cell("# !ls {datadirectory}/*vrt #Uncomment this line to see a List of the files", test_datadirectory)

# Confirm tindex has dtype = datetime64[ns], freq = None, and length = 70
test_tindex = """
if tindex.dtype == 'datetime64[ns]':
    test.log_test('p', f"tindex.dtype == 'datetime64[ns]'")
else:
    test.log_test('f', f"tindex.dtype == {repr(tindex.dtype)}, NOT 'datetime64[ns]'")
if tindex.freq == None:
    test.log_test('p', f"tindex.freq == None")
else:
    test.log_test('f', f"tindex.freq == {tindex.freq}, NOT None")
if len(tindex) == 70:
    test.log_test('p', f"len(tindex) == 70")
else:
    test.log_test('f', f"len(tindex) == {len(tindex)}, NOT 70")    
"""
test.add_test_cell("tindex = pd.DatetimeIndex(dates)", test_tindex)

# Confirm S32644X696260Y3052060sS1_D_vv_0092_mtfil.vrt is a vrt, has 70 bands, 1547 pixels, and 1270 lines
test_img = """
test_img_info = gdal.Info(img, format='json')
if test_img_info['driverLongName'] == 'Virtual Raster':
    test.log_test('p', f"img's driverLongName == 'Virtual Raster'")
else:
    test.log_test('f', f"img's driverLongName == {test_img_info['driverLongName']}, NOT 'Virtual Raster'")
if img.RasterCount == 70:
    test.log_test('p', f"img.RasterCount == 70")
else:
    test.log_test('f', f"img.RasterCount {img.RasterCount}, NOT == 70")
if img.RasterXSize == 1547:
    test.log_test('p', f"img.RasterXSize == 1547")
else:
    test.log_test('f', f"img.RasterXSize == {img.RasterXSize}, NOT 1547")
if img.RasterYSize == 1270:
    test.log_test('p', f"img.RasterYSize == 1270")
else:
    test.log_test('f', f"img.RasterYSize == {img.RasterYSize}, NOT 1270")
"""
test.add_test_cell("img = gdal.Open(str(imagefile))", test_img)

# Confirm caldB.shape == (70, 600, 600)
test_caldB = """
if caldB.shape == (70, 600, 600):
    test.log_test('p', f"caldB.shape == (70, 600, 600)")
else:
    test.log_test('f', f"caldB.shape == {caldB.shape}, NOT (70, 600, 600)")
"""
test.add_test_cell("caldB = 20*np.log10(rasterstack) - 83", test_caldB)

# Confirm calPwr.shape and calAmp.shape == (70, 600, 600)
test_calPwr_calAmp = """
if calPwr.shape == (70, 600, 600):
    test.log_test('p', f"calPwr.shape == (70, 600, 600)")
else:
    test.log_test('f', f"calPwr.shape == {calPwr.shape}, NOT (70, 600, 600)")
if calAmp.shape == (70, 600, 600):
    test.log_test('p', f"calAmp.shape == (70, 600, 600)")
else:
    test.log_test('f', f"calAmp.shape == {calAmp.shape}, NOT (70, 600, 600)")
"""
test.add_test_cell("calAmp = np.sqrt(calPwr)", test_calPwr_calAmp)

# Confirm S32644X696260Y3052060sS1_D_vh_0092_mtfil.vrt is a vrt, has 38 bands, 1547 pixels, and 1270 lines
test_img_cross = """
test_img_cross_info = gdal.Info(img_cross, format='json')
if test_img_cross_info['driverLongName'] == 'Virtual Raster':
    test.log_test('p', f"img_cross's driverLongName == 'Virtual Raster'")
else:
    test.log_test('f', f"img_cross's driverLongName == {test_img_cross_info['driverLongName']}, NOT 'Virtual Raster'")
if img_cross.RasterCount == 38:
    test.log_test('p', f"img_cross.RasterCount == 38")
else:
    test.log_test('f', f"img_cross.RasterCount {img_cross.RasterCount}, NOT == 38")
if img_cross.RasterXSize == 1547:
    test.log_test('p', f"img_cross.RasterXSize == 1547")
else:
    test.log_test('f', f"img_cross.RasterXSize == {img_cross.RasterXSize}, NOT 1547")
if img_cross.RasterYSize == 1270:
    test.log_test('p', f"img_cross.RasterYSize == 1270")
else:
    test.log_test('f', f"img_cross.RasterYSize == {img_cross.RasterYSize}, NOT 1270")
"""
test.add_test_cell("img_cross = gdal.Open(str(imagefile_cross))", test_img_cross)

# Confirm creation of product_path
test_product_path = """ 
if Path(f"{product_path}").exists():
    test.log_test('p', f"{product_path} found")
else:
    test.log_test('f', f"{product_path} NOT found")
"""
test.add_test_cell("product_path = path/'plots_and_animations'", test_product_path)

# Confirm creation of animation.gif
test_animation = """
if Path(f"{product_path}/animation.gif").exists():
    test.log_test('p', f"{product_path}/animation.gif found")
else:
    test.log_test('f', f"{product_path}/animation.gif NOT found")
"""
test.add_test_cell("ani.save(product_path/'animation.gif', writer='pillow', fps=2)", test_animation)

# Confirm rs_means_pwr.shape == (70,)
test_rs_means_pwr = """
if rs_means_pwr.shape == (70,):
    test.log_test('p', f"rs_means_pwr.shape == (70,)")
else:
    test.log_test('f', f"rs_means_pwr.shape == {rs_means_pwr.shape}, NOT (70,)")
"""
test.add_test_cell("rs_means_pwr.shape", test_rs_means_pwr)

# Confirm creation of time_series_means
test_time_series_means = """ 
if Path(f"{product_path}/time_series_means.png").exists():
    test.log_test('p', f"{product_path}/time_series_means.png found")
else:
    test.log_test('f', f"{product_path}/time_series_means.png NOT found")
"""
test.add_test_cell("plt.savefig(product_path/'time_series_means', dpi=72, transparent='true')", test_time_series_means)
                   
# Confirm creation of animation_histogram.gif
test_animation_histogram = """ 
if Path(f"{product_path}/animation_histogram.gif").exists():
    test.log_test('p', f"{product_path}/animation_histogram.gif found")
else:
    test.log_test('f', f"{product_path}/animation_histogram.gif NOT found")
"""
test.add_test_cell("ani.save(product_path/'animation_histogram.gif', writer='pillow', fps=2)", test_animation_histogram)
                   

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
    