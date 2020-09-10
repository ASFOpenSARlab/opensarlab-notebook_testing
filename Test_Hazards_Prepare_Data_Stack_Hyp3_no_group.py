#!/usr/bin/env python3

from getpass import getpass
from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = "/home/jovyan/notebooks/SAR_Training/English/Hazards/Prepare_Data_Stack_Hyp3.ipynb"
log_pth = "/home/jovyan/notebooks/asf_jupyter_notebook_testing"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
replace_data_dir = """
data_dir = "/home/jovyan/notebooks/asf_jupyter_notebook_testing/data_Test_Prepare_Data_Stack_Hyp3"
try:
    shutil.rmtree(data_dir)
except FileNotFoundError:
    pass
os.mkdir(data_dir)
"""
test.replace_cell("data_dir = input_path", replace_data_dir)

test.replace_line('analysis_directory = f"{os.getcwd()}/{data_dir}"',
                  'analysis_directory = f"{os.getcwd()}/{data_dir}"',
                  'analysis_directory = data_dir')

# Don't input a group id for testing
test.replace_line("group_id = input", "group_id = input", "    group_id = ''\n")

# Skip all cells inputing user defined values for filtering products to download
skip_em = ["login = EarthdataLogin()",
           "subscriptions = get_hyp3",
           "subscription_id = subscription_id",
           "Note: After selecting a date range",
           "date_range = get_slider_vals(date_picker)",
           "granule_names = get_subscription_granule_names_ids",
           "product_info = get_product_info",
           "path_choice = select_mult",
           "fp = path_choice.value",
           "valid_directions = set()",
           "polarizations = get_RTC_po",
           "direction = direction_choice.value",
           "subscription_info = login.a",
           "polarization_choice = select_parameter"]
for search_str in skip_em:
    test.replace_cell(search_str)
    
download = "!aws s3 cp s3://asf-jupyter-data/jamalpur_notebook_testing.zip jamalpur_notebook_testing.zip"
test.replace_cell("download_urls = []", download)

move_downloads = f'''
asf_unzip(os.getcwd(), "jamalpur_notebook_testing.zip")
products = glob.glob("jamalpur_notebook_testing/*")
for product in products:
    shutil.move(product, products_path, copy_function=shutil.copytree)
try:
    os.remove("jamalpur_notebook_testing.zip")
except OSError:
    pass
try:
    shutil.rmtree("jamalpur_notebook_testing")
except FileNotFoundError:
    pass
'''
test.replace_cell("cmd = get_wget_cmd(url, login)", move_downloads)

process_type = """process_type = 2"""
test.replace_cell("subscription_info = login.api.get_subscriptions", process_type)

test_polarization = "polarization = 'VV and VH'"
test.replace_line("polarization = polarization_choice.value", "polarization = polarization_choice.value",
                  test_polarization)

test.replace_line('coord_choice = select_parameter(["UTM", "Lat/Long"]', 
                  'coord_choice = select_parameter(["UTM", "Lat/Long"]',
                  "coord_choice = 'UTM'")

test.replace_line("if coord_choice.value == 'UTM'", "if coord_choice.value == 'UTM':", "if coord_choice == 'UTM':")


######### TESTS ###########

# Confirm tiff_paths
test_tiff_paths_1 = """
test_tiff_pths = ['rtc_products/S1A_IW_GRDH_1SDV_20170424T120428_20170424T120453_016286_01AF0F_DDC2-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170424T120428_G_gpn_VH.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170424T120428_20170424T120453_016286_01AF0F_DDC2-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170424T120428_G_gpn_VV.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170307T120442_20170307T120507_015586_0199F9_40EA-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170307T120442_G_gpn_VV.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170307T120442_20170307T120507_015586_0199F9_40EA-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170307T120442_G_gpn_VH.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170331T120426_20170331T120451_015936_01A461_2F7D-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170331T120426_G_gpn_VH.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170331T120426_20170331T120451_015936_01A461_2F7D-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170331T120426_G_gpn_VV.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170412T120427_20170412T120444_016111_01A9AE_156D-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170412T120427_G_gpn_VH.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170412T120427_20170412T120444_016111_01A9AE_156D-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170412T120427_G_gpn_VV.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170223T120417_20170223T120442_015411_0194AE_F18E-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170223T120417_G_gpn_VH.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170223T120417_20170223T120442_015411_0194AE_F18E-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170223T120417_G_gpn_VV.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170319T120426_20170319T120451_015761_019F2B_3A67-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170319T120426_G_gpn_VH.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170319T120426_20170319T120451_015761_019F2B_3A67-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170319T120426_G_gpn_VV.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170307T120417_20170307T120442_015586_0199F9_8DCA-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170307T120417_G_gpn_VV.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170307T120417_20170307T120442_015586_0199F9_8DCA-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170307T120417_G_gpn_VH.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170223T120442_G_gpn_VV.tif', 'rtc_products/S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170223T120442_G_gpn_VH.tif']
if tiff_paths == test_tiff_pths:
    test.log_test('p', f"tiff_paths == {test_tiff_pths}")
else:
    test.log_test('f', f"tiff_paths == {tiff_paths}, NOT {test_tiff_pths}")
"""
test.add_test('tiff_pth = f"{rtc_path}/*/*{polarization[0]}*.tif*"',
                   test_tiff_paths_1)
                   

