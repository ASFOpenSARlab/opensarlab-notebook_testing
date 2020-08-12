#!/usr/bin/env python3

from getpass import getpass
import shutil

from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io

######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = ("/home/jovyan/notebooks/SAR_Training/English/Ecosystems/"
                "Exercise4B-Change_Detection_Amplitude_Time_Series_Example.ipynb")
log_pth = "/home/jovyan/notebooks/notebook_testing_dev"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = "path = \"/home/jovyan/notebooks/SAR_Training/English/Ecosystems/data_Ex4B-Change_Detection_Amplitude_Time_Series_Example\""
test_data_path = "/home/jovyan/notebooks/notebook_testing_dev/data_Ex4B-Change_Detection_Amplitude_Time_Series_Example"
_replacement = f"path = f\"{test_data_path}\""
test.replace_line(_to_replace, _to_replace, _replacement)

# Erase data directory if already present
try:
   shutil.rmtree(test_data_path)
except:
   pass


######### TESTS ###########

# Check that the data was downloaded from the S3 bucket
test_s3_copy = """
if os.path.exists(f"{os.getcwd()}/Niamey.zip"):
    test.log_test('p', f"Niamey.zip successfully copied from s3://asf-jupyter-data/Niamey.zip")
else:
    test.log_test('f', f"Niamey.zip NOT copied from s3://asf-jupyter-data/Niamey.zip")
"""
test.add_test_cell("!aws s3 cp s3://asf-jupyter-data/Niamey.zip Niamey.zip", test_s3_copy)

# Confirm that all expected files were extracted from the zip
test_zip_extraction = """
import glob
test_vrt_qty = len(glob.glob("cra/*.vrt"))
if test_vrt_qty == 134:
    test.log_test('p', f"134 vrts extracted, as expected")
else:
    test.log_test('f', f"{test_vrt_qty} vrts extracted, NOT 134") 
test_tif_qty = len(glob.glob("cra/*.tif"))
if test_tif_qty == 14:
    test.log_test('p', f"14 tifs extracted, as expected")
else:
    test.log_test('f', f"{test_tif_qty} tifs extracted, NOT 14")     
test_dates_qty = len(glob.glob("cra/*.dates"))
if test_dates_qty == 10:
    test.log_test('p', f"10 dates files extracted, as expected")
else:
    test.log_test('f', f"{test_dates_qty} dates files extracted, NOT 10")    
test_mp4_qty = len(glob.glob("cra/*.mp4"))    
if test_mp4_qty == 1:
    test.log_test('p', f"1 mp4 extracted, as expected")
else:
    test.log_test('f', f"{test_mp4_qty} mp4 files extracted, NOT 1")     
test_xml_qty = len(glob.glob("cra/*.xml"))
if test_xml_qty == 4:
    test.log_test('p', f"4 xml files extracted, as expected")
else:
    test.log_test('f', f"{test_xml_qty} xml files extracted, NOT 4")    
"""
test.add_test_cell("asf_unzip(path, f)", test_zip_extraction)

# Confirm creation of time_index
test_time_index = """
if type(time_index) == pd.core.indexes.datetimes.DatetimeIndex:
    test.log_test('p', f"type(time_index) == pd.core.indexes.datetimes.DatetimeIndex")
else:
    test.log_test('f', f"type(time_index) == {type(time_index)}, NOT pd.core.indexes.datetimes.DatetimeIndex")
if time_index.size == 60:
    test.log_test('p', f"time_index.size == 60")
else:
    test.log_test('f', f"time_index.size == {time_index.size}, NOT 60")
"""
test.add_test_cell("time_index = pd.DatetimeIndex(dates)", test_time_index)

# Confirm raster_stack.shape == (60, 38, 44)
test_raster_stack = """
if raster_stack.shape == (60, 38, 44):
    test.log_test('p', f"raster_stack.shape == (60, 38, 44)")
else:
    test.log_test('f', f"raster_stack.shape == {raster_stack.shape}, NOT (60, 38, 44)")
"""
test.add_test_cell("raster_stack = gdal.Open(image_file).ReadAsArray()", test_raster_stack)

