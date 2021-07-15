# Alaska Satellite Facility
# ASF_Jupyter_Test.py
# Alex Lewandowski
# 6-25-2020

import ast
import astor
import inspect
import json
import logging
import os
import re
import sys
from io import StringIO
import contextlib


def is_braced(string: str) -> bool:
    """
    returns: True if string starts with { and ends with }
    """
    regex = '({)[\S]*(})'
    return re.search(regex, string) is not None


def get_base_var(var: str) -> str:
    """
    takes: a string of code for an assignment in python,
           with or without leading whitespaces.
           (ex: "    variable = 'a value'")
    returns: the variable name with no whitespaces.
    """
    regex = "^[ |A-z|0-9]*"
    return (re.search(regex, var).group(0)).replace(" ", "")


def is_f_string(string: str) -> bool:
    """
    returns True if string starts with f", f\"\"\", f', or f'''
    """
    f_regex = "^(f\"\"\"|f'''|f\"|f')"
    return re.search(f_regex, string) is not None


def search_subscriptable_start(line: str):
    regex = "^\w*(\[\w*)\.?(\].)?"
    results = re.search(regex, line)
    if results:
        t = results.group(0)
        return results.group(0)
    else:
        return ""


def count_leading_whitespaces(string: str) -> int:
    """
    returns the number of leading whitespaces in a string
    """
    count = 0
    for char in string:
        if char == ' ':
            count += 1
        else:
            break
    return count


def get_assignment_start(line: str):
    """
    line: a string of python code
    returns: result search string or empty string if search fails
    """
    regex = "^[^(=]*[= |=]{2}"
    result = re.search(regex, line)
    if result:
        return result.group(0)
    return ""


def add_newline(code: str) -> str:
    """
    code: a string
    returns: code with appended newline, if not already present
    """
    if len(code) > 0 and code[-1] != "\n":
        code = f"{code}\n"
    return code


