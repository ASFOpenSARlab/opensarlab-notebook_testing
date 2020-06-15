# Alaska Satellite Facility
# ASF_Jupyter_Test.py
# Alex Lewandowski
# 6-14-2020

import json
import re


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
    if code[-1] != "\n":
        code = f"{code}\n"
    return code


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
            args = code_lst[0].split(' ')
            args[0] = args[0][2:]  # drop the f"
            args[len(args) - 1] = args[len(args) - 1][:-1]  # drop the "
            for i, arg in enumerate(args):
                if is_braced(arg):
                    args[i] = f'f"{args[i]}"'
            code_lst = args
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
        takes: a list of code strings in a code cell
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

    def assemble_test_code(self, stop_cell=None) -> dict:
        """
        takes: an optional code cell index at which to stop
        returns: a dictionary {code-cell index: prepared code-cell string}
        """
        print("Assembling Notebook Test Code...")
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
                all_the_code.update({index: code})
        return all_the_code