# Confirm creation of plots_and_products directory
test_product_path = """
if os.path.exists(f"{test_data_path}/{product_path}"):
    test.log_test('p', f"{test_data_path}/{product_path} directory found")
else:
    test.log_test('f', f"{test_data_path}/{product_path} directory NOT found")
"""
test.add_test_cell("product_path = 'plots_and_products'", test_product_path)

# Confrim coords == [[402380.0, 1492220.0], [403260.0, 1491460.0]]
test_coords = """
if coords == [[402380.0, 1492220.0], [403260.0, 1491460.0]]:
    test.log_test('p', f"coords == [[402380.0, 1492220.0], [403260.0, 1491460.0]]")
else:
    test.log_test('f', f"coords == {coords}, NOT [[402380.0, 1492220.0], [403260.0, 1491460.0]]")
"""
test.add_test_cell("coords = [vrt_info['cornerCoordinates']['upperLeft'],", test_coords)

# Confirm utm_zone == 32631
test_utm_zone = """
if utm_zone == '32631':
    test.log_test('p', f"utm_zone == '32631'")
else:
    test.log_test('f', f"utm_zone == {utm_zone}, NOT '32631'")
"""
test.add_test_cell("utm_zone = vrt_info['coordinateSystem']['wkt'", test_utm_zone)

# Confirm type, dtype, and size of ts
test_ts = """
if type(ts) == pd.core.series.Series:
    test.log_test('p', f"type(ts) == pd.core.series.Series")
else:
    test.log_test('f', f"type(ts) == {type(ts)}, NOT pd.core.series.Series")
if ts.dtype == np.float64:
    test.log_test('p', f"ts.dtype == np.float64")
else:
    test.log_test('f', f"ts.dtype == {ts.dtype}, NOT np.float64")
if ts.size == 60:
    test.log_test('p', f"ts.size == 60")
else:
    test.log_test('f', f"ts.size == {ts.size}, NOT 60")
"""
test.add_test_cell("ts = pd.Series(rs_means_dB,index=time_index)", test_ts)

# Confirm creation of time_series_means.png
test_times_series_means = """
if os.path.exists("time_series_means.png"):
    test.log_test('p', f"time_series_means.png found")
else:
    test.log_test('f', f"time_series_means.png NOT found")
"""
test.add_test_cell("plt.savefig('time_series_means.png', dpi=72)", test_times_series_means)

# Confirm creation of band_24.png
test_band_24_png = """
if os.path.exists("band_24.png"):
    test.log_test('p', f"band_24.png found")
else:
    test.log_test('f', f"band_24.png NOT found")
"""
test.add_test_cell("band_number = 24", test_band_24_png)

# Confirm creation of band_43.png
test_band_43_png = """
if os.path.exists("band_43.png"):
    test.log_test('p', f"band_43.png found")
else:
    test.log_test('f', f"band_43.png NOT found")
"""
test.add_test_cell("band_number = 43", test_band_43_png)

# Confirm type, dtype, and size of timeseries for subset (5, 20, 3, 3)
test_ts_2 = """
if type(ts) == pd.core.series.Series:
    test.log_test('p', f"type(ts) == pd.core.series.Series")
else:
    test.log_test('f', f"type(ts) == {type(ts)}, NOT pd.core.series.Series")
if ts.dtype == np.float64:
    test.log_test('p', f"ts.dtype == np.float64")
else:
    test.log_test('f', f"ts.dtype == {ts.dtype}, NOT np.float64")
if ts.size == 60:
    test.log_test('p', f"ts.size == 60")
else:
    test.log_test('f', f"ts.size == {ts.size}, NOT 60")
"""
test.add_test_cell("ts = timeSeries(raster_stack_pwr, time_index, subset)", test_ts_2)

