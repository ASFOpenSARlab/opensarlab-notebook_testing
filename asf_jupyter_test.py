# Alaska Satellite Facility
# ASF_Jupyter_Test.py
# Alex Lewandowski
# 6-16-2020

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
    return re.search(regex, string)


def is_filename(expression: str) -> bool:
    regex = "^[ ]*[|A-Z|a-z|0-9|_|-]*[.][a-z]{1,6}"
    return re.search(regex, expression) != None


def is_format_string(code: str) -> bool:
    f_regex = "^(f\"\"\"|f'''|f\"|f')"
    if re.search(f_regex, code):
        return True
    return False


def is_expr(expression: str) -> bool:
    """
    takes: a string of code
    returns: True if looks like a function call, object reference,
             or an indexed subscriptable object
    """
    regex = "^[ |A-Z|a-z|0-9|_|-]*[.|[|(]"
    return re.search(regex, expression) != None


def get_base_var(var: str) -> str:
    """
    takes: a string of code for an assignment in python,
           with or without leading whitespaces.
           (ex: "    variable = 'a value'")
    returns: the variable name with no whitespaces.
    """
    regex = "^[ |A-z|0-9]*"
    return (re.search(regex, var).group(0)).replace(" ", "")


def is_f_string(code: str) -> bool:
    f_regex = "^(f\"\"\"|f'''|f\"|f')"
    if re.search(f_regex, code):
        return True
    return False


def count_leading_whitespaces(string: str) -> int:
    count = 0
    for char in string:
        if char == ' ':
            count += 1
        else:
            break
    return count


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
    formatter = logging.Formatter('%(asctime)s %(message)s --- ')
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


class Cell:
    def __init__(self, index, cell_type, contents):
        self.index = index
        self.cell_type = cell_type
        self.contents = contents