# Confirm utm_zones and utm_types
test_utm = """
test_zones = ['32646', '32646', '32645', '32645', '32646', '32646', '32646', '32646', 
              '32646', '32646', '32646', '32646', '32646', '32646', '32645', '32645']
test_types = ['EPSG', 'EPSG', 'EPSG', 'EPSG', 'EPSG', 'EPSG', 'EPSG', 'EPSG', 
              'EPSG', 'EPSG', 'EPSG', 'EPSG', 'EPSG', 'EPSG', 'EPSG', 'EPSG']
if utm_zones == test_zones:
    test.log_test('p', f"utm_zones == {test_zones}")
else:
    test.log_test('f', f"utm_zones == {utm_zones}, NOT {test_zones}")
if utm_types == test_types:
    test.log_test('p', f"utm_types == {test_types}")
else:
    test.log_test('f', f"utm_types == {utm_types}, NOT {test_types}")
"""
test.add_test("utm_zones = []", test_utm)

# Confirm predominant_utm == '32646'
test_predominant_utm = """
if predominant_utm == '32646':
    test.log_test('p', f"predominant_utm == '32646'")
else:
    test.log_test('f', f"predominant_utm == {predominant_utm}, NOT '32646'")           
"""
test.add_test("predominant_utm = utm_unique[a][0]", test_predominant_utm)
    
# Confirm creaation of reprojected tiffs
test_reprojection = """
test_rtc_pth = f"{data_dir}/rtc_products/"
test_tiff_paths = [f"{test_rtc_pth}S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma/rS1A_IW_RT30_20170223T120442_G_gpn_VH.tif",
                   f"{test_rtc_pth}S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma/rS1A_IW_RT30_20170223T120442_G_gpn_VV.tif"]
for test_p in test_tiff_paths:
    if os.path.exists(test_p):
        test.log_test('p', f"Reprojected file present: {test_p}")
    else:
        test.log_test('f', f"Missing Reprojected File: {test_p}")
"""
test.add_test("reproject_indicies = [i for", test_reprojection)

# Confirm dates hold correct values
test_dates = """
test_dates = ['20170424', '20170424', '20170307', '20170307', '20170331', '20170331', '20170412', '20170412',
              '20170223', '20170223', '20170319', '20170319', '20170307', '20170307', '20170223', '20170223']
if dates == test_dates:
    test.log_test('p', f"dates == {test_dates}")
else:
    test.log_test('f', f"dates == {dates}, NOT {test_dates}")
"""
test.add_test("dates = get_dates(tiff_paths)", test_dates)