# Confirm type, dtype, and size of timeseries for subset (5, 20, 5, 5)
test_ts_3 = """
if type(time_series_1) == pd.core.series.Series:
    test.log_test('p', f"type(time_series_1) == pd.core.series.Series")
else:
    test.log_test('f', f"type(time_series_1) == {type(time_series_1)}, NOT pd.core.series.Series")
if time_series_1.dtype == np.float64:
    test.log_test('p', f"time_series_1.dtype == np.float64")
else:
    test.log_test('f', f"time_series_1.dtype == {time_series_1.dtype}, NOT np.float64")
if time_series_1.size == 60:
    test.log_test('p', f"time_series_1.size == 60")
else:
    test.log_test('f', f"time_series_1.size == {time_series_1.size}, NOT 60")
"""
test.add_test_cell("subset = (5, 20, 5, 5)", test_ts_3)

# Confirm data_frame type and shape
test_data_frame = """
if type(data_frame) == pd.core.frame.DataFrame:
    test.log_test('p', f"type(data_frame) == pd.core.frame.DataFrame")
else:
    test.log_test('f', f"type(data_frame) == {type(data_frame)}, NOT pd.core.frame.DataFrame")
"""
test.add_test_cell("data_frame = pd.DataFrame(time_series_1", test_data_frame)

# Confirm creation of time_series_backscatter_profile.png
test_time_series_backscatter_profile_png = """
if os.path.exists(f"time_series_backscatter_profile.png"):
    test.log_test('p', f"time_series_backscatter_profile.png found")
else:
    test.log_test('f', f"time_series_backscatter_profile.png NOT found")
"""
test.add_test_cell("plt.savefig('time_series_backscatter_profile'", 
                   test_time_series_backscatter_profile_png)

# Confirm creation of march2may_time_series_backscatter_profile.png
test_march2may_time_series_backscatter_profile_png = """
if os.path.exists(f"march2may_time_series_backscatter_profile.png"):
    test.log_test('p', f"march2may_time_series_backscatter_profile.png found")
else:
    test.log_test('f', f"march2may_time_series_backscatter_profile.png NOT found")
"""
test.add_test_cell("plt.savefig('march2may_time_series_backscatter_profile'",
                   test_march2may_time_series_backscatter_profile_png)

# Confirm creation of june2feb_time_series_backscatter_profile.png
test_june2feb_time_series_backscatter_profile_png = """
if os.path.exists(f"june2feb_time_series_backscatter_profile.png"):
    test.log_test('p', f"june2feb_time_series_backscatter_profile.png found")
else:
    test.log_test('f', f"june2feb_time_series_backscatter_profile.png NOT found")
"""
test.add_test_cell("plt.savefig('june2feb_time_series_backscatter_profile'",
                   test_june2feb_time_series_backscatter_profile_png)


# Confirm creation of yearly_time_series_backscatter_profile.png
test_yearly_time_series_backscatter_profile_png = """
if os.path.exists(f"yearly_time_series_backscatter_profile.png"):
    test.log_test('p', f"yearly_time_series_backscatter_profile.png found")
else:
    test.log_test('f', f"yearly_time_series_backscatter_profile.png NOT found")
"""
test.add_test_cell("plt.savefig('yearly_time_series_backscatter_profile'",
                   test_yearly_time_series_backscatter_profile_png)


# Confirm creation of overlapping_years_time_series_backscatter_profile.png
test_overlapping_years_time_series_backscatter_profile_png = """
if os.path.exists(f"overlapping_years_time_series_backscatter_profile.png"):
    test.log_test('p', f"overlapping_years_time_series_backscatter_profile.png found")
else:
    test.log_test('f', f"overlapping_years_time_series_backscatter_profile.png NOT found")
"""
test.add_test_cell("plt.savefig('overlapping_years_time_series_backscatter_profile'",
                   test_overlapping_years_time_series_backscatter_profile_png)


