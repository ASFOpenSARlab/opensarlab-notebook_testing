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
           "utm_zones, utm_types = get_utm_zones_types(tiff_paths)", #remove later so this cell runs
           "for file in tiff_paths:", #remove later so this cell runs
           "utm_zones, utm_types = get_utm_zones_types(tiff_paths)", #remove later so this cell runs
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

# # Verify all the expected amplitude geotiffs are present
# test_amp_paths = '''
# test_amp_pths = ['ingrams/S1AA_20161119T234106_20210720T234131_VVP1704_INT80_G_ueF_D006/S1AA_20161119T234106_20210720T234131_VVP1704_INT80_G_ueF_D006_amp.tif', 'ingrams/S1AA_20170106T234103_20210720T234131_VVP1656_INT80_G_ueF_24E9/S1AA_20170106T234103_20210720T234131_VVP1656_INT80_G_ueF_24E9_amp.tif', 'ingrams/S1AA_20170319T234100_20210720T234131_VVP1584_INT80_G_ueF_F049/S1AA_20170319T234100_20210720T234131_VVP1584_INT80_G_ueF_F049_amp.tif', 'ingrams/S1AA_20170506T234102_20210720T234131_VVP1536_INT80_G_ueF_74A6/S1AA_20170506T234102_20210720T234131_VVP1536_INT80_G_ueF_74A6_amp.tif', 'ingrams/S1AA_20170717T234106_20210720T234131_VVP1464_INT80_G_ueF_0785/S1AA_20170717T234106_20210720T234131_VVP1464_INT80_G_ueF_0785_amp.tif', 'ingrams/S1AA_20170903T234108_20210720T234131_VVP1416_INT80_G_ueF_1C5E/S1AA_20170903T234108_20210720T234131_VVP1416_INT80_G_ueF_1C5E_amp.tif', 'ingrams/S1AA_20171102T234109_20210720T234131_VVP1356_INT80_G_ueF_D66B/S1AA_20171102T234109_20210720T234131_VVP1356_INT80_G_ueF_D66B_amp.tif', 'ingrams/S1AA_20180101T234107_20210720T234131_VVP1296_INT80_G_ueF_CE38/S1AA_20180101T234107_20210720T234131_VVP1296_INT80_G_ueF_CE38_amp.tif', 'ingrams/S1AA_20180302T234106_20210720T234131_VVP1236_INT80_G_ueF_4C0D/S1AA_20180302T234106_20210720T234131_VVP1236_INT80_G_ueF_4C0D_amp.tif', 'ingrams/S1AA_20180501T234108_20210720T234131_VVP1176_INT80_G_ueF_9462/S1AA_20180501T234108_20210720T234131_VVP1176_INT80_G_ueF_9462_amp.tif', 'ingrams/S1AA_20180630T234111_20210720T234131_VVP1116_INT80_G_ueF_DE49/S1AA_20180630T234111_20210720T234131_VVP1116_INT80_G_ueF_DE49_amp.tif', 'ingrams/S1AA_20180817T234114_20210720T234131_VVP1068_INT80_G_ueF_0AE4/S1AA_20180817T234114_20210720T234131_VVP1068_INT80_G_ueF_0AE4_amp.tif', 'ingrams/S1AA_20181004T234116_20210720T234131_VVP1020_INT80_G_ueF_3CBA/S1AA_20181004T234116_20210720T234131_VVP1020_INT80_G_ueF_3CBA_amp.tif', 'ingrams/S1AA_20181203T234115_20210720T234131_VVP960_INT80_G_ueF_DD9A/S1AA_20181203T234115_20210720T234131_VVP960_INT80_G_ueF_DD9A_amp.tif', 'ingrams/S1AA_20190201T234113_20210720T234131_VVP900_INT80_G_ueF_F5FF/S1AA_20190201T234113_20210720T234131_VVP900_INT80_G_ueF_F5FF_amp.tif', 'ingrams/S1AA_20190402T234113_20210720T234131_VVP840_INT80_G_ueF_C23E/S1AA_20190402T234113_20210720T234131_VVP840_INT80_G_ueF_C23E_amp.tif', 'ingrams/S1AA_20190508T234114_20210720T234131_VVP804_INT80_G_ueF_6081/S1AA_20190508T234114_20210720T234131_VVP804_INT80_G_ueF_6081_amp.tif', 'ingrams/S1AA_20190707T234117_20210720T234131_VVP744_INT80_G_ueF_E971/S1AA_20190707T234117_20210720T234131_VVP744_INT80_G_ueF_E971_amp.tif', 'ingrams/S1AA_20190905T234121_20210720T234131_VVP684_INT80_G_ueF_1E13/S1AA_20190905T234121_20210720T234131_VVP684_INT80_G_ueF_1E13_amp.tif', 'ingrams/S1AA_20191104T234122_20210720T234131_VVP624_INT80_G_ueF_E145/S1AA_20191104T234122_20210720T234131_VVP624_INT80_G_ueF_E145_amp.tif', 'ingrams/S1AA_20200103T234120_20210720T234131_VVP564_INT80_G_ueF_5C2F/S1AA_20200103T234120_20210720T234131_VVP564_INT80_G_ueF_5C2F_amp.tif', 'ingrams/S1AA_20200303T234119_20210720T234131_VVP504_INT80_G_ueF_A376/S1AA_20200303T234119_20210720T234131_VVP504_INT80_G_ueF_A376_amp.tif', 'ingrams/S1AA_20200502T234120_20210720T234131_VVP444_INT80_G_ueF_7CE5/S1AA_20200502T234120_20210720T234131_VVP444_INT80_G_ueF_7CE5_amp.tif', 'ingrams/S1AA_20200701T234124_20210720T234131_VVP384_INT80_G_ueF_E040/S1AA_20200701T234124_20210720T234131_VVP384_INT80_G_ueF_E040_amp.tif', 'ingrams/S1AA_20200911T234128_20210720T234131_VVP312_INT80_G_ueF_8E33/S1AA_20200911T234128_20210720T234131_VVP312_INT80_G_ueF_8E33_amp.tif', 'ingrams/S1AA_20201110T234128_20210720T234131_VVP252_INT80_G_ueF_37B4/S1AA_20201110T234128_20210720T234131_VVP252_INT80_G_ueF_37B4_amp.tif', 'ingrams/S1AA_20210109T234126_20210720T234131_VVP192_INT80_G_ueF_AB84/S1AA_20210109T234126_20210720T234131_VVP192_INT80_G_ueF_AB84_amp.tif', 'ingrams/S1AA_20210310T234125_20210720T234131_VVP132_INT80_G_ueF_3720/S1AA_20210310T234125_20210720T234131_VVP132_INT80_G_ueF_3720_amp.tif', 'ingrams/S1AA_20210509T234127_20210720T234131_VVP072_INT80_G_ueF_B33E/S1AA_20210509T234127_20210720T234131_VVP072_INT80_G_ueF_B33E_amp.tif', 'ingrams/S1AA_20210708T234130_20210720T234131_VVP012_INT80_G_ueF_9196/S1AA_20210708T234130_20210720T234131_VVP012_INT80_G_ueF_9196_amp.tif']
# if (amp_paths) == test_amp_pths:
#     test.log_test('p', f"amp_paths == {test_amp_pths}")
# else:
#     test.log_test('f', f"amp_paths == {amp_paths}, NOT {test_amp_pths}")
# '''
# test.add_test_cell("amp_paths    = get_tiff_paths(amp_wild_path)", test_amp_paths)

