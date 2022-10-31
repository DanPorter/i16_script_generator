"""
Timing funcitions
Interprets scans and scripts and provides execution time

Works by evaluating command strings using regular expressions.

By Dan Porter, PhD
Diamond Light Source Ltd
2022
"""

import numpy as np
import re
import datetime

from i16_script_generator.params import DETECTORS
from i16_script_generator.scandef import centred_scan_range, scannable_speed, scan_range

re_scan = re.compile(r' \w+ -?\d+\.?\d* -?\d+\.?\d* -?\d+\.?\d*')  # scannable, start, stop, step
re_scancn = re.compile(r' \w+ -?\d+\.?\d* \d+')  # scannable, step, nsteps
re_cscan = re.compile(r' \w+ -?\d+\.?\d* -?\d+\.?\d*')  # scannable, range, step
detector_list = [DETECTORS[det]['regex'] for det in DETECTORS]
re_detector = re.compile('|'.join([r'\s%s\s+\.?\d+\.?\d*' % det for det in detector_list]))
re_lists = re.compile(r'\[[^\[]+?\]|\([^\(]+?\)')
re_lists_or_float = re.compile(r'\[.+?\]|\(.+?\)|-?\.?\d+\.?\d*')
re_variables = re.compile(r'[a-zA-Z]\w*')
re_for = re.compile(r'in (.+?):')
re_tabs = re.compile(r'\A(\s*?)\S')
re_comment = re.compile(r'#.*')
re_sleep = re.compile(r'sleep\s?\(\s*(\d+\.?\d*)|w\s?\(\s*(\d+\.?\d*)|pos\s+w\s+(\d+\.?\d*)')


def frange(start, stop=None, step=1):
    if stop is None:
     stop = start
     start = 0
    return np.arange(start, stop+step, step).tolist()


def time_string(tot_seconds):
    """Return formatted str"""
    hours = tot_seconds // 3600
    mins = tot_seconds % 3600 // 60
    secs = tot_seconds % 60
    hours = '' if hours < 1 else '%.0f hours, ' % hours
    mins = '' if mins < 1 else '%.0f mins, ' % mins
    secs = '%.0f' % secs
    return '%s%s%ss' % (hours, mins, secs)


def scan_time(nsteps, srange, exposure=1, motor_speed=1, motor_stabilisation=1):
    """Return total scan time in seconds"""
    return (nsteps*exposure) + (nsteps*motor_stabilisation) + np.max(srange/motor_speed)


def scan_command_time_old(cmd):
    """Use regular expressions to determine scan time from command"""
    cmds = cmd.split(';')
    tot_time = 0
    tot_points = 0
    for cmd in cmds:
        if 'scan' not in cmd:
            continue
        cmd_time = 1
        cmd_points = 1
        # Type of scan
        if 'scancn' in cmd:
            for val in re_scancn.findall(cmd):
                cmd = cmd.replace(val, '')
                scannable, step, nsteps = val.split()
                step, nsteps, srange = centred_scan_range(float(step), int(nsteps))
                speed, stabilisation = scannable_speed(scannable)
                cmd_time *= scan_time(nsteps, srange, exposure=0, motor_speed=speed, motor_stabilisation=stabilisation)
                cmd_points *= nsteps
        elif 'cscan' in cmd:
            for val in re_cscan.findall(cmd):
                cmd = cmd.replace(val, '')
                scannable, halfrange, step = val.split()
                step, nsteps, srange = centred_scan_range(float(step), srange=float(halfrange)*2)
                speed, stabilisation = scannable_speed(scannable)
                cmd_time += scan_time(nsteps, srange, exposure=0, motor_speed=speed, motor_stabilisation=stabilisation)
                cmd_points *= nsteps
        elif 'pscan' in cmd:
            pass
        else:
            # scan/ rscan
            for val in re_scan.findall(cmd):
                cmd = cmd.replace(val, ' ')
                scannable, start, stop, step = val.split()
                start, stop, step, nsteps, srange = scan_range(float(start), float(stop), float(step))
                speed, stabilisation = scannable_speed(scannable)
                cmd_time += scan_time(nsteps, srange, exposure=0, motor_speed=speed, motor_stabilisation=stabilisation)
                cmd_points *= nsteps
        # Detector exposure
        for val in re_detector.findall(cmd):
            exposure = float(val.split()[-1])
            cmd_time += cmd_points * exposure
        tot_time += cmd_time
        tot_points += cmd_points
    return tot_time, tot_points


