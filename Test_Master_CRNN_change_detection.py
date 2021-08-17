#!/usr/bin/env python3

from getpass import getpass
import shutil
from PIL import Image
from asf_jupyter_test import ASFNotebookTest
from asf_jupyter_test import std_out_io


######### INITIAL SETUP #########

# Define path to notebook and create ASFNotebookTest object
notebook_pth = "/home/jovyan/notebooks/SAR_Training/English/Master/CRNN_change_detection.ipynb"
log_pth = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs"
test = ASFNotebookTest(notebook_pth, log_pth)

# Change data path for testing
_to_replace = 'base_path = "/home/jovyan/notebooks/SAR_Training/English/Master/data_CRNN_change_detection"'
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_data_CRNN_change_detection"
_replacement = f"base_path = (f\"{test_data_path}\")"
test.replace_line(_to_replace, _to_replace, _replacement)

# Get into the data sirectory
_to_replace = "asfn.new_directory(base_path)"
test_data_path = "/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev/test_data_CRNN_change_detection"
_replacement = f"os.chdir(f\"{test_data_path}\")"
test.replace_line(_to_replace, _to_replace, _replacement)

# Skip all cells inputing user defined values for filtering products to download
skip_em = ["var kernel = Jupyter.notebook.kernel;",
           "if env[0] != '/home/jovyan/.local/envs/machine_learning':"]

for search_str in skip_em:
    test.replace_cell(search_str)


######### TESTS ###########

# Verify shape of T1 image
test_T1 = '''
expected_shape = (402, 402, 6)
if imgT1.shape == expected_shape:
    test.log_test('p', f"imgT1.shape == {expected_shape}")
else:
    test.log_test('f', f"imgT1.shape == {imgT1.shape}, NOT {expected_shape}")
'''
test.add_test_cell("print('the shape of T1 image is: {}'.format(imgT1.shape))",test_T1)

# Verify shape of T2 image
test_T2 = '''
expected_shape = (402, 402, 6)
if imgT2.shape == expected_shape:
    test.log_test('p', f"imgT2.shape == {expected_shape}")
else:
    test.log_test('f', f"imgT2.shape == {imgT2.shape}, NOT {expected_shape}")
'''
test.add_test_cell("print('the shape of T2 image is: {}'.format(imgT2.shape))",test_T2)

# Verify shape of input tensors on training set
test_input_tensors = '''
expected_input_tensors_shape = (1000, 3, 3, 6)
if x_tra_t1.shape == expected_input_tensors_shape:
    test.log_test('p', f"x_tra_t1.shape == {expected_input_tensors_shape}")
else:
    test.log_test('f', f"x_tra_t1.shape == {x_tra_t1.shape}, NOT {expected_input_tensors_shape}")
'''
test.add_test_cell("print('the shape of input tensors on training set is: {}'.format(x_tra_t1.shape))",test_input_tensors)

# Verify shape of target tensor on training set
test_target_tensor = '''
expected_target_tensor_shape = (1000,)
if y_tra.shape == expected_target_tensor_shape:
    test.log_test('p', f"y_tra.shape == {expected_target_tensor_shape}")
else:
    test.log_test('f', f"y_tra.shape == {y_tra.shape}, NOT {expected_target_tensor_shape}")
'''
test.add_test_cell("print('the shape of target tensor on training set is: {}'.format(y_tra.shape))",test_target_tensor)

# Verify shape of input tensors on test set
test_input_test_tensors = '''
expected_input_test_tensors_shape = (21016, 3, 3, 6)
if x_test_t1.shape == expected_input_test_tensors_shape:
    test.log_test('p', f"x_test_t1.shape == {expected_input_test_tensors_shape}")
else:
    test.log_test('f', f"x_test_t1.shape == {x_test_t1.shape}, NOT {expected_input_test_tensors_shape}")
'''
test.add_test_cell("print('the shape of input tensors on training set is: {}'.format(x_test_t1.shape))",test_input_test_tensors)

# Verify shape of target tensor on test set 
test_target_test_tensor = '''
expected_target_test_tensor_shape = (21016,)
if y_test.shape == expected_target_test_tensor_shape:
    test.log_test('p', f"y_test.shape == {expected_target_test_tensor_shape}")
else:
    test.log_test('f', f"y_test.shape == {y_test.shape}, NOT {expected_target_test_tensor_shape}")
'''
test.add_test_cell("print('the shape of target tensor on training set is: {}'.format(y_test.shape))",test_target_test_tensor)

# Verify loss.png is created
test_loss_png = '''
if os.path.exists(f"{test_data_path}/loss.png"):
    test.log_test('p', f"{test_data_path}/loss.png found")
else:
    test.log_test('f', f"{test_data_path}/loss.png NOT found")
'''
test.add_test_cell("plt.plot(loss)",test_loss_png)

# Verify loss.png size
test_loss_png_size = '''
expected_loss_png_size = (1438,1244)
loss_im_size = Image.open(f"{test_data_path}/loss.png")
loss_png_size = loss_im_size.size
if loss_png_size == expected_loss_png_size:
    test.log_test('p', f"loss_png_size == (1438,1244)")
else:
    test.log_test('f', f"loss_png_size == {loss_png_size}, NOT (1438,1244)")
'''
test.add_test_cell("plt.plot(loss)",test_loss_png_size)

# Verify change_map_probability.png is created
test_change_map_probability_png = '''
if os.path.exists(f"{test_data_path}/change_map_probability.png"):
    test.log_test('p', f"{test_data_path}/change_map_ability.png found")
else:
    test.log_test('f', f"{test_data_path}/change_map_probability.png NOT found")
'''
test.add_test_cell("plt.imshow(change_map_prob)",test_change_map_probability_png)

# Verify change_map_probability.png size
test_change_map_probability_png_size = '''
expected_change_map_probability_png_size = (1600,1400)
change_map_probability_im_size = Image.open(f"{test_data_path}/change_map_probability.png")
change_map_probability_png_size = change_map_probability_im_size.size
if change_map_probability_png_size == expected_change_map_probability_png_size:
    test.log_test('p', f"change_map_probability_png_size == (1600,1400)")
else:
    test.log_test('f', f"change_map_probability_png_size == {change_map_probability_png_size}, NOT (1600,1400)")
'''
test.add_test_cell("plt.imshow(change_map_prob)",test_change_map_probability_png_size)

# Verify change_map_binary.png is created
test_change_map_binary_png = '''
if os.path.exists(f"{test_data_path}/change_map_binary.png"):
    test.log_test('p', f"{test_data_path}/change_map_binary.png found")
else:
    test.log_test('f', f"{test_data_path}/change_map_binary.png NOT found")
'''
test.add_test_cell("plt.imshow(change_map_binary)",test_change_map_binary_png)

# Verify change_map_binary.png size
test_change_map_binary_png_size = '''
expected_change_map_binary_png_size = (1600,1400)
change_map_binary_im_size = Image.open(f"{test_data_path}/change_map_binary.png")
change_map_binary_png_size = change_map_binary_im_size.size
if change_map_binary_png_size == expected_change_map_binary_png_size:
    test.log_test('p', f"change_map_binary_png_size == (1600,1400)")
else:
    test.log_test('f', f"change_map_binary_png_size == {change_map_binary_png_size}, NOT (1600,1400)")
'''
test.add_test_cell("plt.imshow(change_map_prob)",test_change_map_binary_png_size)




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