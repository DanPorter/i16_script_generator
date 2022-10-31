"""
Example usage of ScanGenerator in tkinter GUI
"""

import tkinter as tk
from i16_script_generator import ScanGenerator


class Test:
    def __init__(self):
        self.root = tk.Tk()
        frm = tk.Frame(self.root)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        self.lab = tk.StringVar(self.root, '')

        var = tk.Button(frm, text='Get Scan Command',command=self.button)
        var.pack(side=tk.TOP)

        var = tk.Label(frm, textvariable=self.lab)
        var.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        self.root.protocol("WM_DELETE_WINDOW", self.f_exit)
        self.root.mainloop()

    def button(self):
        cmd = ScanGenerator(self.root).show()
        self.lab.set(cmd)

    def f_exit(self):
        self.root.destroy()


if __name__ == '__main__':
    Test()