# Confirm creation of year2year_differencing_time_series.png
test_year2year_differencing_time_series_png = """
if os.path.exists(f"year2year_differencing_time_series.png"):
    test.log_test('p', f"year2year_differencing_time_series.png found")
else:
    test.log_test('f', f"year2year_differencing_time_series.png NOT found")
"""
test.add_test_cell("plt.savefig('year2year_differencing_time_series'",
                   test_year2year_differencing_time_series_png)

# Confirm type, values of threshold_exceeded
test_threshold_exceeded = """
if type(threshold_exceeded) == pd.core.series.Series:
    test.log_test('p', f"type(threshold_exceeded) == pd.core.series.Series")
else:
    test.log_test('f', (f"type(threshold_exceeded) == {type(threshold_exceeded)}"
                        f", NOT pd.core.series.Series"))
test_threshold_exceeded_values = set([-3.642116657591833, -3.527523298131465, -3.0819736909879634,
                                      -3.4991774578663364, -3.8107595055247785, -3.6659672020413723,
                                      -3.2480335783369725, -3.4209522714485345, -3.741038740894158,
                                      -3.7829747823672175, -3.8032501377976082, -3.9564387882144274,
                                      -4.00389092570658, -3.430614690382912])
if set(threshold_exceeded.values) == test_threshold_exceeded_values:
    test.log_test('p', f"set(threshold_exceeded.values) == {test_threshold_exceeded_values}")
else:
    test.log_test('f', (f"set(threshold_exceeded.values) == {set(threshold_exceeded.values)}"
                        f", NOT {test_threshold_exceeded_values}"))
"""
test.add_test_cell("threshold_exceeded = diff_2017_2016[abs", test_threshold_exceeded)

# Confirm creation of original_vs_median_time_series.png
test_original_vs_median_time_series_png = """
if os.path.exists(f"original_vs_median_time_series.png"):
    test.log_test('p', f"original_vs_median_time_series.png found")
else:
    test.log_test('f', f"original_vs_median_time_series.png NOT found")
"""
test.add_test_cell("plt.savefig('original_vs_median_time_series'",
                   test_original_vs_median_time_series_png)

# Confirm creation of original_time_series_vs_mean_val.png
test_original_time_series_vs_mean_val_png = """
if os.path.exists(f"original_time_series_vs_mean_val.png"):
    test.log_test('p', f"original_time_series_vs_mean_val.png found")
else:
    test.log_test('f', f"original_time_series_vs_mean_val.png NOT found")
"""
test.add_test_cell("plt.savefig('original_time_series_vs_mean_val'",
                   test_original_time_series_vs_mean_val_png)

# Confirm creation of median_time_series_vs_mean_val.png
test_median_time_series_vs_mean_val_png = """
if os.path.exists(f"median_time_series_vs_mean_val.png"):
    test.log_test('p', f"median_time_series_vs_mean_val.png found")
else:
    test.log_test('f', f"median_time_series_vs_mean_val.png NOT found")
"""
test.add_test_cell("plt.savefig('median_time_series_vs_mean_val'",
                   test_median_time_series_vs_mean_val_png)

# Confirm creation of cumulative_sum_residuals.png
test_cumulative_sum_residuals_png = """
if os.path.exists(f"cumulative_sum_residuals.png"):
    test.log_test('p', f"cumulative_sum_residuals.png found")
else:
    test.log_test('f', f"cumulative_sum_residuals.png NOT found")
"""
test.add_test_cell("plt.savefig('cumulative_sum_residuals'",
                   test_cumulative_sum_residuals_png)

# Confirm change_mag == 32.803057442215746
test_change_mag = """
if change_mag == 32.803057442215746:
    test.log_test('p', f"change_mag == 32.803057442215746")
else:
    test.log_test('f', f"change_mag == {change_mag}, NOT 32.803057442215746")
"""
test.add_test_cell("change_mag = sums.max() - sums.min()", test_change_mag)

