# This Python code is encoded in: utf-8
"""
tkinter GUI for i16_script_generator

By Dan Porter, PhD
Diamond Light Source Ltd
2022
"""
import tkinter as tk
from tkinter import ttk

from i16_script_generator.params import SCANNABLES, DETECTORS, EDGES, SCANOPTIONS
from i16_script_generator.scandef import scannable_desc, det_desc, energy_desc, scan, scan_range, strfmt, scancn, \
    centred_scan_range, cscan, theta2theta_horiz, theta2theta_vert, energy_pol, energy, scan2d, psi_scancn, psi, \
    detector, detector_rois, detector_name
from i16_script_generator.timing import scan_command_time, time_string
from i16_script_generator.tkwidgets import TF, BF, SF, MF, bkg, ety, btn, opt, btn_active, opt_active, txtcol, ety_txt, \
    SelectionBox


def select_scannable(parent):
    """Returns scannable name"""

    options = [scannable_desc(name) for name in SCANNABLES]
    out = SelectionBox(parent, options, title='Scannables', multiselect=False).show()
    name = out[0].split('|')[0].strip()
    return name


def select_detector(parent):
    """Returns detector name"""

    options = [det_desc(name) for name in DETECTORS]
    out = SelectionBox(parent, options, title='Detectors', multiselect=False).show()
    name = out[0].split('|')[0].strip()
    return name


def select_energy(parent):
    """Returns detector name"""

    options = [energy_desc(name) for name in EDGES]
    out = SelectionBox(parent, options, title='Resonant Edges', multiselect=False).show()
    name = out[0].split('|')[0].strip()
    return name


class AbsoluteScan:
    """Absolute Scan tab"""

    def __init__(self, parent, update_function=None):
        self.parent = parent
        if update_function is None:
            self.update_function = lambda: None
        else:
            self.update_function = update_function
        self.scannable = tk.StringVar(parent, 'x')
        self.scan_start = tk.StringVar(parent, 0)
        self.scan_stop = tk.StringVar(parent, 1)
        self.scan_step = tk.StringVar(parent, 0.1)
        self.scan_nsteps = tk.StringVar(parent, 11)
        self.scan_range = tk.StringVar(parent, 1)

        frm = ttk.Frame(parent)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = ttk.Label(frm, text='Scannable:', font=SF)
        var.pack(side=tk.LEFT)
        var = tk.Entry(frm, textvariable=self.scannable, font=TF, width=14, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Button(frm, text='Select', font=BF, width=4, command=self.but_scannable,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=4, ipadx=4)
        var = ttk.Label(frm, text='Start:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_start, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_start)
        var.bind('<KP_Enter>', self.ety_scan_start)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Stop:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_stop, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_stop)
        var.bind('<KP_Enter>', self.ety_scan_stop)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Step:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_step, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_step)
        var.bind('<KP_Enter>', self.ety_scan_step)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Steps:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_nsteps, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_npoints)
        var.bind('<KP_Enter>', self.ety_scan_npoints)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Range:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_range, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range)
        var.bind('<KP_Enter>', self.ety_scan_range)
        var.pack(side=tk.LEFT, padx=4)

    def command(self):
        scannable = self.scannable.get()
        start = eval(self.scan_start.get())
        stop = eval(self.scan_stop.get())
        step = eval(self.scan_step.get())
        _, _, _, nsteps, srange = scan_range(start, stop, step)
        return scan(scannable, start, stop, step)

    def get_sss(self):
        start = self.scan_start.get()
        stop = self.scan_stop.get()
        step = self.scan_step.get()
        nsteps = self.scan_nsteps.get()
        srange = self.scan_range.get()

        inputs = {
            'start': eval(start),
            'stop': None if stop == '' else eval(stop),
            'step': None if step == '' else eval(step),
            'nsteps': None if nsteps == '' else eval(nsteps),
            'srange': None if srange == '' else eval(srange),
        }

        start, stop, step, nsteps, srange = scan_range(**inputs)
        self.scan_start.set(strfmt(start))
        self.scan_stop.set(strfmt(stop))
        self.scan_step.set(strfmt(step))
        self.scan_nsteps.set(strfmt(nsteps))
        self.scan_range.set(strfmt(srange))
        self.update_function()

    def ety_scan_start(self, event=None):
        self.get_sss()

    def ety_scan_stop(self, event=None):
        self.get_sss()

    def ety_scan_step(self, event=None):
        self.get_sss()

    def ety_scan_npoints(self, event=None):
        self.scan_step.set('')
        self.get_sss()

    def ety_scan_range(self, event=None):
        self.scan_stop.set('')
        self.get_sss()

    def but_scannable(self):
        """Select scannable"""
        opt = select_scannable(self.parent)
        if opt:
            self.scannable.set(opt)
            if 'start' in SCANNABLES[opt]:
                self.scan_start.set(SCANNABLES[opt]['start'])
            else:
                self.scan_start.set(0)
            if 'stop' in SCANNABLES[opt]:
                self.scan_stop.set(SCANNABLES[opt]['stop'])
            else:
                self.scan_stop.set(1)
            if 'step' in SCANNABLES[opt]:
                self.scan_step.set(SCANNABLES[opt]['step'])
            else:
                self.scan_step.set(0.1)
            self.get_sss()