@contextlib.contextmanager
def std_out_io(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file, 'w')
    formatter = logging.Formatter('%(asctime)s --- %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


class SearchFailedException(Exception):
    """
    Raised when search returns no results
    """
    pass


class NotCommandLineMagicException(Exception):
    """
    Raised when command line magic string doesn't begin with '!'
    """
    pass


class WidgetTypeNotHandled(Exception):
    """
    Raised when encountering an unsupported widget
    """
    pass


class NotASTFunctionDef(Exception):
    """
    Raised when expecting an ast.FunctionDef object
    """
    pass


class NotASTCall(Exception):
    """
    Raised when expecting an ast.Call object
    """
    pass


class NotASTAssign(Exception):
    """
    Raised when expecting an ast.Assign object
    """
    pass


class NotWidgetValueLine(Exception):
    """
    Raised when trying to parse a widget value from code
    with no variable being assigned a widget value
    """
    pass


class Cell:
    def __init__(self, index, cell_type, contents):
        self.index = index
        self.cell_type = cell_type
        self.contents = contents


class ASFNotebookTest:
    def __init__(self, notebook_path: str, log_path: str):
        self.cells = self.get_cells(notebook_path)
        self.replace_cells = {}
        self.skip_cells = []
        self.test_cells = {}
        self.notebook_path = notebook_path
        prepend_dir = notebook_path.split('/')[-2] ###T.S. 7/15/2021
        self.info_logger = setup_logger('info_logger', f"{log_path}/{prepend_dir}_{os.path.basename(notebook_path).split('.')[0]}.info.log")
        self.test_logger = setup_logger('test_logger', f"{log_path}/{prepend_dir}_{os.path.basename(notebook_path).split('.')[0]}.test.log")
        self.code_dict = {}
        self.failed_count = 0
        self.exception_count = 0

    @staticmethod
    def get_loop_var_names(cell_code: list) -> list:
        """
        takes: a list of python code strings
        returns: a list of variable names associated with any
                 for loops (handles enumerate)
        """
        var_lst = []
        for i, line in enumerate(cell_code):
            if "for " in line and "enumerate" not in line:
                # print(f"line: {line}") ####################################
                var_lst.append(line.split(' ')[1])
            elif "enumerate" in line:
                var_lst.append(line.split(' ')[1][:-1])
                var_lst.append(line.split(' ')[1])
        return var_lst

    @staticmethod
    def magic_calls_var_containing_cmd(code: str, test_locals: dict) -> bool:
        """
        Provides lookahead capability to determine if a magic ! call uses code assigned
        to a variable in the same code cell

        code: string of python code
        test_locals: a dict of {variable names: values} assigned in the same cell as code.
        """
        if code[0] == '!':
            return code[2:] in test_locals
        else:
            print("Error: magic_calls_var_containing_cmd() was passed magic command string missing '!'")
            raise NotCommandLineMagicException

    @staticmethod
    def remove_dollar_magic(code_lst: list) -> list:
        """
        takes: a list of code strings
        returns: the list of code strings with any leading $ removed
        """
        for i, chunk in enumerate(code_lst):
            if len(chunk) > 0 and chunk[0] == '$':
                code_lst[i] = chunk[1:]
        return code_lst

    @staticmethod
    def subprocess_check_output_to_run(string: str) -> str:
        """
        takes: a string subprocess.check_output call with args
               stderr=subprocess.PIPE and shell=True
        returns: the call string as subprocess.run with arg capture_output=True
        """
        string = string.replace('check_output', 'run')
        return string.replace("stderr=subprocess.PIPE, shell=True)", "capture_output=True)")

    @staticmethod
    def f_str_to_arg_lst(f_str: str) -> list:
        """
        f_str: string representation of an f-string command line call
               ex: 'f"gdal_merge.py -o {output} {dup_dates[dup_date]}"'
        returns: formatted list of command line call elements for  use
                 as a subprocess arg list
        """
        args = f_str.split(' ')
        args[0] = args[0][2:]  # drop the f"
        args[len(args) - 1] = args[len(args) - 1][:-1]  # drop the "
        for i, arg in enumerate(args):
            if is_braced(arg):
                args[i] = f'{args[i]}'
        return args

    def find(self, string: str) -> list:
        """
        takes: a search string
        returns: a list of indices of code cells containing matching strings
        """
        results = []
        for i in self.cells:
            for line in self.cells[i].contents:
                if string in line:
                    results.append(i)
        if len(results) > 0:
            return results
        else:
            raise SearchFailedException(f"'{string}' not found")

    @staticmethod
    def get_cells(notebook_path: str):
        """
        takes: a path to a Jupyter Notebook
        returns: a list of all (code) Cell objects in notebook
        """
        doc = json.load(open(notebook_path))
        cells = dict()
        for i, c in enumerate(doc['cells']):
            if c['cell_type'] == "code":
                cell = Cell(i, c['cell_type'], c['source'])
                cells.update({i: cell})
        return cells

    def log_info(self, message: str):
        self.info_logger.info(message)

    def log_test(self, passed: str, message: str):
        if passed == 'p':
            self.test_logger.info(f"PASSED: {message}")
        elif passed == 'f':
            self.test_logger.info(f"**FAILED**: {message}")
            self.failed_count += 1
        elif passed == 'e':
            self.test_logger.info(f"EXCEPTION: {message}")
            self.exception_count += 1
        else:
            raise ValueError("Valid values for passed are p (passed), f (failed), and e (exception)")

    # TODO: decide how to handle duplicates. Only handle 1st and give warning?
    def replace_line(self, cell_search_str: str, line_search_str: str, replacement_code: str):
        """
        cell_search_str: a search string to locate cell
        line_search_str: a search string to locate line in cell to replace
        replacement_code: a string of replacement code

        updates self.replace_cells dictionary with altered code
        """
        index = self.find(cell_search_str)
        if len(index) > 0:
            index = index[0]
        else:
            raise SearchFailedException
        contents = self.cells[index].contents
        replacement_code = add_newline(replacement_code)
        for i, line in enumerate(contents):
            if line_search_str in line:
                contents[i] = replacement_code
        self.replace_cells.update({index: contents})

    # TODO: decide how to handle duplicates. Only handle 1st and give warning?
    def replace_cell(self, search_str, replacement_code=""):
        """
        search_str: a search string to locate cell
        replacement_code: a string of replacement cell code

        updates self.replace_cells dictionary with altered code
        """
        index = self.find(search_str)
        if len(index) > 0:
            index = index[0]
        else:
            print(f"Failed to find: \"{search_str}\"")
            raise SearchFailedException
        self.replace_cells.update({index: [replacement_code]})

    def add_test_cell(self, search_str: str, test_code: str):
        """
        search_str: a search string to locate cell
        test_code: custom test code to append to target cell

        updates self.test_cells dict with {target cell index: test_code}
        """
        cell_index = self.find(search_str)[0]          
        try:
            self.test_cells.update({cell_index: f"{self.test_cells[cell_index]}\n{test_code}"})
        except KeyError:
            self.test_cells.update({cell_index: test_code})

    @staticmethod
    def magic_to_subprocess(code: str) -> str:
        """
        code: a string of a ! Jupyter Notebook magic command
        returns: a string containing the ! command converted into 
                 a subprocess.call command 
        """
        space_count = count_leading_whitespaces(code)
        code = code[space_count + 1:]  # drop the ! magic char
        spaces = space_count * " "
        code_lst = code.split(' ')
        for i, code in enumerate(code_lst):
            if code[0] == '$':
                code_lst[i] = f'{{{code[1:]}}}'  # drop the $ magic
        code_str = (" ".join(code_lst)).replace('\n', '')
        return f'{spaces}subprocess.call(f"{code_str}", shell=True)\n'

    # TODO: handle more jupyter notebook magic commands as needed
    def prepare_code_cell(self, code: list) -> str:
        """
        code: a list of code strings in a code cell
        output: (optional) if "string", returns code as a newline delineated string
                else returns code as a list of strings
        returns: a string of code-cell code, ready to run, with
                 Jupyter Notebook magic commands handled
        """
        assignments = {}
        code_block = """"""
        for c in code:
            if len(c) > 0 and c[0] == '%' or "clear_output()" in c:
                continue
            assignment_regex = "^[ |A-z|0-9]*(=| =)[^=]"
            assignment = re.search(assignment_regex, c)
            if assignment:
                var_regex = "^[ |]*[A-z|0-9]*"
                var = re.search(var_regex, assignment.group(0))
                var = var.group(0).replace(' ', '', 1)
                base_var = get_base_var(var)
                val = c.replace(var, '')
                space_equals_regex = "^[ |]*[=][| ]*"
                val = val.replace(re.search(space_equals_regex, val).group(0), '')
                if val[-1] == '\n':
                    val = val[:-1]
                assignments.update({base_var: val})
            spaces = count_leading_whitespaces(c)
            if len(c) > 0 and c[spaces] == '!':
                c = self.magic_to_subprocess(c)
            code_block = f"""{code_block}{c}"""
        return code_block

    def assemble_code(self, stop_cell=None, include_tests=False) -> dict:
        """
        takes: an optional code cell index at which to stop
        returns: a dictionary {code-cell index: prepared code-cell string}
        """
        print("Assembling Notebook Test Code...")
        self.log_info("Begin Assembling Test Code")
        all_the_code = {-1: "import subprocess"}
        for index in self.cells:
            if not stop_cell or index <= stop_cell:
                if index in self.skip_cells:
                    continue
                elif index in self.replace_cells:
                    code = self.replace_cells[index]
                else:
                    code = self.cells[index].contents
                code = self.prepare_code_cell(code)
                if include_tests and index in self.test_cells:
                    code = f"{code}\n{self.test_cells[index]}\n"
                all_the_code.update({index: code})
        return all_the_code

    def get_calls(self, tree) -> list:
        """
        tree: an ast object
        returns: a list of ast.Call nodes
        """
        calls = []
        for node in ast.walk(tree):
            if type(node) == ast.Call:
                calls.append(node)
        return calls

    def get_format_calls(self, tree) -> list:
        """
        tree: ast object
        returns: a list of ast.Call nodes of str.format calls
        """
        calls = self.get_calls(tree)
        format_calls = []
        for call in calls:
            for node in ast.walk(call):
                if type(node) == ast.Call:
                    if type(node.func) == ast.Attribute and \
                            node.func.attr == 'format' and \
                            astor.to_source(node)[0:3] == '"""':
                        format_calls.append(node)
        return list(set(format_calls))
    
    def get_func_name(self, call_node: ast.Call) -> str:
        """
        call_node: an ast.Call object
        returns: the string name of the function being called
        """
        if type(call_node.func) == ast.Attribute:
            return call_node.func.attr
        elif type(call_node.func) == ast.Name:
            return call_node.func.id
        
    def get_assignment(self, assign_node: ast.Call) -> str:
        """
        call_node: an ast.Call object
        returns: the string name of the function being called
        """
        ass = ""
        if type(assign_node.targets[0]) == ast.Tuple:
            print(f"ASSIGN NODE TARGETS: {assign_node.targets[0].elts}") ######################################
            for elt in assign_node.targets[0].elts:
                ass = f"{ass}, {ass}"
            return ass[1:]
        elif type(assign_node) == ast.Assign:
            return assign_node.targets[0].id
        else: 
            raise NotASTAssign
        
    def has_widget(self, call_node: ast.Call) -> bool:
        """
        call_node: an ast.Call object
        returns: true if function call contains "widgets"
        """
        return 'widgets' in astor.to_source(call_node.func)
        
    def get_first_arg(self, func_def_node: ast.FunctionDef) -> str:
        """
        func_def_node: an ast.FunctionDef object
        returns: string name of first function argument
                 or an empty string if there are no args
        """
        if type(func_def_node) == ast.FunctionDef:
            if len(func_def_node.args.args) > 0:
                return func_def_node.args.args[0].arg
            else:
                return ""
        else:
            raise NotASTFunctionDef
            
    def get_first_param(self, call_node: ast.Call) -> str:
        if type(call_node) == ast.Call:
            if len(call_node.args) > 0:
                return astor.to_source(call_node.args[0])
            else:
                return ""
        else:
            raise NotASTCall
        
    def get_widget_type(self, call_node: ast.Call) -> str:
        """
        line: a string of python code, presumably containing a ipywidget call
        returns: widget type or None (if type not supported)
        """
        return call_node.func.attr
            
    def code_list_to_str(self, code_list: list) -> str:
        """
        code_list: list of code strings with correct indentation
        returns: newline seperated code string
        """
        code = ""
        for line in code_list:
            code = f"{code}{line}"
        return code

    def get_widget_details(self, cell_code: str, to_import: list = None) -> dict:
        """
        Assumes that the first arg for functions using widgets is the container
        used for the widget option arg.

        cell_code: a string of all code in a code cell
        to_import: a list of names of imports needed function call code inspections
        returns: {"type": widget_type, "container": widget_container} if a widget call is
                 discovered or an empty dict if none is found
        """
        if not to_import:
            to_import = ["asf_notebook"]
        for imp in to_import:
            try:
                exec(f"import {imp}")
            except ModuleNotFoundError:
                raise
        tree = ast.parse(cell_code)
        func_calls = self.get_calls(tree)
        widget_container = None
        widget_type = None
        assignment = None
        for call in func_calls:
            func_name = self.get_func_name(call) 
            for node in ast.walk(tree):
                if type(node) == ast.Assign and func_name in astor.to_source(node):
                    assignment = self.get_assignment(node)
                    break
            source = None
            try:
                source = ast.parse(inspect.getsource(eval(f"asf_notebook.{func_name}")))
            except NameError:
                pass
            except AttributeError:
                pass
            except TypeError:
                pass
            if source:
                for source_call in self.get_calls(source):
                    if self.has_widget(source_call):
                        widget_container = self.get_first_param(call)
                        widget_type = self.get_widget_type(source_call)
                        return {"func_name": assignment, 
                                "type": widget_type, 
                                "container": widget_container}
        return {}
    
    def replace_widget_dot_value(self, widget_name: str):
        """
        widget_name: the variable name of a widget
        void: replaces all occurrences of widget_name.value in self.code_dict
              with widget_name
        """
        value = f"{widget_name}.value"
        for code_cell_index in self.code_dict:
            self.code_dict[code_cell_index] = self.code_dict[code_cell_index].replace(value, widget_name)

    def widget_replacement_code(self, widget_details: dict) -> list:
        """
        widget_details: {'type' : string widget type name,
                         'container': variable name of widget data container}
        widget_name: the variable name of the widget
        returns: a list of command line runnable replacement code for a widget call
        """
        code = []
        if widget_details['type'] in ["RadioButtons", ]:
            replacement = [
                f'widget_container = {widget_details["container"]}',
                'for item in widget_container:',
                '    print(item)',
                f'{widget_details["func_name"]} = input("Enter your selection from the list above:")'
            ]
        elif widget_details['type'] in ["SelectionRangeSlider", ]:
            replacement = [
                'from datetime import datetime',
                f'widget_container = list(set({widget_details["container"]}))',
                'widget_container.sort()',
                'for item in widget_container:',
                '    print(item)',
                'print("Choose a Range:")',
                'widget_min = input(f"Enter the bottom of the range from the list above:")',
                'widget_max = input(f"Enter the top of the range from the list above:")',
                'try:',
                "    widget_min = datetime.strptime(widget_min, '%Y%m%d')",
                "    widget_max = datetime.strptime(widget_max, '%Y%m%d')",
                'except ValueError:',
                '    pass',
                f'{widget_details["func_name"]} = [widget_min, widget_max]'
            ]
        elif widget_details['type'] in ["SelectMultiple", ]:
            replacement = [
                f'widget_container = {widget_details["container"]}',
                'for item in widget_container:',
                '    print(item)',
                'widget_input = None',
                f'{widget_details["func_name"]}  = []',
                'print("Select one or many elements")',
                'while True:',
                '    widget_input = input("Add an element or hit enter to continue: ")',
                '    if widget_input == "":',
                '        break',
                f'    {widget_details["func_name"]}.append(widget_input)'
            ]
        else:
            raise WidgetTypeNotHandled
        for line in replacement:
            code.append(line)
        return code

    def notebook_to_script(self, stop_cell: int = None):
        """
        stop_cell: allows generation of a script up to and including a designated code cell
                   if None, scripts entire notebook
        """
        self.code_dict = self.assemble_code(stop_cell=stop_cell, include_tests=True)
        script = ["#!/usr/bin/env python3\n\n"]
        for code_cell_index in self.code_dict:
            print(f"CODE FOR WIDGET_DETAILS:{self.code_dict[code_cell_index]}") ###########################
            widget_details = self.get_widget_details(self.code_dict[code_cell_index])
            if len(widget_details) > 0:
                
                cell_lines = self.code_dict[code_cell_index].split('\n')
                for i, line in enumerate(cell_lines):
                    if widget_details['func_name'] in line:
                        for replacement_line in self.widget_replacement_code(widget_details):
                            script.append(f"{replacement_line}\n")
                        print(f"FUNCTION CALLING WIDGET LINE: {line}") ####################
                    else:
                        script.append(line)
            else:
                script.append(self.code_dict[code_cell_index])
        file_path = f"{self.notebook_path.split('.')[0]}.py"
        print(f"file_path: {file_path}")
        try:
            os.remove(file_path)
        except FileNotFoundError:
            print("filenotfound error")
            pass
        with open(file_path, 'a+') as outfile:
            for line in script:
                outfile.write(f"{line}\n")

    def output(self, code: str, cell_index: int, terminal: bool = False, log: bool = False):
        '''
        code: a string of code-cell code (one or many lines)
        cell_index: The code cell index
        terminal: True outputs to terminal
        log: True outputs to info log (test log handled in test script)
        '''
        if terminal:
            print("\n-----------------------------------------------------------------")
            print(f"Cell Index: {cell_index}")
            if "password" not in code and code != '':
                print(f"Code:\n {code}\n")
            elif code == '':
                print("SKIPPED CELL")
            else:
                print("Code Hidden. Contains a Password\n")
        if log:
            self.log_info("\n-----------------------------------------------------------------")
            self.log_info(f"Cell Index: {cell_index}")
            if "password" not in code and code != '':
                self.log_info(f"Code:\n {code}\n")
            elif code == '':
                self.log_info("SKIPPED CELL")
            else:
                self.log_info("Code Hidden. Contains a Password\n")