# Confirm change_point_before == pd.Timestamp('2017-02-15 00:00:00')
test_change_point_before = """
if change_point_before == pd.Timestamp('2017-02-15 00:00:00'):
    test.log_test('p', f"change_point_before == pd.Timestamp('2017-02-15 00:00:00')")
else:
    test.log_test('f', f"change_point_before == {change_point_before}, NOT pd.Timestamp('2017-02-15 00:00:00')")
"""
test.add_test_cell("change_point_before = sums[sums==sums.max()].index[0]",
                   test_change_point_before)

# Confirm change_point_after == pd.Timestamp('2017-02-27 00:00:00')
test_change_point_after = """
if change_point_after == pd.Timestamp('2017-02-27 00:00:00'):
    test.log_test('p', f"change_point_after == pd.Timestamp('2017-02-27 00:00:00')")
else:
    test.log_test('f', f"change_point_after == {change_point_after}, NOT pd.Timestamp('2017-02-27 00:00:00')")
"""
test.add_test_cell("change_point_after = sums[sums.index > change_point_before].index[0]",
                   test_change_point_after)

# Confirm creation of bootstrap__2000.png
test_bootstrap__2000_png = """
if os.path.exists(f"bootstrap__2000.png"):
    test.log_test('p', f"bootstrap__2000.png found")
else:
    test.log_test('f', f"bootstrap__2000.png NOT found")
"""
test.add_test_cell("bootstrapped_change_mag = bootstrap(n_",
                  test_bootstrap__2000_png)
                   
# Confirm confidence_level == 1.0
test_confidence_level = """
if confidence_level == 1.0:
    test.log_test('p', f"confidence_level == 1.0")
else:
    test.log_test('f', f"confidence_level == {confidence_level}, NOT 1.0")
"""
test.add_test_cell("confidence_level = 1.0 * bootstrapped_change_mag[0] / n_bootstraps",
                   test_confidence_level)

# Confirm creation of global_means_time_series.png
test_global_means_time_series_png = """
if os.path.exists(f"global_means_time_series.png"):
    test.log_test('p', f"global_means_time_series.png found")
else:
    test.log_test('f', f"global_means_time_series.png NOT found")
"""
test.add_test_cell('plt.savefig(f"global_means_time_series"',
                  test_global_means_time_series_png)

# Confirm creation of detrended_time_series.png
test_detrended_time_series_png = """
if os.path.exists(f"detrended_time_series.png"):
    test.log_test('p', f"detrended_time_series.png found")
else:
    test.log_test('f', f"detrended_time_series.png NOT found")
"""
test.add_test_cell('plt.savefig(f"detrended_time_series"',
                  test_detrended_time_series_png)

# Confirm creation of globalMeans_original_detrended_time_series.png
test_globalMeans_original_detrended_time_series_png = """
if os.path.exists(f"globalMeans_original_detrended_time_series.png"):
    test.log_test('p', f"globalMeans_original_detrended_time_series.png found")
else:
    test.log_test('f', f"globalMeans_original_detrended_time_series.png NOT found")
"""
test.add_test_cell('plt.savefig(f"globalMeans_original_detrended_time_series',
                  test_globalMeans_original_detrended_time_series_png)

# Confirm creation of cumualtive_sum_detrended_time_series.png
test_cumualtive_sum_detrended_time_series_png = """
if os.path.exists(f"cumualtive_sum_detrended_time_series.png"):
    test.log_test('p', f"cumualtive_sum_detrended_time_series.png found")
else:
    test.log_test('f', f"cumualtive_sum_detrended_time_series.png NOT found")
"""
test.add_test_cell('plt.savefig(f"cumualtive_sum_detrended_time_series"',
                  test_cumualtive_sum_detrended_time_series_png)

