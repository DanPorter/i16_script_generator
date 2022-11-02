"""
i16_script_generator
Simple GUI to automatically generate scan commands in GDA

Usage:
    $ python -m i16_script_generator.py

or from another GUI:
    import tkinter as tk
    from i16_script_generator import ScanGenerator
    root = tk.Tk()
    cmd = ScanGenerator(root).show()  # Waits for user to press "insert"

By Dan Porter, PhD
Diamond Light Source Ltd.
2022
"""

from i16_script_generator.tkscangen import ScanGenerator
from i16_script_generator.tkscriptgen import ScriptGenerator

__version__ = '0.9.0'
__date__ = '02/11/22'


def version_info():
    return 'i16_script_generator version %s (%s)' % (__version__, __date__)


def module_info():
    import sys
    out = 'Python version %s' % sys.version
    out += '\n%s' % version_info()
    # Modules
    import numpy
    out += '\n     numpy version: %s' % numpy.__version__
    import tkinter
    out += '\n   tkinter version: %s' % tkinter.TkVersion
    from tkinter import ttk
    out += '\n       ttk version: %s' % ttk.__version__
    out += '\n'
    return out


def doc_str():
    return __doc__
