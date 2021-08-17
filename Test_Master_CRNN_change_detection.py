#!/usr/bin/env python3

from getpass import getpass
import shutil

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

# # Test build the network
# test_net_summary = '''
# actual_summary = str(net.summary())
# expected_summary = '
# Model: "model"
# __________________________________________________________________________________________________
# Layer (type)                    Output Shape         Param #     Connected to                     
# ==================================================================================================
# input_1 (InputLayer)            [(None, 3, 3, 6)]    0                                            
# __________________________________________________________________________________________________
# input_2 (InputLayer)            [(None, 3, 3, 6)]    0                                            
# __________________________________________________________________________________________________
# conv2d (Conv2D)                 (None, 1, 1, 32)     1760        input_1[0][0]                    
# __________________________________________________________________________________________________
# conv2d_1 (Conv2D)               (None, 1, 1, 32)     1760        input_2[0][0]                    
# __________________________________________________________________________________________________
# activation (Activation)         (None, 1, 1, 32)     0           conv2d[0][0]                     
# __________________________________________________________________________________________________
# activation_1 (Activation)       (None, 1, 1, 32)     0           conv2d_1[0][0]                   
# __________________________________________________________________________________________________
# reshape (Reshape)               (None, 1, 32)        0           activation[0][0]                 
# __________________________________________________________________________________________________
# reshape_1 (Reshape)             (None, 1, 32)        0           activation_1[0][0]               
# __________________________________________________________________________________________________
# concatenate (Concatenate)       (None, 2, 32)        0           reshape[0][0]                    
#                                                                  reshape_1[0][0]                  
# __________________________________________________________________________________________________
# lstm (LSTM)                     (None, 128)          82432       concatenate[0][0]                
# __________________________________________________________________________________________________
# dense (Dense)                   (None, 32)           4128        lstm[0][0]                       
# __________________________________________________________________________________________________
# dense_1 (Dense)                 (None, 1)            33          dense[0][0]                      
# ==================================================================================================
# Total params: 90,113
# Trainable params: 90,113
# Non-trainable params: 0
# __________________________________________________________________________________________________'
# if actual_summary == expected_summary:
#     test.log_test('p', f"actual_summary == {expected_summary}")
# else:
#     test.log_test('f', f"actual_summary == {actual_summary}, NOT {expected_summary}")
# '''
# test.add_test_cell("print('########## train the network... ##########')",test_net_summary)


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