def scan_command_time(cmd, debug=False):
    """Use regular expressions to determine scan time from command"""
    cmds = cmd.split(';')
    tot_time = 0
    tot_points = 0
    for cmd in cmds:  # split multiplle commands by ;
        if 'scan' not in cmd:
            continue
        if debug:
            print('Scan command time: %s' % cmd)
        cmd_time = 1
        cmd_points = 1
        # split command by variable names e.g. scan, hkl, pil
        variables = re_variables.findall(cmd)
        params = re_variables.split(cmd)
        if len(params) < 2:
            continue
        scan_type = variables[0]
        # loop through variables analysing numbers/ lists after
        for var, param in zip(variables[1:], params[2:]):
            values = [eval_range(a) for a in re_lists_or_float.findall(param)]  # list of arrays
            if debug:
                print('  ', var, param, values)
            if len(values) == 3:
                # start, stop, step
                start, stop, step, nsteps, srange = scan_range(*values)
                speed, stabilisation = scannable_speed(var)
                if debug:
                    print('    scan', var, start, stop, step, nsteps, srange, speed, stabilisation)
                cmd_time += scan_time(nsteps, srange, exposure=0, motor_speed=speed, motor_stabilisation=stabilisation)
                cmd_points *= nsteps
            elif len(values) == 2 and scan_type == 'scancn':
                # step, nsteps
                step, nsteps, srange = centred_scan_range(step=values[0], nsteps=values[1])
                speed, stabilisation = scannable_speed(var)
                if debug:
                    print('    scancn', var, step, nsteps, srange, speed, stabilisation)
                cmd_time *= scan_time(nsteps, srange, exposure=0, motor_speed=speed, motor_stabilisation=stabilisation)
                cmd_points *= nsteps
            elif len(values) == 2 and scan_type == 'cscan':
                # halfrange, step
                # print('cscan', var, values)
                step, nsteps, srange = centred_scan_range(step=values[1], srange=values[0]*2)
                speed, stabilisation = scannable_speed(var)
                if debug:
                    print('    cscan', var, step, nsteps, srange, speed, stabilisation)
                cmd_time *= scan_time(nsteps, srange, exposure=0, motor_speed=speed, motor_stabilisation=stabilisation)
                cmd_points *= nsteps
            elif len(values) == 1:
                # detector exposure, should be after scans
                for val in re_detector.findall(' '.join(['', var, param])):
                    exposure = float(val.split()[-1])
                    if debug:
                        print('    detector %s: %s * %s' % (val, cmd_points, exposure))
                    cmd_time += cmd_points * exposure
        tot_time += cmd_time
        tot_points += cmd_points
    return tot_time, tot_points


def eval_range(cmd, local_vars=None):
    if local_vars is None:
        local_vars = {'frange': frange, 'dnp': np}
    # replace variable names with zeros
    for lst in re_lists.findall(cmd):
        new = re_variables.sub('0', lst)
        # new = re_lists.sub('0', new)
        cmd = cmd.replace(lst, new)
    # replace other variables
    for var in re_variables.findall(cmd):
        if var not in local_vars:
            cmd = cmd.replace(var, '[0]')
    # evaluate range
    try:
        array = np.asarray(eval(cmd, local_vars)).reshape(-1)
    except Exception as xx:
        print('Warning: Loop didnt complete: %s' % xx)
        array = np.array([])
    return array 


def eval_sleep(cmd):
    """Return time in seconds from sleep(x) or pos w x or w(x)"""
    return sum([float(n) if n else 0 for fn in re_sleep.findall(cmd) for n in fn])


def eval_for(line, time_per_point=1, local_vars=None):
    """Evaluate for loop time, returns time, nsteps"""
    range_find = re_for.findall(line)
    time = 0
    npoints = 0
    for range_str in range_find:
        array = eval_range(range_str, local_vars)
        npoints += len(array)
        time += len(array) * time_per_point
    return time, npoints


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


def time_script(filename, print_script=False):
    """
    Time a script, return datetime.timedelta
    """
    with open(filename) as f:
        if print_script:
            print('----- Time Script: %s -----' % filename)
        tot_time = 0
        comment_zone = False
        bracket_zone = False
        bracket_var = ''
        bracket_str = ''
        local_vars = {'frange': frange, 'dnp': np}
        loop_points = [1]
        tab_pos = 0
        for line in f:
            line = re_comment.sub('', line)  # remove comments
            if line.count('"""') % 2 == 1:
                comment_zone = not comment_zone
            if comment_zone or not line.strip() or line.strip()[0] in ['#', '\'', '\"']:
                continue
            if bracket_zone:
                bracket_str += line
                if line.count('[') != line.count(']') and line.count('[') < line.count(']'):
                    # Close bracket
                    # print('close bracket: %s = %s' % (bracket_var, bracket_str.replace('\n', '')))
                    # print('close bracket: %s =' % bracket_var, eval_range(bracket_str.replace('\n', '')) )
                    local_vars[bracket_var] = eval_range(bracket_str.replace('\n', ''))

            # variable assignment inc. multiline
            if '=' in line:
                var, value = line.split('=')
                if line.count('[') != line.count(']') and line.count('[') > line.count(']'):
                    # print('Open bracket:', value)
                    bracket_zone = True
                    bracket_var = var.strip()
                    bracket_str = value
                else:
                    local_vars[var.strip()] = eval(value,local_vars)

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

