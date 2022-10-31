# This Python code is encoded in: utf-8
"""
Scan generator functions for beamline I16

By Dan Porter, PhD
Diamond Light Source Ltd
2022
"""

import numpy as np

from i16_script_generator.params import SCANNABLES, DETECTORS, EDGES


def detector_name(name):
    name = name.lower().replace(' ', '').replace('_', '').replace('-', '')
    if name in DETECTORS:
        return name
    for det_name in DETECTORS:
        if name in DETECTORS[det_name]['alt names']:
            return det_name
    return name


def detector(name, exposure=None):
    name = detector_name(name)
    if exposure is None:
        exposure = DETECTORS[name]['exposure']
    if name not in DETECTORS:
        return name
    return DETECTORS[name]['cmd'] % exposure


def detector_rois(name):
    name = detector_name(name)
    if 'rois' in DETECTORS[name]:
        return DETECTORS[name]['rois']
    return []


def det_desc(name):
    return '%12s | %s' % (name, DETECTORS[name]['desc'])


def scannable_desc(name):
    return '%12s | %s' % (name, SCANNABLES[name]['desc'])


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


def energy_desc(name):
    return '%7s | %s keV' % (name, EDGES[name])


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


def strfmt(value):
    return np.array2string(np.asarray(value), suppress_small=True, separator=',',
                           formatter={'float_kind': lambda x: "%.5g" % x, 'str_kind': lambda x: x})


def scangen(scan_type, *args, **kwargs):
    new_args = [strfmt(arg) for arg in args] + [strfmt(kwargs[arg]) for arg in kwargs]
    return ' '.join([scan_type] + new_args)


"================== Scan Types ======================"


def scan(scannable, start, stop, step):
    """Absolute scan"""
    return scangen('scan', **locals())


def scancn(scannable, step, nsteps):
    """Centred scan"""
    return scangen('scancn', **locals())


def cscan(scannable, step, srange):
    """Centred scan (range)"""
    return scangen('cscan', scannable, srange / 2, step)


def scan2d(scannable1, start1, stop1, step1, scannable2, start2, stop2, step2):
    """2D scan"""
    return "scan %s %.5g %.5g %.5g %s %.5g %.5g %.5g" % (
    scannable1, start1, stop1, step1, scannable2, start2, stop2, step2)


def theta2theta_vert(delta_start, delta_stop, delta_step, eta_start=None):
    """theta-twotheta scan"""
    if eta_start is None:
        eta_start = delta_start / 2.
    eta_step = delta_step / 2.
    return scangen('scan', 'delta', delta_start, delta_stop, delta_step, 'eta', eta_start, eta_step)


def theta2theta_horiz(gamma_start, gamma_stop, gamma_step, mu_start=None):
    """theta-twotheta scan"""
    if mu_start is None:
        mu_start = gamma_start / 2.
    mu_step = gamma_step / 2.
    return scangen('scan', 'gam', gamma_start, gamma_stop, gamma_step, 'mu', mu_start, mu_step)


def energy(min_energy, max_energy, energy_step=0.0005):
    """Energy scan"""
    return scan('energy', min_energy, max_energy, energy_step)


def energy_hkl(min_energy, max_energy, energy_step=0.0005):
    """Energy scan at fixed hkl"""
    return 'hkl_eng=hkl(); ' + energy(min_energy, max_energy, energy_step) + ' hkl hkl_eng'


def energy_pol(min_energy, max_energy, energy_step=0.0005, pol=0, pp=None):
    """Energy scan at fixed hkl with analyser at fixed pol"""
    analyser = '' if pol is None else ' pol %.5g' % pol
    polariser = '' if pp is None else ' PP400u %.10g' % pp
    return ''.join([energy_hkl(min_energy, max_energy, energy_step), analyser, polariser])


def psi(start, stop, step):
    """azimuthal scan"""
    return 'hkl_psi=hkl(); ' + scan('psic', start, stop, step) + ' hkl hkl_psi'


def psi_scancn(step, nsteps):
    """azimuthal scan"""
    return 'hkl_psi=hkl(); ' + scancn('psic', step, nsteps) + ' hkl hkl_psi'