# Confirm residuals_change_point_before and residuals_change_point_after values
test_detrended_change_points_before_after = """
if detrended_change_point_before == pd.Timestamp('2017-11-06 00:00:00'):
    test.log_test('p', f"detrended_change_point_before == pd.Timestamp('2017-11-06 00:00:00')")
else:
    test.log_test('f', (f"detrended_change_point_before == {detrended_change_point_before},"
                        f" NOT pd.Timestamp('2017-11-06 00:00:00')"))
if detrended_change_point_after == pd.Timestamp('2017-11-18 00:00:00'):
    test.log_test('p', f"detrended_change_point_after == pd.Timestamp('2017-11-18 00:00:00')")
else:
    test.log_test('f', (f"detrended_change_point_after == {detrended_change_point_after},"
                        f"NOT pd.Timestamp('2017-11-18 00:00:00')"))
"""
test.add_test_cell("detrended_change_point_before =",
                   test_detrended_change_points_before_after)

# Confirm creation of bootstrap_detrended_2000.png
test_bootstrap_detrended_2000_png = """
if os.path.exists(f"bootstrap_detrended_2000.png"):
    test.log_test('p', f"bootstrap_detrended_2000.png found")
else:
    test.log_test('f', f"bootstrap_detrended_2000.png NOT found")
"""
test.add_test_cell('bootstrap(n_bootstraps, "detrended"',
                  test_bootstrap_detrended_2000_png)

# Confirm detrended_confidence_level == 0.0
test_detrended_confidence_level = """
if detrended_confidence_level == 0.0:
    test.log_test('p', f"detrended_confidence_level == 0.0")
else:
    test.log_test('f', f"detrended_confidence_level == {detrended_confidence_level}, NOT 0.0")
"""
test.add_test_cell("detrended_confidence_level = bootstrapped_change",
                   test_detrended_confidence_level)
       
# Confirm creation of band_1.png
test_band_1_png = """
if os.path.exists("band_1.png"):
    test.log_test('p', f"band_1.png found")
else:
    test.log_test('f', f"band_1.png NOT found")
"""
test.add_test_cell("plt.savefig('band_1.png',", test_band_1_png)

# Confirm creation of band_1.tiff
test_band_1_tiff = """
if os.path.exists("band_1.tiff"):
    test.log_test('p', f"band_1.tiff found")
else:
    test.log_test('f', f"band_1.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(raster_stack[0], 'band_1'", test_band_1_tiff)

# Confirm creation of raster_stack_mean.png
test_raster_stack_mean_png = """
if os.path.exists("raster_stack_mean.png"):
    test.log_test('p', f"raster_stack_mean.png found")
else:
    test.log_test('f', f"raster_stack_mean.png NOT found")
"""
test.add_test_cell("plt.savefig('raster_stack_mean.png'", test_raster_stack_mean_png)

# Confirm creation of raster_stack_mean.tiff
test_raster_stack_mean_tiff = """
if os.path.exists("raster_stack_mean.tiff"):
    test.log_test('p', f"raster_stack_mean.tiff found")
else:
    test.log_test('f', f"raster_stack_mean.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(raster_stack_mean", test_raster_stack_mean_tiff)

# Confirm creation of residuals_band_1.png
test_residuals_band_1_png = """
if os.path.exists("residuals_band_1.png"):
    test.log_test('p', f"residuals_band_1.png found")
else:
    test.log_test('f', f"residuals_band_1.png NOT found")
"""
test.add_test_cell("plt.savefig('residuals_band_1'", test_residuals_band_1_png)

# Confirm creation of residuals_band_1.tiff
test_residuals_band_1_tiff = """
if os.path.exists("residuals_band_1.tiff"):
    test.log_test('p', f"residuals_band_1.tiff found")
else:
    test.log_test('f', f"residuals_band_1.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(residuals[0]", test_residuals_band_1_tiff)

# Confirm creation of Smax_Smin_Sdiff.png
test_Smax_Smin_Sdiff_png = """
if os.path.exists("Smax_Smin_Sdiff.png"):
    test.log_test('p', f"Smax_Smin_Sdiff.png found")