class CentreScan:
    """Centred Scan tab"""

    def __init__(self, parent, update_function=None):
        self.parent = parent
        if update_function is None:
            self.update_function = lambda: None
        else:
            self.update_function = update_function
        self.scannable = tk.StringVar(parent, 'x')
        self.scan_step = tk.StringVar(parent, 0.01)
        self.scan_nsteps = tk.StringVar(parent, 31)
        self.scan_range = tk.StringVar(parent, 1)

        frm = ttk.Frame(parent)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = ttk.Label(frm, text='Scannable:', font=SF)
        var.pack(side=tk.LEFT)
        var = tk.Entry(frm, textvariable=self.scannable, font=TF, width=14, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Button(frm, text='Select', font=BF, width=4, command=self.but_scannable,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=4, ipadx=4)
        var = ttk.Label(frm, text='Step:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_step, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_step)
        var.bind('<KP_Enter>', self.ety_scan_step)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Steps:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_nsteps, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_npoints)
        var.bind('<KP_Enter>', self.ety_scan_npoints)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Range:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_range, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range)
        var.bind('<KP_Enter>', self.ety_scan_range)
        var.pack(side=tk.LEFT, padx=4)

    def command(self):
        scannable = self.scannable.get()
        step = eval(self.scan_step.get())
        nsteps = eval(self.scan_nsteps.get())
        return scancn(scannable, step, nsteps)

    def get_sss(self):
        step = self.scan_step.get()
        nsteps = self.scan_nsteps.get()
        srange = self.scan_range.get()

        inputs = {
            'step': None if step == '' else eval(step),
            'nsteps': None if nsteps == '' else eval(nsteps),
            'srange': None if srange == '' else eval(srange),
        }

        step, nsteps, srange = centred_scan_range(**inputs)
        self.scan_step.set(strfmt(step))
        self.scan_nsteps.set(strfmt(nsteps))
        self.scan_range.set(strfmt(srange))
        self.update_function()

    def ety_scan_step(self, event=None):
        self.scan_range.set('')
        self.get_sss()

    def ety_scan_npoints(self, event=None):
        self.scan_range.set('')
        self.get_sss()

    def ety_scan_range(self, event=None):
        self.get_sss()

    def but_scannable(self):
        """Select scannable"""
        opt = select_scannable(self.parent)
        if opt:
            self.scannable.set(opt)
            if 'step' in SCANNABLES[opt]:
                self.scan_step.set(SCANNABLES[opt]['step'])
            else:
                self.scan_step.set(0.1)
            self.get_sss()


class CentreScan2:
    """Centred Scan tab"""

    def __init__(self, parent, update_function=None):
        self.parent = parent
        if update_function is None:
            self.update_function = lambda: None
        else:
            self.update_function = update_function
        self.scannable = tk.StringVar(parent, 'x')
        self.scan_step = tk.StringVar(parent, 0.01)
        self.scan_nsteps = tk.StringVar(parent, 101)
        self.scan_range = tk.StringVar(parent, 1)

        frm = ttk.Frame(parent)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = ttk.Label(frm, text='Scannable:', font=SF)
        var.pack(side=tk.LEFT)
        var = tk.Entry(frm, textvariable=self.scannable, font=TF, width=14, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Button(frm, text='Select', font=BF, width=4, command=self.but_scannable,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=4, ipadx=4)
        var = ttk.Label(frm, text='Step:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_step, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_step)
        var.bind('<KP_Enter>', self.ety_scan_step)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Range:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_range, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range)
        var.bind('<KP_Enter>', self.ety_scan_range)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Steps:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_nsteps, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_npoints)
        var.bind('<KP_Enter>', self.ety_scan_npoints)
        var.pack(side=tk.LEFT, padx=4)

    def command(self):
        scannable = self.scannable.get()
        step = eval(self.scan_step.get())
        srange = eval(self.scan_range.get())
        return cscan(scannable, step, srange)

    def get_sss(self):
        step = self.scan_step.get()
        nsteps = self.scan_nsteps.get()
        srange = self.scan_range.get()

        inputs = {
            'step': None if step == '' else eval(step),
            'nsteps': None if nsteps == '' else eval(nsteps),
            'srange': None if srange == '' else eval(srange),
        }

        step, nsteps, srange = centred_scan_range(**inputs)
        self.scan_step.set(strfmt(step))
        self.scan_nsteps.set(strfmt(nsteps))
        self.scan_range.set(strfmt(srange))
        self.update_function()

    def ety_scan_step(self, event=None):
        self.get_sss()

    def ety_scan_range(self, event=None):
        self.scan_nsteps.set('')
        self.get_sss()

    def ety_scan_npoints(self, event=None):
        self.scan_step.set('')
        self.get_sss()

    def but_scannable(self):
        """Select scannable"""
        opt = select_scannable(self.parent)
        if opt:
            self.scannable.set(opt)
            if 'step' in SCANNABLES[opt]:
                self.scan_step.set(SCANNABLES[opt]['step'])
            else:
                self.scan_step.set(0.1)
            self.get_sss()


