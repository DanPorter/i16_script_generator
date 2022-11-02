# This Python code is encoded in: utf-8
"""
Scan generator functions for beamline I16

By Dan Porter, PhD
Diamond Light Source Ltd
2022
"""

import re
import datetime
import numpy as np

re_scan = re.compile(r' \w+ -?\d+\.?\d* -?\d+\.?\d* -?\d+\.?\d*')  # scannable, start, stop, step
re_scancn = re.compile(r' \w+ -?\d+\.?\d* \d+')  # scannable, step, nsteps
re_cscan = re.compile(r' \w+ -?\d+\.?\d* -?\d+\.?\d*')  # scannable, range, step
re_lists = re.compile(r'\[[^\[]+?\]|\([^\(]+?\)')
re_lists_or_float = re.compile(r'\[.+?\]|\(.+?\)|-?\.?\d+\.?\d*')
re_variables = re.compile(r'[a-zA-Z]\w*')
re_for = re.compile(r'in (.+?):')
re_tabs = re.compile(r'\A(\s*?)\S')
re_comment = re.compile(r'#.*|\"\"\".*|\'\'\'.*')
re_sleep = re.compile(r'sleep\s?\(\s*(\d+\.?\d*)|w\s?\(\s*(\d+\.?\d*)|pos\s+w\s+(\d+\.?\d*)')


def eval_tabpos(line, tablen=4):
    """Evaluate tab position of line, returns number of tabs"""
    out = re_tabs.findall(line)
    count = 0
    if out:
        out = out[0]
        if '\t' in out:
            count = out.count('\t')
        else:
            count = out.count(' ' * tablen)
    return count


class Script:
    """
    Script object
    """
    def __init__(self, filename):
        self.filename = filename
        self.top_comment = ''
        self.top_matter = ''


def load_script(filename):
    """
    Load a beamline measurement script
    """
    with open(filename) as f:
        # Comment section
        top_comment = ''  # comments at top of file
        top_matter = ''  # code at top of file (before scans and loops)
        code = ['']
        code_tab = [0]

        comment_zone = False
        def_zone = False
        for line in f:
            line = line.replace("\'", '\"')
            cmd = re_comment.sub('', line)  # remove comments
            if line.count('"""') % 2 == 1:
                comment_zone = not comment_zone
            if def_zone and (not line.strip() or eval_tabpos(line) > 0):
                def_zone = False
            if line.startswith('def') or line.startswith('class'):
                def_zone = True
            elif 'scan' in cmd or 'for' in cmd:
                code += ['']
                code_tab += [code_tab[-1]]
            elif 'for' in cmd:
                code += ['']
                code_tab += [code_tab[-1]+1]
            code += [line]
            if comment_zone or line.startswith('#'):
                code[-1] += line
            elif def_zone:
                if not line.strip() or eval_tabpos(line) > 0:

                def_zone = False





        loop_points = [1]
        tab_pos = 0
        for line in f:
            line = line.replace("'''", '"""')
            if line.count('"""') % 2 == 1:
                comment_zone = not comment_zone
            if comment_zone or not line.strip() or line.strip()[0] in ['#', '\'', '\"']:
                script_list[-1] += line
                continue
            if bracket_count > 0:
                bracket_str += line
                bracket_count += line.count('[') - line.count(']')
                if bracket_count == 0:
                    # Close bracket
                    # print('close bracket: %s = %s' % (bracket_var, bracket_str.replace('\n', '')))
                    # print('close bracket: %s =' % bracket_var, eval_range(bracket_str.replace('\n', '')) )
                    local_vars[bracket_var] = eval_range(bracket_str.replace('\n', ''))
                    bracket_str = ''

            # variable assignment inc. multiline
            if re_assignment.match(line):
                var, value = line.split('=')
                if line.count('[') > line.count(']'):
                    # print('Open bracket:', value)
                    bracket_count += line.count('[') - line.count(']')
                    bracket_var = var.strip()
                    bracket_str = value
                else:
                    local_vars[var.strip()] = eval(value, local_vars)

            # Tab position of line
            line_tab_pos = eval_tabpos(line)
            if line_tab_pos < tab_pos:
                loop_points = loop_points[:line_tab_pos+1]
            line = line.strip()

            # For loop in line
            if line.startswith('for'):
                for_time, for_points = eval_for(line, local_vars=local_vars)
                tot_time += for_time
                loop_points += [for_points]
                if print_script:
                    ln = '\t' * line_tab_pos + line + '  # %s points' % for_points
                    print(ln)
                continue

            # pos commands
            tot_loop_points = np.prod(loop_points)
            tot_time += line.count('pos') * tot_loop_points
            tot_time += eval_sleep(line)

            # scan commands
            if 'scan' in line:
                # replace any local variables with zeros
                for var in local_vars:
                    line = line.replace(var, '0')
                scan_seconds, scan_points = scan_command_time(line)
                tot_time += scan_seconds * tot_loop_points
                if print_script:
                    ln = '\t' * line_tab_pos + line + '  # %.4gs * %s' % (scan_seconds, tot_loop_points)
                    print(ln)
                continue
            if print_script:
                ln = '\t' * line_tab_pos + line
                print(ln)
        if print_script:
            print('----- End Time Script: %s -----' % filename)
            print(f'   Script total time: %s' % time_string(tot_time))
    return datetime.timedelta(seconds=tot_time)

