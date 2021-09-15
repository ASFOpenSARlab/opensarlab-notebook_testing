#!/usr/bin/env python3

from getpass import getpass
import shutil

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io
from asf_notebook import asf_unzip
from pathlib import Path
import os


######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = r"/home/jovyan/notebooks/ASF/GEOS_657_Labs/2019/GEOS 657-Lab9-InSARTimeSeriesAnalysis-Part1-DataDownload-HyP3_v2.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Define data path for testing
_replacement = """
analysis_directory = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data" 
if os.path.exists(analysis_directory):
    contents = glob.glob(f'{analysis_directory}/*')
    if len(contents) > 0:
        shutil.rmtree(analysis_directory)
        os.mkdir(analysis_directory)
else:
    os.mkdir(analysis_directory)
"""
test.replace_cell("while True:", _replacement)

# Skip all cells inputing user defined values for filtering products to download
# or those involving conda environment checks
skip_em = ["var kernel = Jupyter.notebook.kernel;",
           "if env[0] != '/home/jovyan/.local/envs/train':",
           "hyp3 = HyP3(prompt=True)",
           "projects = asfn.get_RTC_projects(hyp3)",
           "date_picker = asfn.gui_date_picker(dates)",
           "project = asfn.filter_jobs_by_date(jobs, date_range)",
           "project = asfn.get_paths_orbits(project)",
           "aoi = asfn.AOI_Selector(rasterstack, fig_xsize, fig_ysize)",
           "def write_dot_netrc(path, username, password):", #remove later so this cell runs
           "!$train_path/aps_weather_model.py -g {georef_path} 0 0", #remove later so this cell runs
           "!$train_path/aps_weather_model.py -g {georef_path} 1 1", #remove later so this cell runs
           "!$train_path/aps_weather_model.py -g {georef_path} 2 2", #remove later so this cell runs
           "!$train_path/aps_weather_model.py -g {georef_path} 3 3", #remove later so this cell runs
           "bin_paths.sort()", #remove later so this cell runs
           "for p in bin_paths:", #remove later so this cell runs
           "!$train_path/aps_weather_model.py -g {georef_path} 4 4", #remove later so this cell runs
           "fig = plt.figure(figsize=(18, 10))", #remove later so this cell runs
           "difference = np.subtract(im_c, im_u)", #remove later so this cell runs
           'print(f"original coordiante system = EPSG:{predominant_utm}")', #remove later so this cell runs
           'paths = f"{corrected_folder}/*.tif"', #remove later so this cell runs
           "for file in tiff_paths:", #remove later so this cell runs
           "pixels_lines = get_pixels_lines(tiff_paths)", #remove later so this cell runs
           "pickle.dump(to_pickle, outfile)" #remove later so this cell runs
           ]

for search_str in skip_em:
    test.replace_cell(search_str)
    
# Download the Hyp3 project data from S3 bucket
_to_replace = "direction_choice = asfn.select_parameter(orbit_directions, 'Direction:')"
replacement = "!aws --region=us-east-1 --no-sign-request s3 cp s3://asf-jupyter-data/notebook_testing/GEOS657_Lab9_2019_part1.zip /home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/GEOS657_Lab9_2019_part1.zip"
#replacement = ""
test.replace_cell(_to_replace, replacement)

# Unzip the downloaded project
test_unzip = '''
asf_unzip("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams", "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/GEOS657_Lab9_2019_part1.zip")
zip_dir = f"{analysis_directory}/ingrams"
os.chdir(zip_dir)
dirpath = Path.cwd()
zip_files = dirpath.glob("*.zip")
zip_paths = list(zip_files)
zip_paths.sort()
back_dir = f"{analysis_directory}"
os.chdir(back_dir)
'''
test.replace_cell("project = asfn.filter_jobs_by_orbit(project, direction)", test_unzip)

# Unzip the individual HyP3 products
_to_replace = "project_zips = jobs.download_files(ingram_folder)"
_replacement = "project_zips = zip_paths"
test.replace_line(_to_replace, _to_replace, _replacement)