class Theta2ThetaScan:
    """Absolute Scan tab"""

    def __init__(self, parent, update_function=None):
        self.parent = parent
        if update_function is None:
            self.update_function = lambda: None
        else:
            self.update_function = update_function
        geometries = ['Vertical', 'Horizontal']
        self.geometry = tk.StringVar(parent, geometries[0])
        self.tth_start = tk.StringVar(parent, 6)
        self.tth_stop = tk.StringVar(parent, 20)
        self.tth_step = tk.StringVar(parent, 0.1)
        self.tth_nsteps = tk.StringVar(parent, 141)
        self.tth_range = tk.StringVar(parent, 14)
        self.th_start = tk.StringVar(parent, 3)
        self.th_offset = tk.StringVar(parent, 0)

        frm = ttk.Frame(parent)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = ttk.Label(frm, text='Geometry:', font=SF)
        var.pack(side=tk.LEFT)
        var = tk.OptionMenu(frm, self.geometry, *geometries, command=self.opt_geometry)
        var.config(font=SF, width=10, bg=opt, activebackground=opt_active)
        var["menu"].config(bg=opt, bd=0, activebackground=opt_active)
        var.pack(side=tk.LEFT, padx=4)

        frm2 = ttk.Frame(frm)
        frm2.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.tthfrm = tk.LabelFrame(frm2, text='delta')
        self.tthfrm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = ttk.Label(self.tthfrm, text='Start:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(self.tthfrm, textvariable=self.tth_start, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_start)
        var.bind('<KP_Enter>', self.ety_scan_start)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(self.tthfrm, text='Stop:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(self.tthfrm, textvariable=self.tth_stop, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_stop)
        var.bind('<KP_Enter>', self.ety_scan_stop)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(self.tthfrm, text='Step:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(self.tthfrm, textvariable=self.tth_step, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_step)
        var.bind('<KP_Enter>', self.ety_scan_step)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(self.tthfrm, text='Steps:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(self.tthfrm, textvariable=self.tth_nsteps, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_npoints)
        var.bind('<KP_Enter>', self.ety_scan_npoints)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(self.tthfrm, text='Range:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(self.tthfrm, textvariable=self.tth_range, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range)
        var.bind('<KP_Enter>', self.ety_scan_range)
        var.pack(side=tk.LEFT, padx=4)

        self.thfrm = tk.LabelFrame(frm2, text='eta')
        self.thfrm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = ttk.Label(self.thfrm, text='Start:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(self.thfrm, textvariable=self.th_start, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_theta_start)
        var.bind('<KP_Enter>', self.ety_theta_start)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(self.thfrm, text='Offset:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(self.thfrm, textvariable=self.th_offset, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_theta_offset)
        var.bind('<KP_Enter>', self.ety_theta_offset)
        var.pack(side=tk.LEFT, padx=4)

    def command(self):
        geometry = self.geometry.get()
        start = eval(self.tth_start.get())
        stop = eval(self.tth_stop.get())
        step = eval(self.tth_step.get())
        theta = eval(self.th_start.get())
        if geometry == 'Horizontal':
            return theta2theta_horiz(gamma_start=start, gamma_stop=stop, gamma_step=step, mu_start=theta)
        return theta2theta_vert(delta_start=start, delta_stop=stop, delta_step=step, eta_start=theta)

    def get_sss(self):
        start = self.tth_start.get()
        stop = self.tth_stop.get()
        step = self.tth_step.get()
        nsteps = self.tth_nsteps.get()
        srange = self.tth_range.get()
        offset = self.th_offset.get()

        inputs = {
            'start': eval(start),
            'stop': None if stop == '' else eval(stop),
            'step': None if step == '' else eval(step),
            'nsteps': None if nsteps == '' else eval(nsteps),
            'srange': None if srange == '' else eval(srange),
        }

        start, stop, step, nsteps, srange = scan_range(**inputs)
        offset = 0 if offset == '' else eval(offset)
        theta = offset+(start / 2)
        self.tth_start.set(strfmt(start))
        self.tth_stop.set(strfmt(stop))
        self.tth_step.set(strfmt(step))
        self.tth_nsteps.set(strfmt(nsteps))
        self.tth_range.set(strfmt(srange))
        self.th_start.set(theta)
        self.th_offset.set(offset)
        self.update_function()

    def opt_geometry(self, event=None):
        geometry = self.geometry.get()
        if geometry == 'Horizontal':
            self.tthfrm.configure(text="gamma")
            self.thfrm.configure(text="mu")
        else:
            self.tthfrm.configure(text="delta")
            self.thfrm.configure(text="eta")

    def ety_scan_start(self, event=None):
        self.get_sss()

    def ety_scan_stop(self, event=None):
        self.get_sss()

    def ety_scan_step(self, event=None):
        self.get_sss()

    def ety_scan_npoints(self, event=None):
        self.tth_step.set('')
        self.get_sss()

    def ety_scan_range(self, event=None):
        self.tth_stop.set('')
        self.get_sss()

    def ety_theta_start(self, event=None):
        tth_start = eval(self.tth_start.get())
        th_start = eval(self.th_start.get())
        offset = th_start - (tth_start/2)
        self.th_offset.set(offset)
        self.get_sss()

    def ety_theta_offset(self, event=None):
        self.get_sss()


class EnergyScan:
    """Absolute Energy Scan tab"""

    def __init__(self, parent, update_function=None):
        self.parent = parent
        if update_function is None:
            self.update_function = lambda: None
        else:
            self.update_function = update_function
        self.edge = tk.StringVar(parent, 'Select')
        self.scan_start = tk.StringVar(parent, 7.9)
        self.scan_stop = tk.StringVar(parent, 8.1)
        self.scan_step = tk.StringVar(parent, 0.001)
        self.scan_nsteps = tk.StringVar(parent, 201)
        self.scan_range = tk.StringVar(parent, 0.2)
        self.opt_hkl = tk.BooleanVar(parent, False)
        self.opt_pol = tk.BooleanVar(parent, False)
        self.pol = tk.DoubleVar(parent, 0)
        pols = ['σσ', 'σπ']
        self.pol_selection = tk.StringVar(parent, 'σσ')

        frm = ttk.Frame(parent)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = tk.Button(frm, textvariable=self.edge, font=BF, width=4, command=self.but_edge,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=4, ipadx=4)
        var = ttk.Label(frm, text='Start:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_start, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_start)
        var.bind('<KP_Enter>', self.ety_scan_start)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Stop:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_stop, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_stop)
        var.bind('<KP_Enter>', self.ety_scan_stop)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Step:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_step, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_step)
        var.bind('<KP_Enter>', self.ety_scan_step)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Steps:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_nsteps, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_npoints)
        var.bind('<KP_Enter>', self.ety_scan_npoints)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Range:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_range, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range)
        var.bind('<KP_Enter>', self.ety_scan_range)
        var.pack(side=tk.LEFT, padx=4)

        frm = ttk.Frame(parent)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)
        var = tk.Checkbutton(frm, text='hkl', variable=self.opt_hkl, font=SF)
        var.pack(side=tk.LEFT, padx=6)
        var = tk.Checkbutton(frm, text='Analyser:', variable=self.opt_pol, font=SF)
        var.pack(side=tk.LEFT, padx=6)
        var = tk.Entry(frm, textvariable=self.pol, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range)
        var.bind('<KP_Enter>', self.ety_scan_range)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.OptionMenu(frm, self.pol_selection, *pols, command=self.sel_pol)
        var.config(font=SF, width=10, bg=opt, activebackground=opt_active)
        var["menu"].config(bg=opt, bd=0, activebackground=opt_active)
        var.pack(side=tk.LEFT, padx=4)

    def command(self):
        start = eval(self.scan_start.get())
        stop = eval(self.scan_stop.get())
        step = eval(self.scan_step.get())

        if self.opt_hkl.get() or self.opt_pol.get():
            pol = self.pol.get() if self.opt_pol.get() else None
            return energy_pol(start, stop, step, pol=pol, pp=None)
        return energy(start, stop, step)

    def sel_pol(self, event=None):
        selection = self.pol_selection.get()
        if selection == 'σσ':
            self.pol.set(0)
        else:
            self.pol.set(90)
        self.opt_hkl.set(True)
        self.opt_pol.set(True)

    def get_sss(self):
        start = self.scan_start.get()
        stop = self.scan_stop.get()
        step = self.scan_step.get()
        nsteps = self.scan_nsteps.get()
        srange = self.scan_range.get()

        inputs = {
            'start': eval(start),
            'stop': None if stop == '' else eval(stop),
            'step': None if step == '' else eval(step),
            'nsteps': None if nsteps == '' else eval(nsteps),
            'srange': None if srange == '' else eval(srange),
        }

        start, stop, step, nsteps, srange = scan_range(**inputs)
        self.scan_start.set(strfmt(start))
        self.scan_stop.set(strfmt(stop))
        self.scan_step.set(strfmt(step))
        self.scan_nsteps.set(strfmt(nsteps))
        self.scan_range.set(strfmt(srange))
        self.update_function()

    def ety_scan_start(self, event=None):
        self.get_sss()

    def ety_scan_stop(self, event=None):
        self.get_sss()

    def ety_scan_step(self, event=None):
        self.get_sss()

    def ety_scan_npoints(self, event=None):
        self.scan_step.set('')
        self.get_sss()

    def ety_scan_range(self, event=None):
        self.scan_stop.set('')
        self.get_sss()

    def but_edge(self):
        """Select scannable"""
        opt = select_energy(self.parent)
        if opt:
            self.edge.set(opt)
            energy = EDGES[opt]
            step = eval(self.scan_step.get())
            nsteps = eval(self.scan_nsteps.get())
            srange = eval(self.scan_range.get())
            step, nsteps, srange = centred_scan_range(step, nsteps, srange)
            start = energy - srange / 2
            stop = energy + srange / 2
            self.scan_start.set(strfmt(start))
            self.scan_stop.set(strfmt(stop))
            self.scan_step.set(strfmt(step))
            self.scan_nsteps.set(strfmt(nsteps))
            self.scan_range.set(strfmt(srange))


class TwoDimScan:
    """Absolute Scan tab"""

    def __init__(self, parent, update_function=None):
        self.parent = parent
        if update_function is None:
            self.update_function = lambda: None
        else:
            self.update_function = update_function
        self.scannable = tk.StringVar(parent, 'x')
        self.scan_start = tk.StringVar(parent, 0)
        self.scan_stop = tk.StringVar(parent, 1)
        self.scan_step = tk.StringVar(parent, 0.1)
        self.scan_nsteps = tk.StringVar(parent, 11)
        self.scan_range = tk.StringVar(parent, 1)
        self.scannable2 = tk.StringVar(parent, 'y')
        self.scan_start2 = tk.StringVar(parent, -1)
        self.scan_stop2 = tk.StringVar(parent, 1)
        self.scan_step2 = tk.StringVar(parent, 0.1)
        self.scan_nsteps2 = tk.StringVar(parent, 21)
        self.scan_range2 = tk.StringVar(parent, 2)

        frm = ttk.LabelFrame(parent, text='Fast axis')
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = ttk.Label(frm, text='Scannable 1:', font=SF)
        var.pack(side=tk.LEFT)
        var = tk.Entry(frm, textvariable=self.scannable, font=TF, width=14, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Button(frm, text='Select', font=BF, width=4, command=self.but_scannable,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=4, ipadx=4)
        var = ttk.Label(frm, text='Start:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_start, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_start)
        var.bind('<KP_Enter>', self.ety_scan_start)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Stop:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_stop, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_stop)
        var.bind('<KP_Enter>', self.ety_scan_stop)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Step:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_step, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_step)
        var.bind('<KP_Enter>', self.ety_scan_step)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Steps:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_nsteps, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_npoints)
        var.bind('<KP_Enter>', self.ety_scan_npoints)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Range:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_range, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range)
        var.bind('<KP_Enter>', self.ety_scan_range)
        var.pack(side=tk.LEFT, padx=4)

        frm = ttk.LabelFrame(parent, text='Slow axis')
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = ttk.Label(frm, text='Scannable 2:', font=SF)
        var.pack(side=tk.LEFT)
        var = tk.Entry(frm, textvariable=self.scannable2, font=TF, width=14, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Button(frm, text='Select', font=BF, width=4, command=self.but_scannable2,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=4, ipadx=4)
        var = ttk.Label(frm, text='Start:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_start2, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_start2)
        var.bind('<KP_Enter>', self.ety_scan_start2)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Stop:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_stop2, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_stop2)
        var.bind('<KP_Enter>', self.ety_scan_stop2)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Step:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_step2, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_step2)
        var.bind('<KP_Enter>', self.ety_scan_step2)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Steps:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_nsteps2, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_npoints2)
        var.bind('<KP_Enter>', self.ety_scan_npoints2)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Range:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_range2, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range2)
        var.bind('<KP_Enter>', self.ety_scan_range2)
        var.pack(side=tk.LEFT, padx=4)

    def command(self):
        scannable1 = self.scannable.get()
        start1 = eval(self.scan_start.get())
        stop1 = eval(self.scan_stop.get())
        step1 = eval(self.scan_step.get())
        scannable2 = self.scannable2.get()
        start2 = eval(self.scan_start2.get())
        stop2 = eval(self.scan_stop2.get())
        step2 = eval(self.scan_step2.get())
        return scan2d(scannable1, start1, stop1, step1, scannable2, start2, stop2, step2)

    def get_sss(self):
        start = self.scan_start.get()
        stop = self.scan_stop.get()
        step = self.scan_step.get()
        nsteps = self.scan_nsteps.get()
        srange = self.scan_range.get()

        inputs = {
            'start': eval(start),
            'stop': None if stop == '' else eval(stop),
            'step': None if step == '' else eval(step),
            'nsteps': None if nsteps == '' else eval(nsteps),
            'srange': None if srange == '' else eval(srange),
        }

        start, stop, step, nsteps, srange = scan_range(**inputs)
        self.scan_start.set(strfmt(start))
        self.scan_stop.set(strfmt(stop))
        self.scan_step.set(strfmt(step))
        self.scan_nsteps.set(strfmt(nsteps))
        self.scan_range.set(strfmt(srange))
        self.update_function()

    def ety_scan_start(self, event=None):
        self.get_sss()

    def ety_scan_stop(self, event=None):
        self.get_sss()

    def ety_scan_step(self, event=None):
        self.get_sss()

    def ety_scan_npoints(self, event=None):
        self.scan_step.set('')
        self.get_sss()

    def ety_scan_range(self, event=None):
        self.scan_stop.set('')
        self.get_sss()

    def but_scannable(self):
        """Select scannable"""
        opt = select_scannable(self.parent)
        if opt:
            self.scannable.set(opt)
            if 'start' in SCANNABLES[opt]:
                self.scan_start.set(SCANNABLES[opt]['start'])
            else:
                self.scan_start.set(0)
            if 'stop' in SCANNABLES[opt]:
                self.scan_stop.set(SCANNABLES[opt]['stop'])
            else:
                self.scan_stop.set(1)
            if 'step' in SCANNABLES[opt]:
                self.scan_step.set(SCANNABLES[opt]['step'])
            else:
                self.scan_step.set(0.1)
            self.get_sss()

    def get_sss2(self):
        start = self.scan_start2.get()
        stop = self.scan_stop2.get()
        step = self.scan_step2.get()
        nsteps = self.scan_nsteps2.get()
        srange = self.scan_range2.get()

        inputs = {
            'start': eval(start),
            'stop': None if stop == '' else eval(stop),
            'step': None if step == '' else eval(step),
            'nsteps': None if nsteps == '' else eval(nsteps),
            'srange': None if srange == '' else eval(srange),
        }

        start, stop, step, nsteps, srange = scan_range(**inputs)
        self.scan_start2.set(strfmt(start))
        self.scan_stop2.set(strfmt(stop))
        self.scan_step2.set(strfmt(step))
        self.scan_nsteps2.set(strfmt(nsteps))
        self.scan_range2.set(strfmt(srange))
        self.update_function()

    def ety_scan_start2(self, event=None):
        self.get_sss2()

    def ety_scan_stop2(self, event=None):
        self.get_sss2()

    def ety_scan_step2(self, event=None):
        self.get_sss2()

    def ety_scan_npoints2(self, event=None):
        self.scan_step.set('')
        self.get_sss2()

    def ety_scan_range2(self, event=None):
        self.scan_stop.set('')
        self.get_sss2()

    def but_scannable2(self):
        """Select scannable"""
        opt = select_scannable(self.parent)
        if opt:
            self.scannable2.set(opt)
            if 'start' in SCANNABLES[opt]:
                self.scan_start2.set(SCANNABLES[opt]['start'])
            else:
                self.scan_start2.set(0)
            if 'stop' in SCANNABLES[opt]:
                self.scan_stop2.set(SCANNABLES[opt]['stop'])
            else:
                self.scan_stop2.set(1)
            if 'step' in SCANNABLES[opt]:
                self.scan_step2.set(SCANNABLES[opt]['step'])
            else:
                self.scan_step2.set(0.1)
            self.get_sss2()