# # Confirm creation of tindex
# test_tindex = """
# if type(tindex) == pd.core.indexes.datetimes.DatetimeIndex:
#     test.log_test('p', f"type(tindex) == pd.core.indexes.datetimes.DatetimeIndex")
# else:
#     test.log_test('f', f"type(tindex) == {type(tindex)}, NOT pd.core.indexes.datetimes.DatetimeIndex")
# if tindex.size == 70:
#     test.log_test('p', f"tindex.size == 70")
# else:
#     test.log_test('f', f"tindex.size == {tindex.size}, NOT 70")
# """
# test.add_test_cell("tindex = pd.DatetimeIndex(dates)", test_tindex)

# # Confirm raster_stack == (1270, 1547)
# test_raster = """
# if raster.shape == (1270, 1547):
#     test.log_test('p', f"raster.shape == (1270, 1547)")
# else:
#     test.log_test('f', f"raster.shape == {raster.shape}, NOT (1270, 1547)")
# """
# test.add_test_cell("raster = band.ReadAsArray()", test_raster)

# # Confirm creation of plots_and_products directory
# test_product_path = """
# if os.path.exists(f"{test_data_path}/{product_path}"):
#     test.log_test('p', f"{test_data_path}/{product_path} directory found")
# else:
#     test.log_test('f', f"{test_data_path}/{product_path} directory NOT found")
# """
# test.add_test_cell("product_path = 'plots_and_animations'", test_product_path)

# # Confirm creation of animation.gif
# test_animation_gif = """
# if os.path.exists(f"{test_data_path}/{product_path}/animation.gif"):
#     test.log_test('p', f"{test_data_path}/{product_path}/animation.gif found")
# else:
#     test.log_test('f', f"{test_data_path}/{product_path}/animation.gif NOT found")
# """
# test.add_test_cell("ani.save('animation.gif', writer='pillow', fps=2)", test_animation_gif)
# #test.add_test_cell("ani.save('NepalTimeSeriesAnimation.gif', writer='pillow', fps=2)", test_animation_gif)

# # Confirm rs_means_pwr.shape == (70,)
# test_rs_means_pwr = """
# if rs_means_pwr.shape == (70,):
#     test.log_test('p', f"rs_means_pwr.shape == (70,)")
# else:
#     test.log_test('f', f"rs_means_pwr.shape == {rs_means_pwr.shape}, NOT (70,)")
# """
# test.add_test_cell("rs_means_pwr.shape", test_rs_means_pwr)

# # Confirm creation of time_series_means.png
# test_time_series_means_png = """
# if os.path.exists(f"{test_data_path}/{product_path}/time_series_means.png"):
#     test.log_test('p', f"{test_data_path}/{product_path}/time_series_means.png found")
# else:
#     test.log_test('f', f"{test_data_path}/{product_path}/time_series_means.png NOT found")
# """
# test.add_test_cell("plt.savefig('time_series_means', dpi=72, transparent='true')",
#                    test_time_series_means_png)

# # Confirm creation of animation_histogram.gif
# test_animation__histogram_gif = """
# if os.path.exists(f"{test_data_path}/{product_path}/animation_histogram.gif"):
#     test.log_test('p', f"{test_data_path}/{product_path}/animation_histogram.gif found")
# else:
#     test.log_test('f', f"{test_data_path}/{product_path}/animation_histogram.gif NOT found")
# """
# #test.add_test_cell("ani.save('NepalTSAnimation_means.gif', writer='pillow', fps=2)", test_animation__histogram_gif)
# test.add_test_cell("ani.save('animation_histogram.gif', writer='pillow', fps=2)", test_animation__histogram_gif)


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