# Replace the cell using the ! and bash commands within the function to get tiff paths
_to_replace = 'def get_tiff_paths(paths):'
_replacement = '''
def get_tiff_paths(paths):
    tiff_paths = glob.glob(paths)
    return tiff_paths

def print_tiff_paths(tiff_paths):
    print("Tiff paths:", tiff_paths)
'''
test.replace_cell(_to_replace, _replacement)

# Replace manually input coords from matplotlib plot with hardcoded test coords
_to_replace = "    aoi_coords = [geolocation(aoi.x1, aoi.y1, geotrans, latlon=False), geolocation(aoi.x2, aoi.y2, geotrans, latlon=False)]"
_replacement = "    aoi_coords = [geolocation(823.2718776795205, 1267.4977990512953, geotrans, latlon=False), geolocation(1885.9620005837792, 2669.4504964038615, geotrans, latlon=False)]"
test.replace_line(_to_replace, _to_replace, _replacement)

######### TESTS ###########

# Check that the data was downloaded from the S3 bucket
_to_replace = "direction_choice = asfn.select_parameter(orbit_directions, 'Direction:')"
test_s3_copy = '''
if os.path.exists("/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/GEOS657_Lab9_2019_part1.zip"):
    test.log_test("p", "GEOS657_Lab9_2019_part1.zip successfully copied from s3://asf-jupyter-data/notebook_testing/GEOS657_Lab9_2019_part1.zip")
else:
    test.log_test("f", "GEOS657_Lab9_2019_part1.zip NOT copied from s3://asf-jupyter-data/notebook_testing/GEOS657_Lab9_2019_part1.zip")
'''
test.add_test_cell(_to_replace, test_s3_copy)

# Confirm zip_paths contains expected paths
test_zip_paths = '''
test_zip_pths = "[PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20190408T141243_20210103T141256_VVP636_INT80_G_ueF_0DD4.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20190526T141245_20210103T141256_VVP588_INT80_G_ueF_25B7.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20190725T141249_20210103T141256_VVP528_INT80_G_ueF_9805.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20191122T141252_20210103T141256_VVP408_INT80_G_ueF_50ED.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20191216T141251_20210103T141256_VVP384_INT80_G_ueF_04BE.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20200202T141249_20210103T141256_VVP336_INT80_G_ueF_2668.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20200321T141249_20210103T141256_VVP288_INT80_G_ueF_F2E0.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20200508T141251_20210103T141256_VVP240_INT80_G_ueF_2F16.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20200613T141253_20210103T141256_VVP204_INT80_G_ueF_DE52.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20200707T141254_20210103T141256_VVP180_INT80_G_ueF_E339.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20200812T141256_20210103T141256_VVP144_INT80_G_ueF_6FC6.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20201011T141258_20210103T141256_VVP084_INT80_G_ueF_1BC5.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20201104T141258_20210103T141256_VVP060_INT80_G_ueF_EA59.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20201128T141258_20210103T141256_VVP036_INT80_G_ueF_D855.zip'), PosixPath('/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/GEOS_657_2019_lab_9_data/ingrams/S1BB_20201222T141257_20210103T141256_VVP012_INT80_G_ueF_A80C.zip')]"
if str(zip_paths) == test_zip_pths:
    test.log_test('p', f"zip_paths == {test_zip_pths}")
else:
    test.log_test('f', f"zip_paths == {zip_paths}, NOT {test_zip_pths}")
'''
test.add_test_cell("project = asfn.filter_jobs_by_orbit(project, direction)", test_zip_paths)