class PsiScan:
    """Azimuthal Scan tab"""

    def __init__(self, parent, update_function=None):
        self.parent = parent
        if update_function is None:
            self.update_function = lambda: None
        else:
            self.update_function = update_function
        self.opt_cen = tk.BooleanVar(parent, False)
        self.scannable = tk.StringVar(parent, 'psic')
        self.scan_start = tk.StringVar(parent, 0)
        self.scan_stop = tk.StringVar(parent, 1)
        self.scan_step = tk.StringVar(parent, 0.1)
        self.scan_nsteps = tk.StringVar(parent, 11)
        self.scan_range = tk.StringVar(parent, 1)

        frm = ttk.Frame(parent)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        var = tk.Checkbutton(frm, text='Centred:', variable=self.opt_cen, font=SF)
        var.pack(side=tk.LEFT, padx=6)
        var = ttk.Label(frm, text='Start:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_start, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_start)
        var.bind('<KP_Enter>', self.ety_scan_start)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Stop:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_stop, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_stop)
        var.bind('<KP_Enter>', self.ety_scan_stop)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Step:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_step, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_step)
        var.bind('<KP_Enter>', self.ety_scan_step)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Steps:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_nsteps, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_npoints)
        var.bind('<KP_Enter>', self.ety_scan_npoints)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, text='Range:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm, textvariable=self.scan_range, font=TF, width=6, bg=ety, fg=ety_txt)
        var.bind('<Return>', self.ety_scan_range)
        var.bind('<KP_Enter>', self.ety_scan_range)
        var.pack(side=tk.LEFT, padx=4)

    def command(self):
        centre = self.opt_cen.get()
        if centre:
            step = eval(self.scan_step.get())
            nsteps = eval(self.scan_nsteps.get())
            return psi_scancn(step, nsteps)
        start = eval(self.scan_start.get())
        stop = eval(self.scan_stop.get())
        step = eval(self.scan_step.get())
        return psi(start, stop, step)

    def get_sss(self):
        start = self.scan_start.get()
        stop = self.scan_stop.get()
        step = self.scan_step.get()
        nsteps = self.scan_nsteps.get()
        srange = self.scan_range.get()

        inputs = {
            'start': eval(start),
            'stop': None if stop == '' else eval(stop),
            'step': None if step == '' else eval(step),
            'nsteps': None if nsteps == '' else eval(nsteps),
            'srange': None if srange == '' else eval(srange),
        }

        start, stop, step, nsteps, srange = scan_range(**inputs)
        self.scan_start.set(strfmt(start))
        self.scan_stop.set(strfmt(stop))
        self.scan_step.set(strfmt(step))
        self.scan_nsteps.set(strfmt(nsteps))
        self.scan_range.set(strfmt(srange))
        self.update_function()

    def ety_scan_start(self, event=None):
        self.get_sss()

    def ety_scan_stop(self, event=None):
        self.get_sss()

    def ety_scan_step(self, event=None):
        self.get_sss()

    def ety_scan_npoints(self, event=None):
        self.scan_step.set('')
        self.get_sss()

    def ety_scan_range(self, event=None):
        self.scan_stop.set('')
        self.get_sss()

    def but_scannable(self):
        """Select scannable"""
        opt = select_scannable(self.parent)
        if opt:
            self.scannable.set(opt)
            if 'start' in SCANNABLES[opt]:
                self.scan_start.set(SCANNABLES[opt]['start'])
            else:
                self.scan_start.set(0)
            if 'stop' in SCANNABLES[opt]:
                self.scan_stop.set(SCANNABLES[opt]['stop'])
            else:
                self.scan_stop.set(1)
            if 'step' in SCANNABLES[opt]:
                self.scan_step.set(SCANNABLES[opt]['step'])
            else:
                self.scan_step.set(0.1)
            self.get_sss()