else:
    test.log_test('f', f"Smax_Smin_Sdiff.png NOT found")
"""
test.add_test_cell("plt.savefig('Smax_Smin_Sdiff'", test_Smax_Smin_Sdiff_png)

# Confirm creation of Smax.tiff
test_Smax_tiff = """
if os.path.exists("Smax.tiff"):
    test.log_test('p', f"Smax.tiff found")
else:
    test.log_test('f', f"Smax.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(sums_max, 'Smax'", test_Smax_tiff)

# Confirm creation of Smin.tiff
test_Smin_tiff = """
if os.path.exists("Smin.tiff"):
    test.log_test('p', f"Smin.tiff found")
else:
    test.log_test('f', f"Smin.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(sums_min, 'Smin'", test_Smin_tiff)

# Confirm creation of Sdiff.tiff
test_Sdiff_tiff = """
if os.path.exists("Sdiff.tiff"):
    test.log_test('p', f"Sdiff.tiff found")
else:
    test.log_test('f', f"Sdiff.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(change_mag, 'Sdiff'", test_Sdiff_tiff)

# Confirm creation of Sdiff_histogram_CDF.png
test_Sdiff_histogram_CDF_png = """
if os.path.exists("Sdiff_histogram_CDF.png"):
    test.log_test('p', f"Sdiff_histogram_CDF.png found")
else:
    test.log_test('f', f"Sdiff_histogram_CDF.png NOT found")
"""
test.add_test_cell("plt.savefig('Sdiff_histogram_CDF'", test_Sdiff_histogram_CDF_png)

# Confirm creation of change_candidate.png
test_change_candidate_png = """
if os.path.exists("change_candidate.png"):
    test.log_test('p', f"change_candidate.png found")
else:
    test.log_test('f', f"change_candidate.png NOT found")
"""
test.add_test_cell("plt.savefig('change_candidate'", test_change_candidate_png)

# Confirm creation of change_candidate.tiff
test_change_candidate_tiff = """
if os.path.exists("change_candidate.tiff"):
    test.log_test('p', f"change_candidate.tiff found")
else:
    test.log_test('f', f"change_candidate.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(change_mag_mask, 'change_candidate'",
                   test_change_candidate_tiff)

# Confirm creation of masked_Smax_Smin_Sdiff.png
test_masked_Smax_Smin_Sdiff_png = """
if os.path.exists("masked_Smax_Smin_Sdiff.png"):
    test.log_test('p', f"masked_Smax_Smin_Sdiff.png found")
else:
    test.log_test('f', f"masked_Smax_Smin_Sdiff.png NOT found")
"""
test.add_test_cell("plt.savefig('masked_Smax_Smin_Sdiff'", 
                   test_masked_Smax_Smin_Sdiff_png)

# Confirm creation of masked_Smax.tiff
test_masked_Smax_tiff = """
if os.path.exists("masked_Smax.tiff"):
    test.log_test('p', f"masked_Smax.tiff found")
else:
    test.log_test('f', f"masked_Smax.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(sums_masked_max, 'masked_Smax'",
                   test_masked_Smax_tiff)

# Confirm creation of masked_Smin.tiff
test_masked_Smin_tiff = """
if os.path.exists("masked_Smin.tiff"):
    test.log_test('p', f"masked_Smin.tiff found")
else:
    test.log_test('f', f"masked_Smin.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(sums_masked_min, 'masked_Smin'",
                   test_masked_Smin_tiff)

# Confirm creation of masked_Sdiff.tiff
test_masked_Sdiff_tiff = """
if os.path.exists("masked_Sdiff.tiff"):
    test.log_test('p', f"masked_Sdiff.tiff found")
else:
    test.log_test('f', f"masked_Sdiff.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(change_mag, 'masked_Sdiff'",
                   test_masked_Sdiff_tiff)

