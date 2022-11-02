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
if __name__ == '__main__':
    from i16_script_generator import ScanGenerator, ScriptGenerator
    ScriptGenerator()
