# Alaska Satellite Facility
# ASF_Jupyter_Test.py
# Alex Lewandowski
# 6-12-2020

import json
import re


class Cell():
    def __init__(self, index, cell_type, contents):
        self.index = index
        self.cell_type = cell_type
        self.contents = contents


class SearchFailedException(Exception):
    """Raised when search returns no results"""
    pass


class NotCommandLineMagicException(Exception):
    """Raised when command line magic string doesn't begin with '!'"""
    pass


class OSL_Notebook_Test():
    def __init__(self, notebook_path):

        self.cells = self.get_cells(notebook_path)

        self.rtc_vvvh = ""
        self.rtc_s1tbh = ""
        self.insar = ""

        self.replace_cells = {}
        self.skip_cells = []

    def find(self, string):
        results = []
        for i in self.cells:
            for line in self.cells[i].contents:
                if string in line:
                    results.append(i)
        return results

    def get_cells(self, notebook_path):
        doc = json.load(open(notebook_path))
        cells = dict()
        for i, c in enumerate(doc['cells']):
            if c['cell_type'] == "code":
                cell = Cell(i, c['cell_type'], c['source'])
                cells.update({i: cell})
        return cells

    def replace_line(self, cell_search_str, line_search_str, replacement_code):
        index = self.find(cell_search_str)

        # TODO: decide how to handle duplicates,
        #      only handle 1st and give warning?

        if len(index) > 0:
            index = index[0]
        else:
            raise SearchFailedException
        contents = self.cells[index].contents
        replacement_code = self.add_missing_newline(replacement_code)
        for i, line in enumerate(contents):
            if line_search_str in line:
                contents[i] = replacement_code
        self.replace_cells.update({index: contents})

    def replace_cell(self, search_str, code_list):
        index = self.find(search_str)

        # TODO: decide how to handle duplicates,
        #      only handle 1st and give warning?

        if len(index) > 0:
            index = index[0]
        else:
            raise SearchFailedException

        self.replace_cells.update({index: code_list})

    def skip_cell(self, search_str):
        index = self.find(search_str)

        # TODO: decide how to handle duplicates,
        #      only handle 1st and give warning?

        if len(index) > 0:
            index = index[0]
        else:
            raise SearchFailedException
        self.skip_cells.append(index)

    def add_missing_newline(self, code: str) -> str:
        if code[-1] != "\n":
            code = f"{code}\n"
        return code

    def remove_dollar_magic(self, code):
        code_lst = code.split(' ')
        for i, chunk in enumerate(code_lst):
            if len(chunk) > 0 and chunk[0] == '$':
                code_lst[i] = chunk[1:]
        return code_lst

    def count_leading_whitespaces(self, string):
        count = 0
        for char in string:
            if char == ' ':
                count += 1
            else:
                break
        return count

    def magic_calls_var_containing_cmd(self, code: str, test_locals: list):
        if code[0] == '!':
            return code[2:] in test_locals
        else:
            print("Error: magic_calls_var_containing_cmd() was passed magic command string missing '!'")
            raise NotCommandLineMagicException

    def is_f_string(self, code: str) -> bool:
        f_regex = "^(f\"\"\"|f'''|f\"|f')"
        if re.search(f_regex, code):
            return True
        return False

    def format_arg_list_f_str(self, args: list) -> list:
        for i, _ in enumerate(args):
            if len(args[i]) > 1:
                if args[i][:2] == 'f"':
                    args[i] = args[i][2:]
                if args[i][0] == '{' and args[i][-1] == '}':
                    args[i] = args[i][1:-1]
                if len(args[i]) > 3:
                    if args[i][0] == '{' and args[i][-3] == '}':
                        args[i] = args[i][1:-3]
                if args[i][-2:] == '"\n':
                    args[i] = args[i][:-2]
        return args

    def is_format_string(self, code: str) -> bool:
        f_regex = "^(f\"\"\"|f'''|f\"|f')"
        if re.search(f_regex, code):
            return True
        return False

    # TODO: Write it
    def format_arg_list_format_str(self, args: list) -> list:
        print(args)
        return args

    def convert_to_subprocess(self, code: str, assignments: dict, spaces: int):
        arg_lst = None
        code_lst = self.remove_dollar_magic(code[1:])
        for i, chunk in enumerate(code_lst):
            if len(chunk) > 0 and chunk[-1] == '\n':
                chunk = chunk[:-1]
            if chunk[1:] in assignments:
                args = assignments[chunk[1:]]
            elif chunk[1:] in locals():
                args = locals()[chunk[1:]]
            else:
                arg_lst = f'["{chunk[1:]}"]'
        spaces = " " * spaces
        if not arg_lst:
            args = args.split(' ')
        if self.is_f_string(args):
            arg_lst = self.format_arg_list_f_str(arg_lst)
        elif self.is_format_string(args):
            arg_lst = self.format_arg_list_format_str(arg_lst)
        subprocess_cmd = f"{spaces}process = subprocess.check_output({arg_lst}, stderr=subprocess.PIPE, shell=True)"
        prnt = f"\n{spaces}print(process.decode(\"utf-8\"))\n"
        subprocess_cmd = f"""{subprocess_cmd}{prnt}"""
        # print(f"subprocess_cmd:\n{subprocess_cmd}")  ###### DEBUGGING
        return subprocess_cmd

    def get_base_var(self, var: str):
        regex = "^( |)*\w*"
        return (re.search(regex, var).group(0)).replace(" ", "")

    def prepare_code_cell(self, code):
        assignments = {}
        code_block = """"""
        for c in code:
            if ('%%' in c and "\"" not in c) or \
                    "clear_output()" in c:
                continue
            assignment_regex = "^[ |A-z]*(=| =)[^=]"
            assignment = re.search(assignment_regex, c)
            if assignment:
                var_regex = "^[ |]*[A-z]*"
                var = re.search(var_regex, assignment.group(0))
                var = var.group(0).replace(' ', '', 1)
                base_var = self.get_base_var(var)
                val = c.replace(var, '')
                space_equals_regex = "^[ |]*[=][| ]*"
                val = val.replace(re.search(space_equals_regex, val).group(0), '')
                # print(f"BASE_VAR: '{base_var}'")  ########### DEBUG
                # print(f"VAL: '{val}'")            ########### DEBUG
                assignments.update({base_var: val})
            spaces = self.count_leading_whitespaces(c)
            if c[spaces] == '!':
                c = self.convert_to_subprocess(c, assignments, spaces)
            code_block = f"""{code_block}{c}"""
        return code_block

    def assemble_test_code(self, stop_cell=None):
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