class ScanOptions:
    """Create swappable menu's of additional scan options"""
    def __init__(self, parent, update_function=None):
        self.parent = parent
        if update_function is None:
            self.update_function = lambda: None
        else:
            self.update_function = update_function
        self.addoption = tk.StringVar(parent, '')

        "--------------- LEFT ---------------"
        frm = ttk.Frame(parent)
        frm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        var = ttk.Label(frm, text='Options', font=SF)
        var.pack(side=tk.TOP)
        # Listbox with scrollbar
        lst = ttk.Frame(frm)
        lst.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        scly = tk.Scrollbar(lst)
        scly.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.lst_options = tk.Listbox(lst, font=MF, selectmode=tk.EXTENDED, width=10, height=6, bg=ety,
                                      yscrollcommand=scly.set)
        self.lst_options.configure(exportselection=True)
        # self.lst_options.bind('<<ListboxSelect>>', self.fun_listboxselect)
        self.lst_options.bind('<Double-Button-1>', self.lst_doubleclick)

        # Populate list box
        for name in SCANOPTIONS:
            self.lst_options.insert(tk.END, name)
        self.lst_options.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        scly.config(command=self.lst_options.yview)

        # for select in current_selection:
        #     if select in data_fields:
        #         idx = data_fields.index(select)
        #         self.lst_data.select_set(idx)

        # Entry with button
        sec = ttk.Frame(frm)
        sec.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        var = tk.Entry(sec, textvariable=self.addoption, font=TF, width=8, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Button(sec, text='+', font=BF, width=4, command=self.but_newoption,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=4, ipadx=4)

        "--------------- MIDDLE ---------------"
        frm = ttk.Frame(parent)
        frm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.Y)

        var = tk.Button(frm, text='>', font=BF, width=1, command=self.but_addoption,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)
        var = tk.Button(frm, text='<', font=BF, width=1, command=self.but_remoption,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)

        "--------------- RIGHT ---------------"
        frm = ttk.Frame(parent)
        frm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        var = ttk.Label(frm, text='Include', font=SF)
        var.pack(side=tk.TOP)
        # Listbox with scrollbar
        lst = ttk.Frame(frm)
        lst.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        scly = tk.Scrollbar(lst)
        scly.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.lst_include = tk.Listbox(lst, font=MF, selectmode=tk.SINGLE, width=10, height=6, bg=ety,
                                      yscrollcommand=scly.set)
        self.lst_include.configure(exportselection=True)
        self.lst_include.bind('<Double-Button-1>', self.inc_doubleclick)
        self.lst_include.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        scly.config(command=self.lst_include.yview)

        frm = ttk.Frame(parent)
        frm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.Y)

        var = tk.Button(frm, text='+', font=BF, width=1, command=self.but_moveup,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)
        var = tk.Button(frm, text='-', font=BF, width=1, command=self.but_movedown,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)

    def command(self):
        return ' '.join(self.lst_include.get(0, tk.END))

    def but_newoption(self):
        newopt = self.addoption.get()
        if newopt and newopt not in self.lst_options.get(0, tk.END):
            self.lst_options.insert(tk.END, newopt)

    def but_addoption(self):
        selection = self.lst_options.curselection()
        all_include = self.lst_include.get(0, tk.END)
        for idx in selection:
            name = self.lst_options.get(idx)
            if name not in all_include:
                self.lst_include.insert(tk.END, name)

    def but_remoption(self):
        selection = self.lst_include.curselection()
        for idx in selection:
            self.lst_include.delete(idx)
            if idx > 0:
                self.lst_include.select_set(idx - 1)
            elif idx < self.lst_include.size():
                self.lst_include.select_set(idx)

    def lst_doubleclick(self, event=None):
        self.but_addoption()

    def but_moveup(self):
        selection = self.lst_include.curselection()
        if selection and selection[0] > 0:
            item = self.lst_include.get(selection[0])
            self.lst_include.delete(selection[0])
            self.lst_include.insert(selection[0] - 1, item)
            self.lst_include.select_set(selection[0] - 1)

    def but_movedown(self):
        selection = self.lst_include.curselection()
        if selection and selection[0] < self.lst_include.size():
            item = self.lst_include.get(selection[0])
            self.lst_include.delete(selection[0])
            self.lst_include.insert(selection[0] + 1, item)
            self.lst_include.select_set(selection[0] + 1)

    def inc_doubleclick(self, event=None):
        selection = self.lst_include.curselection()
        if selection and selection[0] < self.lst_include.size():
            item = self.lst_include.get(selection[0])
            self.lst_include.delete(selection[0])
            self.lst_include.insert(tk.END, item)


