#!/usr/bin/env python3

from getpass import getpass
from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io

username = input("Earthdata Username: ")
password = getpass("Earthdata Password: ")

pth = "/home/jovyan/notebooks/notebook_testing_dev/Prepare_Data_Stack_Hyp3.ipynb"
test = ASFNotebookTest(pth)

######### REPLACE CELLS ###########

test.replace_cell("login = EarthdataLogin()",
                  f"login = EarthdataLogin(username='{username}', password='{password}')")

data_dir = """
data_dir = "NOTEBOOK_TESTING"
try:
    shutil.rmtree(data_dir)
except FileNotFoundError:
    pass
os.mkdir(data_dir)
"""
test.replace_cell("data_dir = input_path", data_dir)

test.replace_line("group_id = input", "group_id = input", "    group_id = ''\n")

download_urls = """
download_urls = ['https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170223T120417_20170223T120442_015411_0194AE_F18E-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170307T120417_20170307T120442_015586_0199F9_8DCA-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170307T120442_20170307T120507_015586_0199F9_40EA-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170319T120426_20170319T120451_015761_019F2B_3A67-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170331T120426_20170331T120451_015936_01A461_2F7D-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170412T120427_20170412T120444_016111_01A9AE_156D-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170424T120428_20170424T120453_016286_01AF0F_DDC2-POEORB-30m-power-rtc-gamma.zip']
"""
'''
download_urls = """
download_urls = ['https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170223T120417_20170223T120442_015411_0194AE_F18E-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma.zip', 
                 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20170307T120417_20170307T120442_015586_0199F9_8DCA-POEORB-30m-power-rtc-gamma.zip']
"""
'''
test.replace_cell("download_urls = []", download_urls)

download = f'''
product_count = 1
for url in download_urls:
    print(f"Product Number {{product_count}} of {{len(download_urls)}}:")
    product_count += 1
    product = url.split('/')[5]
    filename = f"{{products_path}}/{{product}}"
    # if not already present, we need to download and unzip products
    if not os.path.exists(filename.split('.zip')[0]):
        print(f"{{product}} is not present.")
        print(f"Downloading from {{url}}")
        cmd = ["wget", "-c", "-q", "--show-progress", "--http-user={username}", "--http-password={password}", url]
        subprocess.run(cmd, capture_output=True)
        asf_unzip(products_path, product)
        print(f"product: {{product}}")
        try:
            os.remove(product)
        except OSError:
            pass
'''
test.replace_cell("cmd = get_wget_cmd(url, login)", download)

test.replace_cell("coord_choice = select_parameter", "coord_choice = 'UTM'")

process_type = """process_type = 2"""
test.replace_cell("subscription_info = login.api.get_subscriptions", process_type)

######## REPLACE SPECIFIC LINES IN CELLS #########

polarization = "polarization = 'VV and VH'"
test.replace_line("polarization = polarization_choice.value", "polarization = polarization_choice.value",
                  polarization)

test.replace_line("if coord_choice.value == 'UTM'", "if coord_choice.value == 'UTM':", "if coord_choice == 'UTM':")

test.replace_line("if coord_choice.value == 'UTM':", "if coord_choice.value == 'UTM':", "    if coord_choice == 'UTM':")

test.replace_line("elif coord_choice.value == 'Lat/Long':", "elif coord_choice.value == 'Lat/Long':",
                  "    elif coord_choice == 'Lat/Long':")

######### DECLARE SKIP CELLS ###########

skip_em = ["subscriptions = get_hyp3",
           "subscription_id = subscription_id",
           "Note: After selecting a date range",
           "get_slider_vals(date_picker)",
           "product_info = get_product_info",
           "path_choice = select_mult",
           "fp = path_choice.value",
           "valid_directions = set()",
           "polarizations = get_RTC_po",
           "direction = direction_choice.value",
           "subscription_info = login.a",
           "polarization_choice = select_parameter",
           ]
for search_str in skip_em:
    test.replace_cell(search_str)

######## ADD TEST CELLS ###########

test_reprojection = """
t_pth = "/home/jovyan/notebooks/notebooks/notebook_testing_dev/NOTEBOOK_TESTING/rtc_products/"
t_paths = [f"{t_pth}S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma/rS1A_IW_RT30_20170223T120442_G_gpn_VH.tif",
f"{t_pth}S1A_IW_GRDH_1SDV_20170223T120442_20170223T120507_015411_0194AE_AFD2-POEORB-30m-power-rtc-gamma/rS1A_IW_RT30_20170223T120442_G_gpn_VV.tif"]
for t_p in t_paths:
    if os.path.exists(t_p):
        test.log_test(f"PASSED: Reprojected file present: {t_p}")
    else:
        test.log_test(f"FAILED: Missing Reprojected File: {t_p}")
"""
test.add_test_cell("reproject_indicies = [i for", test_reprojection)

######## RUN THE NOTEBOOK AND TEST CODE #########

all_the_code = test.assemble_code(include_tests=True)
for cell_index in all_the_code:
    test.output(all_the_code[cell_index], cell_index, terminal=True, log=True)
    with std_out_io() as stdio:
        exec(all_the_code[cell_index])
    print(f"Output: {stdio.getvalue()}")
    test.log_info(f"Output: {stdio.getvalue()}")