# Confirm initial paths to amplitude files
test_amp_paths =''' 
test_amp_pths ="['ingrams/S1BB_20200613T141253_20210103T141256_VVP204_INT80_G_ueF_DE52/S1BB_20200613T141253_20210103T141256_VVP204_INT80_G_ueF_DE52_amp.tif', 'ingrams/S1BB_20201222T141257_20210103T141256_VVP012_INT80_G_ueF_A80C/S1BB_20201222T141257_20210103T141256_VVP012_INT80_G_ueF_A80C_amp.tif', 'ingrams/S1BB_20200707T141254_20210103T141256_VVP180_INT80_G_ueF_E339/S1BB_20200707T141254_20210103T141256_VVP180_INT80_G_ueF_E339_amp.tif', 'ingrams/S1BB_20190526T141245_20210103T141256_VVP588_INT80_G_ueF_25B7/S1BB_20190526T141245_20210103T141256_VVP588_INT80_G_ueF_25B7_amp.tif', 'ingrams/S1BB_20191216T141251_20210103T141256_VVP384_INT80_G_ueF_04BE/S1BB_20191216T141251_20210103T141256_VVP384_INT80_G_ueF_04BE_amp.tif', 'ingrams/S1BB_20201128T141258_20210103T141256_VVP036_INT80_G_ueF_D855/S1BB_20201128T141258_20210103T141256_VVP036_INT80_G_ueF_D855_amp.tif', 'ingrams/S1BB_20200321T141249_20210103T141256_VVP288_INT80_G_ueF_F2E0/S1BB_20200321T141249_20210103T141256_VVP288_INT80_G_ueF_F2E0_amp.tif','ingrams/S1BB_20200812T141256_20210103T141256_VVP144_INT80_G_ueF_6FC6/S1BB_20200812T141256_20210103T141256_VVP144_INT80_G_ueF_6FC6_amp.tif', 'ingrams/S1BB_20201104T141258_20210103T141256_VVP060_INT80_G_ueF_EA59/S1BB_20201104T141258_20210103T141256_VVP060_INT80_G_ueF_EA59_amp.tif', 'ingrams/S1BB_20200202T141249_20210103T141256_VVP336_INT80_G_ueF_2668/S1BB_20200202T141249_20210103T141256_VVP336_INT80_G_ueF_2668_amp.tif', 'ingrams/S1BB_20190408T141243_20210103T141256_VVP636_INT80_G_ueF_0DD4/S1BB_20190408T141243_20210103T141256_VVP636_INT80_G_ueF_0DD4_amp.tif', 'ingrams/S1BB_20200508T141251_20210103T141256_VVP240_INT80_G_ueF_2F16/S1BB_20200508T141251_20210103T141256_VVP240_INT80_G_ueF_2F16_amp.tif', 'ingrams/S1BB_20190725T141249_20210103T141256_VVP528_INT80_G_ueF_9805/S1BB_20190725T141249_20210103T141256_VVP528_INT80_G_ueF_9805_amp.tif', 'ingrams/S1BB_20191122T141252_20210103T141256_VVP408_INT80_G_ueF_50ED/S1BB_20191122T141252_20210103T141256_VVP408_INT80_G_ueF_50ED_amp.tif', 'ingrams/S1BB_20201011T141258_20210103T141256_VVP084_INT80_G_ueF_1BC5/S1BB_20201011T141258_20210103T141256_VVP084_INT80_G_ueF_1BC5_amp.tif']"
if str(amp_paths) == test_amp_pths:
    test.log_test('p', f"amp_paths == {test_amp_pths}")
else:
    test.log_test('f', f"amp_paths == {amp_paths}, NOT {test_amp_pths}")
'''
test.add_test_cell("amp_paths = get_tiff_paths(amp_wild_path)", test_amp_paths)

# Confirm correct average heading
test_avg_hdg = '''
test_average_heading = "194.40839831999998"
if str(heading_avg) == test_average_heading:
    test.log_test('p', f"heading_avg == {test_average_heading}")
else:
    test.log_test('f', f"heading_avg == {heading_avg}, NOT {test_average_heading}")
'''
test.add_test_cell("heading_avg = np.mean(list(headings.values()))", test_avg_hdg)

# Confirm predominant UTM zone
test_predom_utm = '''
expected_utm = "32610"
if str(predominant_utm) == expected_utm:
    test.log_test('p', f"predominant_utm == {expected_utm}")
else:
    test.log_test('f', f"predominant_utm == {predominant_utm}, NOT {expected_utm}")
'''
test.add_test_cell("predominant_utm = utm_unique[a][0]", test_predom_utm)