class ASFNotebookTest:
    def __init__(self, notebook_path):
        self.cells = self.get_cells(notebook_path)
        self.replace_cells = {}
        self.skip_cells = []
        self.test_cells = {}
        self.notebook_path = notebook_path

        # logging.basicConfig(filename=f"{notebook_path.split('.')[0]}.log",
        #                    format='%(asctime)s %(message)s',
        #                    filemode='w')

        self.info_logger = setup_logger('info_logger', f"{notebook_path.split('.')[0]}.info.log")

        self.test_logger = setup_logger('test_logger', f"{notebook_path.split('.')[0]}.test.log")

    @staticmethod
    def get_loop_var_names(cell_code: list) -> list:
        """
        takes: a list of python code strings
        returns: a list of variable names associated with any
                 for loops (handles enumerate)
        """
        var_lst = []
        for i, line in enumerate(cell_code):
            if "for" in line and "enumerate" not in line:
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
                args[i] = f'f"{args[i]}"'
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
        return results

    def get_cells(self, notebook_path: str):
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
            raise SearchFailedException
        self.replace_cells.update({index: [replacement_code]})

    def add_test_cell(self, search_str: str, test_code: str):
        """
        search_str: a search string to locate cell
        test_code: custom test code to append to target cell

        updates self.test_cells dict with {target cell index: test_code}
        """
        index = self.find(search_str)[0]
        self.test_cells.update({index: test_code})

    def log_info(self, message: str):
        self.info_logger.info(message)

    def log_test(self, message: str):
        self.test_logger.info(message)

    def convert_to_subprocess(self, code: str, assignments: dict, loop_vars: list) -> str:
        """
        code: a string of a ! Jupyter Notebook magic command
        assignments: a dict containing all assigned variable names and values in code cell
        loop_vars: a list of all loop variable names in code cell

        returns: a string containing the ! command converted into subprocess.check_output
                 and subprocess.run commands, which when called, tries to call 'check_output' first,
                 and then 'run' if it encounters subprocess.CalledProcessError
        """
        arg_lst = []
        args = None
        spaces = count_leading_whitespaces(code)
        code = code[spaces + 1:]  # drop the !
        code_lst = code.split(' ')
        code_lst = self.remove_dollar_magic(code_lst)

        for i, exp in enumerate(code_lst):
            if exp == "":
                continue
            if len(exp) > 0 and exp[-1] == '\n':
                code_lst[i] = exp[:-1]
            if code_lst[i] in assignments:
                code_lst[i] = assignments[code_lst[i]]
            elif code_lst[i] in locals():
                code_lst[i] = locals()[code_lst[i]]
        spaces = " " * spaces
        subprocess_cmd = f"process = subprocess.check_output(["
        if is_f_string(code_lst[0]):
            code_lst = self.f_str_to_arg_lst(code_lst[0])
        elif is_format_string((code[0])):
            pass
        for i, exp in enumerate(code_lst):
            if exp in loop_vars or (is_expr(exp) and not is_filename(exp)) or is_f_string(exp):
                if i == 0:
                    subprocess_cmd = f"{subprocess_cmd}{exp}"
                else:
                    subprocess_cmd = f"{subprocess_cmd}, {exp}"
            else:
                if i == 0:
                    subprocess_cmd = f"{subprocess_cmd}'{exp}'"
                else:
                    subprocess_cmd = f"{subprocess_cmd}, '{exp}'"
        subprocess_cmd = f"{subprocess_cmd}], stderr=subprocess.PIPE, shell=True)"
        prnt = f"print(process.decode(\"utf-8\"))"
        sub_run_cmd = f"{self.subprocess_check_output_to_run(subprocess_cmd)}"
        subprocess_cmd = f"""{spaces}{f"try:"}\n{spaces}    {subprocess_cmd}\n{spaces}    {prnt}
{spaces}{f"except subprocess.CalledProcessError:"}\n{spaces}    {f"try:"}
{spaces}        {sub_run_cmd}\n{spaces}    {f"except subprocess.CalledProcessError:"}
{spaces}        {f"raise"}\n"""
        return subprocess_cmd

    # FIXME: handle all jupyter notebook magic commands
    def prepare_code_cell(self, code: list) -> str:
        """
        code: a list of code strings in a code cell
        output: (optional) if "string", returns code as a newline delineated string
                else returns code as a list of strings
        returns: a string of code-cell code, ready to run, with
                 Jupyter Notebook magic commands handled
        """
        loop_vars = self.get_loop_var_names(code)
        assignments = {}
        code_block = """"""
        for c in code:
            if ('%%' in c and "\"" not in c) or \
                    "clear_output()" in c:
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
                c = self.convert_to_subprocess(c, assignments, loop_vars)
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

    def get_regex_result_or_empty_str(self, result):
        if result:
            # print(f"result.group(0): {result.group(0)}")
            return result.group(0)
        else:
            return ""

    def get_func_calls(self, line: str) -> list:
        calls = []
        regex = "(?<![A-Za-z])(([a-z][A-z|0-9]*[.])*[a-z][A-z]+)+\("
        matches = re.finditer(regex, line)
        if matches:
            for match in matches:
                calls.append(match.group(1))
        return calls

    def get_start_func_calls(self, line: str) -> list:
        """
        line: a python function call as a string
        returns: a list of lists of function calls, along with
                their occurance counts

        ex. line = "bla(get_the_list(thing, stuff(0)), stuff(8)"
            returns: [['bla(', 1], ['get_the_list(', 1], ['stuff(', 1], ['stuff(', 2]]
        """
        bookkeeping = []
        calls = []
        regex = "(?<![A-Za-z])(([a-z][A-z|0-9]*[.])*[a-z][A-z]+)+\("
        matches = re.finditer(regex, line)
        if matches:
            for match in matches:
                m = match.group(0)
                count = 1
                if m in bookkeeping:
                    count = bookkeeping.count(m) + 1
                # print(f"count: {count}")
                bookkeeping.append(m)
                calls.append([m, count])
        return calls

    def get_assignment_start(self, line: str):
        regex = "^[^(=]*[= |=]{2}"
        return re.search(regex, line)

    def get_calls(self, line: str):
        calls = []
        assignment = self.get_assignment_start(line)
        if assignment:
            line = line.replace(assignment.group(0), "")
        call_starts = self.get_start_func_calls(line)

        for call_start in call_starts:
            left_parenth = 1
            right_parenth = 0
            line_temp = line.split(call_start[0])[call_start[1]]
            for i, char in enumerate(line_temp):
                if char == '(':
                    left_parenth += 1
                elif char == ')':
                    right_parenth += 1
                if left_parenth == right_parenth:
                    function = f"{call_start[0]}{line_temp[:i]})"
                    calls.append(function)
                    break
        return calls

    def get_first_param(self, line: str) -> str:
        param = ""
        assignment = self.get_assignment_start(line)
        if assignment:
            line = line.replace(assignment.group(0), '')
        call_start = self.get_start_func_calls(line)[0]
        print(f"call start: {call_start}")
        line = line.replace(call_start[0], '')
        brace = False
        bracket = False
        parenth = False
        open_container = False
        for i, char in enumerate(line):
            if char in ['[', ']']:
                bracket = (char == '[')
            elif char in ['{', '}']:
                brace = (char == '{')
            elif char in ['(', ')']:
                parenth = (char == '(')
            open_container = brace or bracket or parenth
            if char == ',' and not open_container:
                break
            else:
                param = f"{param}{char}"
        return param

    # TODO: This only works for asf_notebook module functions.
    #       Find a better way to recognize widget options and
    #       modules needing to be imported when calling
    #       inspect.getsourcelines
    def replace_widget_code(self, line: str, to_import="asf_notebook"):
        """
        Assumes that the first arg for functions using widgets is the container
        used for the widget option arg.
        """
        exec(f"import {to_import}")
        # print(f"line: {line}")
        func_calls = self.get_calls(line)
        # print(f"func_calls: {func_calls}")
        widget_container = None
        for call in func_calls:
            # print(f"call: {call}")
            source = None
            try:
                source = inspect.getsourcelines(eval(f"asf_notebook.{call.split('(')[0]}"))[0]
            except NameError:
                pass
            except AttributeError:
                pass
            except TypeError:
                pass
            options = None
            if source:
                # print(f"source:{source}")
                for src_line in source:
                    if "widgets" in src_line:
                        # print(f"source: {source}")
                        print(f"call: {call}")
                        widget_container = self.get_first_param(call)
                        print(f"Widget Container: {widget_container}")
                        break
                        '''
                        print(f"line.split(call)[1]:{line.split(call)[1]}")

                        options_regex = "(?<=options=)[^,]*"
                        print(f"line: {line}")
                        options = re.search(options_regex, line)
                        if options:
                            options = options.group(0)

            if options:
                print(f"line: {line}")
                print(f"src_line: {src_line}")
                print(f"widget_options: {options}")
            '''

    def notebook_to_script(self, stop_cell=None):
        code_dict = self.assemble_code(stop_cell=stop_cell, include_tests=True)
        # print(f"code_lst: {code_lst}")
        script = ["#!/usr/bin/env python3\n\n"]
        for code_block in code_dict:
            # print(f"code_lst[code_block]: {code_dict[code_block]}")
            code_block_lines = code_dict[code_block].split("\n")
            for line in code_block_lines:
                # print(f"line: {line}")
                self.replace_widget_code(line)
                script.append(line)
        file_path = f"{self.notebook_path.split('.')[0]}.py"
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

        with open(file_path, 'a+') as outfile:
            for line in script:
                outfile.write(line)

    def output(self, code: dict, cell_index: int, terminal=False, log=False):
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