# Confirm creation of confidence_change_point.png
test_confidence_change_point_png = """
if os.path.exists("confidence_change_point.png"):
    test.log_test('p', f"confidence_change_point.png found")
else:
    test.log_test('f', f"confidence_change_point.png NOT found")
"""
test.add_test_cell("geotiff_from_plot(confidence_level*100, 'confidence_level'", 
                   test_confidence_change_point_png)

# Confirm creation of confidence_level.tiff
test_confidence_level_tiff = """
if os.path.exists("confidence_level.tiff"):
    test.log_test('p', f"confidence_level.tiff found")
else:
    test.log_test('f', f"confidence_level.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(confidence_level*100, 'confidence_level'", 
                   test_confidence_level_tiff)

# Confirm creation of change_point.tiff
test_change_point_tiff = """
if os.path.exists("change_point.tiff"):
    test.log_test('p', f"change_point.tiff found")
else:
    test.log_test('f', f"change_point.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(change_point_significance, 'change_point'", 
                   test_confidence_level_tiff)

# Confirm creation of CL_x_CP.tiff
test_CL_x_CP_tiff = """
if os.path.exists("CL_x_CP.tiff"):
    test.log_test('p', f"CL_x_CP.tiff found")
else:
    test.log_test('f', f"CL_x_CP.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(confidence_level*change_point_significance", 
                   test_CL_x_CP_tiff)

# Confirm creation of change_point_thresh.png
test_change_point_thresh_png = """
if os.path.exists("change_point_thresh.png"):
    test.log_test('p', f"change_point_thresh.png found")
else:
    test.log_test('f', f"change_point_thresh.png NOT found")
"""
test.add_test_cell("plt.savefig('change_point_thresh',", 
                   test_change_point_thresh_png)

# Confirm creation of change_point_thresh.tiff
test_change_point_thresh_tiff = """
if os.path.exists("change_point_thresh.tiff"):
    test.log_test('p', f"change_point_thresh.tiff found")
else:
    test.log_test('f', f"change_point_thresh.tiff NOT found")
"""
test.add_test_cell("'change_point_thresh', coords, utm_zone, cmap='cool'", 
                   test_change_point_thresh_tiff)

# Confirm change_indices' and change_dates' values
test_change_indices_dates = """
test_change_indices = [32, 33, 34, 35, 36, 37, 39, 44, 45, 46, 47, 48]
test_change_dates = ['2017-01-10', '2017-01-22', '2017-02-03', '2017-02-15', 
                     '2017-02-27', '2017-03-11', '2017-04-04', '2017-06-03', 
                     '2017-06-15', '2017-06-27', '2017-07-09', '2017-07-21']
if change_indices == test_change_indices:
    test.log_test('p', f"change_indices == {test_change_indices}")
else:
    test.log_test('f', f"change_indices == {change_indices}, NOT {test_change_indices}")
if change_dates == test_change_dates:
    test.log_test('p', f"change_dates == {test_change_dates}")
else:
    test.log_test('f', f"change_dates == {change_dates}, NOT {test_change_dates}")
"""
test.add_test_cell("change_indices = list(np.unique(change_point_index))",
                   test_change_indices_dates)

# Confirm creation of change_dates.png
test_change_dates_png = """
if os.path.exists("change_dates.png"):
    test.log_test('p', f"change_dates.png found")
else:
    test.log_test('f', f"change_dates.png NOT found")
"""
test.add_test_cell("plt.savefig('change_dates',", 
                   test_change_dates_png)

# Confirm creation of change_dates.tiff
test_change_dates_tiff = """
if os.path.exists("change_dates.tiff"):
    test.log_test('p', f"change_dates.tiff found")
else:
    test.log_test('f', f"change_dates.tiff NOT found")
"""
test.add_test_cell("geotiff_from_plot(change_point_index, 'change_dates'", 
                   test_change_dates_tiff)

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