class ScanGenerator:
    """
    A Tabbed window for generating scan commands

    Run using:
        ScanGenerator()

    Use as part of a parent GUI:
        root = tk.Tk()
        cmd = ScanGenerator(root).show()  # Waits for user to press "insert"
    """

    def __init__(self, parent=None, initial_command=''):
        """Initialise"""

        self.parent = parent

        # Create Tk inter instance
        if self.parent is None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(self.parent)
        self.root.wm_title('Scan Command Generator')
        # self.root.minsize(width=640, height=480)
        self.root.maxsize(width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.root.tk_setPalette(
            background=bkg,
            foreground=txtcol,
            activeBackground=opt_active,
            activeForeground=txtcol
        )
        style = ttk.Style()
        style.configure(
            ".",
            background=bkg,
        )
        style.configure(  # configure "tabs" background color
            "TNotebook.Tab",
            font=BF,
            padding=[5, 10],
            justify='center',
            background=bkg,
        )
        # ttk.Style().configure('.', font=BF)

        # Variables
        self.detector = tk.StringVar(self.root, 'pil')
        self.exposure = tk.DoubleVar(self.root, 1)
        self.time = tk.StringVar(self.root, '')
        self.command = tk.StringVar(self.root, initial_command)

        "----------- TOP Scan Tabs -----------"
        frm = ttk.Frame(self.root)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        self.tabControl = ttk.Notebook(frm)
        tab_def = [
            ('Absolute\nScan', AbsoluteScan),
            ('Centred\nScan', CentreScan),
            ('Centred\nScan2', CentreScan2),
            ('θ\n2θ', Theta2ThetaScan),
            ('Energy\nScan', EnergyScan),
            ('2D\nScan', TwoDimScan),
            ('Psi\nScan', PsiScan)
        ]
        self.tabs = [{
            'title': title,
            'tab': ttk.Frame(self.tabControl),
            'class': tab_class,
        } for title, tab_class in tab_def
        ]

        # Generate scan tabs
        for tab in self.tabs:
            self.tabControl.add(tab['tab'], text=tab['title'])
            tab['obj'] = tab['class'](tab['tab'], self.generate_command)
        self.tabControl.pack(expand=tk.YES, fill=tk.BOTH)

        "----------- Middle Detector -----------"
        cen = ttk.Frame(self.root)
        cen.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        frm = ttk.LabelFrame(cen, text='Detector', relief=tk.RIDGE)
        frm.pack(side=tk.LEFT, expand=tk.NO, fill=tk.BOTH)

        frm2 = ttk.Frame(frm)
        frm2.pack(side=tk.TOP, expand=tk.NO, fill=tk.BOTH)
        var = ttk.Label(frm2, text='Detector:', font=SF)
        var.pack(side=tk.LEFT)
        var = tk.Entry(frm2, textvariable=self.detector, font=TF, width=14, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, padx=4)
        var.bind('<Return>', self.ety_detector)
        var.bind('<KP_Enter>', self.ety_detector)
        var = tk.Button(frm2, text='Select', font=BF, width=4, command=self.but_detector,
                        bg=ety, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=4, ipadx=4)
        frm2 = ttk.Frame(frm)
        frm2.pack(side=tk.TOP, expand=tk.NO, fill=tk.BOTH)
        var = ttk.Label(frm2, text='Exposure:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = tk.Entry(frm2, textvariable=self.exposure, font=TF, width=6, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, padx=4)

        "----------- Middle Options -----------"
        frm = ttk.LabelFrame(cen, text='Scan Data', relief=tk.RIDGE)
        frm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.options = ScanOptions(frm, self.generate_command)

        "----------- Bottom Time box -----------"
        frm = ttk.Frame(self.root)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)

        var = ttk.Label(frm, text='Time:', font=SF)
        var.pack(side=tk.LEFT, padx=4)
        var = ttk.Label(frm, textvariable=self.time, font=SF)
        var.pack(side=tk.LEFT, padx=4)

        "----------- Bottom Edit box -----------"
        frm = ttk.Frame(self.root)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)

        var = tk.Button(frm, text='Generate', font=BF, width=12, command=self.generate_command,
                        bg=btn, activebackground=btn_active)
        var.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=6)
        var = tk.Entry(frm, textvariable=self.command, width=60, font=TF, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, ipady=5)
        var.bind('<Return>', self.ety_command)
        var.bind('<KP_Enter>', self.ety_command)
        var = tk.Button(frm, text='COPY', font=BF, width=5, height=1, command=self.copy_command,
                        bg=ety, fg='grey', activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=0)

        if self.parent is not None:
            var = tk.Button(frm, text='INSERT', font=BF, width=10, command=self.insert_command,
                            bg='gold', activebackground=btn_active, fg='black')
            var.pack(side=tk.LEFT, fill=tk.Y, padx=4)

        "-------------------------Start Mainloop------------------------------"
        self.ety_command()
        self.root.protocol("WM_DELETE_WINDOW", self.f_exit)
        if self.parent is None:
            self.root.mainloop()

    "------------------------------------------------------------------------"
    "--------------------------General Functions-----------------------------"
    "------------------------------------------------------------------------"

    def detector_command(self):
        """Generate detector command"""
        det_name = self.detector.get()
        exposure = self.exposure.get()
        cmd = detector(det_name, exposure=exposure)
        return cmd

    "------------------------------------------------------------------------"
    "---------------------------Button Callbacks-----------------------------"
    "------------------------------------------------------------------------"

    def but_detector(self):
        """Select detector"""
        det = select_detector(self.root)
        if det:
            self.detector.set(det)
            self.exposure.set(DETECTORS[det]['exposure'])
            rois = detector_rois(det)
            opts = self.options.lst_options.get(0, tk.END)
            for roi in rois:
                if roi not in opts:
                    self.options.lst_options.insert(tk.END, roi)

    def ety_detector(self, event=None):
        """Press enter on detector"""
        det_name = self.detector.get()
        det_name = detector_name(det_name)
        self.detector.set(det_name)
        self.exposure.set(DETECTORS[det_name]['exposure'])
        rois = detector_rois(det_name)
        opts = self.options.lst_options.get(0, tk.END)
        for roi in rois:
            if roi not in opts:
                self.options.lst_options.insert(tk.END, roi)

    def ety_command(self):
        """Update scan time"""
        cmd = self.command.get()
        time, npoints = scan_command_time(cmd)
        s = time_string(time)
        self.time.set('%s (%s points)' % (s, npoints))

    def generate_command(self):
        """Generate command"""
        # Get scan tab
        index = self.tabControl.index(self.tabControl.select())
        scan_command = self.tabs[index]['obj'].command()
        detector_command = self.detector_command()
        options_command = self.options.command()
        cmd = ' '.join([scan_command, detector_command, options_command])
        self.command.set(cmd)
        self.ety_command()

    def copy_command(self):
        """copy string to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.command.get())
        self.root.update()

    def insert_command(self):
        """Insert command in parent, destroy window"""
        self.root.destroy()

    def show(self):
        """Run the selection box, wait for response"""

        # self.root.deiconify()  # show window
        self.root.wait_window()  # wait for window
        return self.command.get()

    def f_exit(self):
        self.root.destroy()

