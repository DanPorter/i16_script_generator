"""
Script timing function for GDA
Based on i16_script_generator by Dan Porter
"""


import numpy as np
import re

SCANNABLES = {
    'eta': {'desc': 'sample rotation parallel to beam'},
    'chi': {'desc': 'sample rotation perpendicular to beam'},
    'phi': {'desc': 'sample rotation clockwise', 'speed': 5, 'stabilisation': 1},
    'mu': {'desc': 'base-sample rotation anti-clockwise'},
    'delta': {'desc': 'detector rotation vertical scattering'},
    'gam': {'desc': 'detector rotation horizontal scattering'},
    'psic': {'desc': 'sample rotation about scattering vector'},
    'th': {'desc': 'sample rotation parallel to beam (eta with offset)'},
    'hkl': {
        'desc': 'sample rotation vertical scattering',
        'start': '[1, 1, 1]',
        'stop': '[1, 1, 2]',
        'step': '[0, 0, 0.1]'
    },
    'energy': {
        'desc': 'incident photon energy',
        'start': 7.9,
        'stop': 8.1,
        'step': '0.001',
        'speed': 0.2,
        'stabilisation': 1,
    },
    'spara': {'desc': 'sample motion parallel to beam'},
    'sperp': {'desc': 'sample motion perpendicular to beam'},
    'sx': {'desc': 'sample translation x'},
    'sy': {'desc': 'sample translation y'},
    'sz': {'desc': 'sample height'},
    'x': {'desc': 'dummy motor', 'speed': 1000, 'stabilisation': 0},
    'y': {'desc': 'dummy motor', 'speed': 1000, 'stabilisation': 0},
    'z': {'desc': 'dummy motor', 'speed': 1000, 'stabilisation': 0},
}
DETECTORS = {
    'pilatus100k': {
        'cmd': 'pil %.5g',
        'desc': 'Pilatus3 100K photon-counting area detector',
        'exposure': 1,
        'alt names': ['pil', 'pil3', 'pilatus3', 'pil100k', 'pil3100k', 'pilatus3100k'],
        'rois': ['roi1', 'roi2', 'chiroi', 'delroi'],
        'regex': r'pil\w*?',
    },
    'diode': {
        'cmd': 'w %.5g diode',
        'desc': 'direct beam diode',
        'exposure': 0.1,
        'alt names': [],
        'regex': r'w',
    },
    'pilatus2m': {
        'cmd': 'pil2m %.5g',
        'desc': 'Pilatus 2M photon-counting large area detector',
        'exposure': 1,
        'alt names': ['pil2m'],
        'rois': [],
        'regex': r'pil2m\w*?',
    },
    'apd': {
        'cmd': 't %.5g',
        'desc': 'Advanced photo-diode point detector',
        'exposure': 1,
        'alt names': [],
        'regex': r't\w*?',
    },
    'merlin': {
        'cmd': 'merlin %.5g',
        'desc': 'Merlin high resolution photon-counting area detector',
        'exposure': 1,
        'alt names': ['quadmerlin'],
        'rois': ['mroi1', 'mroi2'],
        'regex': r'merlin\w*?',
    },
    'cam1': {
        'cmd': 'cam1 %.5g',
        'desc': 'direct beam camera',
        'exposure': 0.0001,
        'alt names': [],
        'rois': [],
        'regex': r'cam1\w*?',
    },
    'bpm': {
        'cmd': 'bpm %.5g',
        'desc': 'direct beam camera',
        'exposure': 0.0001,
        'alt names': [],
        'rois': ['bpmroi1'],
        'regex': r'bpm\w*?',
    },
}

re_scan = re.compile(r' \w+ -?\d+\.?\d* -?\d+\.?\d* -?\d+\.?\d*')  # scannable, start, stop, step
re_scancn = re.compile(r' \w+ -?\d+\.?\d* \d+')  # scannable, step, nsteps
re_cscan = re.compile(r' \w+ -?\d+\.?\d* -?\d+\.?\d*')  # scannable, range, step
detector_list = [DETECTORS[det]['regex'] for det in DETECTORS]
re_detector = re.compile('|'.join([r'\s%s\s+\.?\d+\.?\d*' % det for det in detector_list]))
re_lists = re.compile(r'\[[^\[]+?\]|\([^\(]+?\)')
re_lists_or_float = re.compile(r'\[.+?\]|\(.+?\)|-?\.?\d+\.?\d*')
re_variables = re.compile(r'[a-zA-Z]\w*')
re_assignment = re.compile(r'\w\s*=[^=]+')
re_for = re.compile(r'in (.+?):')
re_comment = re.compile(r'#.*')
re_sleep = re.compile(r'sleep\s?\(\s*(\d+\.?\d*)|w\s?\(\s*(\d+\.?\d*)|pos\s+w\s+(\d+\.?\d*)')


def scannable_speed(name):
    """returns speed, stabilisation_time for given scannable"""
    speed = 1.0
    stabilisation = 1.0
    if name in SCANNABLES:
        if 'speed' in SCANNABLES[name]:
            speed = SCANNABLES[name]['speed']
        if 'stabilisation' in SCANNABLES[name]:
            stabilisation = SCANNABLES[name]['stabilisation']
    return speed, stabilisation