# Confirm single UTM zone
test_single_utm = '''
expected_num_utm = "1"
if str(len(utm_unique)) == expected_num_utm:
    test.log_test('p', f"Expected number of UTM zones == {expected_num_utm}")
else:
    test.log_test('f', f"Expected number of UTM zones == {len(utm_unique)}, NOT {expected_num_utm}")
'''
test.add_test_cell("predominant_utm = utm_unique[a][0]", test_single_utm)

# Confirm existence of full_scene.tif for AOI selector
test_full_scene_tif = '''
if os.path.exists(f"{analysis_directory}/full_scene.tif"):
    test.log_test("p", f"File full_scene.tif for AOI selector tool exists in {analysis_directory}!")
else:
    test.log_test("f", f"File full_scene.tif for AOI selector tool does not exist in {analysis_directory}!")
'''
test.add_test_cell("if os.path.exists(full_scene):", test_full_scene_tif)

# Confirm AOI coordinate transformation
test_geographic_coords = ''' 
expected_coords = "[[571661.7502143616, 5204960.176075896], [656676.9600467023, 5092803.960287691]]"
if str(aoi_coords) == expected_coords:
    test.log_test('p', f"Expected AOI geographic coordinates == {expected_coords}")
else:
    test.log_test('f', f"Expected AOI geographic coordinated == {aoi_coords}, NOT {expected_coords}")   
'''
test.add_test_cell("except TypeError:", test_geographic_coords)

# Confirm number of subset tifs
test_number_tifs = '''
expected_num_tifs = "45"
actual_num_tifs = len(subset_paths)
if str(len(subset_paths)) == expected_num_tifs:
    test.log_test('p', f"Number of subset tifs == {expected_num_tifs}")
else:
    test.log_test('f', f"Number of subset tifs == {actual_num_tifs}, NOT {expected_num_tifs}")
'''
test.add_test_cell("def get_pixels_lines(geotiff_paths: list) -> list:", test_number_tifs)

# Confirm dimensions of subset tifs
test_dimensions_tifs = '''
expected_dimensions_tifs = "{'pixels': {1063}, 'lines': {1402}}"
if str(dimensions) == expected_dimensions_tifs:
    test.log_test('p', f"Dimensions of subset tifs == {expected_dimensions_tifs}")
else:
    test.log_test('f', f"Dimensions of subset tifs == {dimensions}, NOT {expected_dimensions_tifs}")
'''
test.add_test_cell("def get_pixels_lines(geotiff_paths: list) -> list:", test_dimensions_tifs)

# Confirm value of UTC int form
test_utc_int = '''
expected_utc_int = "51172.0"
if str(c_l_utc) == expected_utc_int:
    test.log_test('p', f"UTC in int form == {expected_utc_int}")
else:
    test.log_test('f', f"UTC in int form == {c_l_utc}, NOT {expected_utc_int}")
'''
test.add_test_cell("utc_sat, c_l_utc = getUTC_sat(unw_paths)", test_utc_int)

# Confirm value of UTC human-readable form
test_utc_human = '''
expected_utc_human = "14:12"
if str(utc_sat) == expected_utc_human:
    test.log_test('p', f"UTC in int form == {expected_utc_human}")
else:
    test.log_test('f', f"UTC in int form == {utc_sat}, NOT {expected_utc_human}")
'''
test.add_test_cell("utc_sat, c_l_utc = getUTC_sat(unw_paths)", test_utc_human)

# Confirm existence of parms_aps.txt
test_parms_aps_txt = '''
if os.path.exists(f"{analysis_directory}/parms_aps.txt"):
    test.log_test("p", f"TRAIN info file parms_aps.txt exists in {analysis_directory}!")
else:
    test.log_test("f", f"TRAIN info file parms_aps.txt does not exist in {analysis_directory}!")
'''
test.add_test_cell("!mkdir -p {merra2_datapath} # create the directory", test_parms_aps_tif)

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