# Confirm dup_date_batches hold correct values
test_dup_date_batches = """
test_dup_dates_btchs = [{'20170412': ' rtc_products/S1A_IW_GRDH_1SDV_20170412T120427_20170412T120444_016111_01A9AE_156D-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170412T120427_G_gpn_VV.tif', '20170307': ' rtc_products/S1A_IW_GRDH_1SDV_20170307T120442_20170307T120507_015586_0199F9_40EA-POEORB-30m-power-rtc-gamma/rS1A_IW_RT30_20170307T120442_G_gpn_VV.tif rtc_products/S1A_IW_GRDH_1SDV_20170307T120417_20170307T120442_015586_0199F9_8DCA-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170307T120417_G_gpn_VV.tif', '20170331': ' rtc_products/S1A_IW_GRDH_1SDV_20170331T120426_20170331T120451_015936_01A461_2F7D-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170331T120426_G_gpn_VV.tif', '20170424': ' rtc_products/S1A_IW_GRDH_1SDV_20170424T120428_20170424T120453_016286_01AF0F_DDC2-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170424T120428_G_gpn_VV.tif', '20170319': ' rtc_products/S1A_IW_GRDH_1SDV_20170319T120426_20170319T120451_015761_019F2B_3A67-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170319T120426_G_gpn_VV.tif', '20170223': ' rtc_products/S1A_IW_GRDH_1SDV_20170223T120417_20170223T120442_015411_0194AE_F18E-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170223T120417_G_gpn_VV.tif rtc_products/S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma/rS1A_IW_RT30_20170223T120442_G_gpn_VV.tif'}, 
                        {'20170412': ' rtc_products/S1A_IW_GRDH_1SDV_20170412T120427_20170412T120444_016111_01A9AE_156D-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170412T120427_G_gpn_VH.tif', '20170307': ' rtc_products/S1A_IW_GRDH_1SDV_20170307T120442_20170307T120507_015586_0199F9_40EA-POEORB-30m-power-rtc-gamma/rS1A_IW_RT30_20170307T120442_G_gpn_VH.tif rtc_products/S1A_IW_GRDH_1SDV_20170307T120417_20170307T120442_015586_0199F9_8DCA-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170307T120417_G_gpn_VH.tif', '20170331': ' rtc_products/S1A_IW_GRDH_1SDV_20170331T120426_20170331T120451_015936_01A461_2F7D-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170331T120426_G_gpn_VH.tif', '20170424': ' rtc_products/S1A_IW_GRDH_1SDV_20170424T120428_20170424T120453_016286_01AF0F_DDC2-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170424T120428_G_gpn_VH.tif', '20170319': ' rtc_products/S1A_IW_GRDH_1SDV_20170319T120426_20170319T120451_015761_019F2B_3A67-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170319T120426_G_gpn_VH.tif', '20170223': ' rtc_products/S1A_IW_GRDH_1SDV_20170223T120417_20170223T120442_015411_0194AE_F18E-POEORB-30m-power-rtc-gamma/S1A_IW_RT30_20170223T120417_G_gpn_VH.tif rtc_products/S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma/rS1A_IW_RT30_20170223T120442_G_gpn_VH.tif'}]
if dup_date_batches == test_dup_dates_btchs:
    test.log_test('p', f"dup_date_batches == {test_dup_dates_btchs}")
else:
    test.log_test('p', f"dup_date_batches == {dup_date_batches}, NOT {test_dup_dates_btchs}")
"""
test.add_test("for d in dup_date_batches:", test_dup_date_batches)

# Confirm that duplicate dates for each polarization were merged
test.replace_line('print(f"Duplicate dates still present!")',
                 'print(f"Duplicate dates still present!")',
                 '        test.log_test("f", f"Duplicate dates still present")')
test.replace_line('print(f"No duplicate dates are associated with {polar} polarization.")',
                  'print(f"No duplicate dates are associated with {polar} polarization.")',
                  '        test.log_test("p", f"No duplicate dates are associated with {polar} polarization.")') 

# Confirm updated tiff_paths after merging tiffs
test_merged_tiffs = """
test_merged_paths = ['rtc_products/S1A_IW_GRDH_1SDV_20170424T120428_20170424T120453_016286_01AF0F_DDC2-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170424T120428_G_gpn_VH.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170424T120428_20170424T120453_016286_01AF0F_DDC2-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170424T120428_G_gpn_VV.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170307T120442_20170307T120507_015586_0199F9_40EA-POEORB-30m-power-rtc-gamma/newrS1A_IW_RT30_20170307T120442_G_gpn_VV.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170307T120442_20170307T120507_015586_0199F9_40EA-POEORB-30m-power-rtc-gamma/newrS1A_IW_RT30_20170307T120442_G_gpn_VH.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170331T120426_20170331T120451_015936_01A461_2F7D-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170331T120426_G_gpn_VH.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170331T120426_20170331T120451_015936_01A461_2F7D-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170331T120426_G_gpn_VV.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170412T120427_20170412T120444_016111_01A9AE_156D-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170412T120427_G_gpn_VV.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170412T120427_20170412T120444_016111_01A9AE_156D-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170412T120427_G_gpn_VH.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170223T120417_20170223T120442_015411_0194AE_F18E-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170223T120417_G_gpn_VH.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170223T120417_20170223T120442_015411_0194AE_F18E-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170223T120417_G_gpn_VV.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170319T120426_20170319T120451_015761_019F2B_3A67-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170319T120426_G_gpn_VH.tif',
                     'rtc_products/S1A_IW_GRDH_1SDV_20170319T120426_20170319T120451_015761_019F2B_3A67-POEORB-30m-power-rtc-gamma/newS1A_IW_RT30_20170319T120426_G_gpn_VV.tif']
if tiff_paths == test_merged_paths:
    test.log_test('p', f"tiff_paths == {test_merged_paths}")
else:
    test.log_test('f', f"tiff_paths == {tiff_paths}, NOT {test_merged_paths}")
"""
test.add_test("if len(dates) != len(set(dates)):", test_merged_tiffs)
     



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
    