def scan_range(start, stop=None, step=None, nsteps=None, srange=None):
    """
    Calculate scan range values given variable inputs
      start, stop, step, nsteps, srange = scan_range(start, stop, step, nsteps, srange)
    :param start: float : start position (required)
    :param stop: None or float : if none, requires 2 of step, nsteps, srange
    :param step: None or float : if none, requires 2 of stop, nsteps, srange
    :param nsteps: None or float : if none, requires 2 of stop, step, srange
    :param srange: None or float : if none, requires 2 of stop, step, nsteps
    :return: start, stop, step, nsteps, srange
    """
    start = np.asarray(start)
    if stop is None:
        if srange is None:
            srange = np.asarray(step) * (int(nsteps)-1)
        stop = start + srange
    srange = stop - start

    if step is None:
        step = srange / (nsteps - 1)
    # nsteps = len(np.arange(start, stop+step, step))
    with np.errstate(divide='ignore', invalid='ignore'):
        nsteps = int(np.nanmax(np.round((stop - start + step) / step)))
    return start, stop, step, nsteps, srange


def centred_scan_range(step=None, nsteps=None, srange=None):
    """
    Calculates centred scan range values, given varialbe inputs
        step, nsteps, srange = centred_scan_range(step, nsteps, srange)
    :param step: None or float : if none, requires nsteps, srange
    :param nsteps: None or float : if none, requires step, srange
    :param srange: None or float : if none, requires step, nsteps
    :return: step, nsteps, srange
    """
    start, stop, step, nsteps, srange = scan_range(start=0, stop=None, **locals())
    return step, nsteps, srange


def frange(start, stop=None, step=1):
    """interal frange function to pass to eval"""
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


def calc_tabpos(line, tablen=4):
    """Evaluate tab position of line, returns number of tabs"""
    line = line.replace(' ' * tablen, '\t')
    count = line[:len(line)-len(line.lstrip())].count('\t')
    return count


def scan_time(nsteps, srange, exposure=1., motor_speed=1., motor_stabilisation=1.):
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


def time_script_string(script_string):
    """
    Analyse a script and calcualte the run time by calculating scan length and number of loops.
    :param script_string: multiline string of script
    :return total_time: datetime.timedelta
    :return script: updated script string
    """
    output_str = []
    tot_time = 0
    comment_zone = False
    bracket_count = 0
    bracket_var = ''
    bracket_str = ''
    local_vars = {'frange': frange, 'dnp': np}
    loop_points = [1]
    tab_pos = 0
    tab = "    "
    script_string = script_string.replace('\t', tab)
    for line in script_string.splitlines():
        cmd = re_comment.sub('', line)  # remove comments
        cmd = cmd.replace("'''", '"""')
        if cmd.count('"""') % 2 == 1:
            comment_zone = not comment_zone
        if comment_zone or not cmd.strip() or cmd.strip()[0] in ['#', '\'', '\"']:
            output_str += [line]
            continue
        if bracket_count > 0:
            bracket_str += cmd
            bracket_count += cmd.count('[') - cmd.count(']')
            if bracket_count == 0:
                # Close bracket
                # print('close bracket: %s = %s' % (bracket_var, bracket_str.replace('\n', '')))
                # print('close bracket: %s =' % bracket_var, eval_range(bracket_str.replace('\n', '')) )
                local_vars[bracket_var] = eval_range(bracket_str.replace('\n', ''))
                bracket_str = ''

        # variable assignment inc. multiline
        if re_assignment.search(cmd):
            var, value = cmd.split('=')
            if cmd.count('[') > cmd.count(']'):
                bracket_count += cmd.count('[') - cmd.count(']')
                bracket_var = var.strip()
                bracket_str = value
            else:
                try:
                    value = value.split(';')[0]
                    local_vars[var.strip()] = eval(value, local_vars)  # breaks if e.g. hkl=hkl()
                except NameError:
                    local_vars[var.strip()] = 0

                    # Tab position of line
        line_tab_pos = calc_tabpos(cmd)
        if line_tab_pos < tab_pos:
            loop_points = loop_points[:line_tab_pos+1]
        cmd = cmd.strip()

        # For loop in line
        if cmd.startswith('for'):
            for_time, for_points = eval_for(cmd, local_vars=local_vars)
            tot_time += for_time
            loop_points += [for_points]
            output_str += [tab * line_tab_pos + cmd + '  # %s points' % for_points]
            continue

        # pos commands
        tot_loop_points = np.prod(loop_points)
        tot_time += cmd.count('pos') * tot_loop_points
        tot_time += eval_sleep(cmd)

        # scan commands
        if 'scan' in cmd:
            # replace any local variables with zeros
            orig = cmd
            for var in local_vars:
                cmd = cmd.replace(var, '0')
            scan_seconds, scan_points = scan_command_time(cmd)
            tot_time += scan_seconds * tot_loop_points
            output_str += [(tab * line_tab_pos) + orig + '  # %.4gs * %s' % (scan_seconds, tot_loop_points)]
            continue
        output_str += [line]
    return float(tot_time), '\n'.join(output_str)


def script_timer(filename, print_script=False):
    """
    Analyse a script and calcualte the run time by calculating scan length and number of loops.
    :param filename: str file to open
    :param print_script: Bool, if True, prints updated str
    :return total_time: datetime.timedelta
    """
    with open(filename) as f:
        tot_time, output_str = time_script_string(f.read())
        if print_script:
            print('----- Time Script: %s -----' % filename)
            print(output_str)
            print('----- End Time Script: %s -----' % filename)
        print(f'   Script total time: %s' % time_string(tot_time))


if __name__ == '__main__':
    script_timer('2022_07_29_1534.py', False)