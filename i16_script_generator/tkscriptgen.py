# This Python code is encoded in: utf-8
"""
tkinter GUI for i16_script_generator

By Dan Porter, PhD
Diamond Light Source Ltd
2022
"""

import re
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from i16_script_generator.params import SCANNABLES, DETECTORS, EDGES, SCANOPTIONS
from i16_script_generator.timing import time_script_string, time_string, eval_tabpos
from i16_script_generator.tkwidgets import TF, BF, SF, MF, bkg, ety, btn, opt, btn_active, opt_active, txtcol, \
    ety_txt, SelectionBox, popup_about, popup_message, popup_help, topmenu, filedialog
from i16_script_generator.tkscangen import select_scannable, scan_range, strfmt, ScanGenerator


SCRIPT = '''"""
Example Script
%s
"""

pos shutter 1
pos x1 1

scancn eta 0.01 101 pil 1 roi2

for chi_val in frange(84, 96, 2):
    pos chi chi_val
    scancn eta 0.01 101 pil 1 roi2
''' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

# Define colors for the variouse types of tokens
normal = '#eaeaea'  # rgb((234, 234, 234))
keywords = '#ea5f5f'  # rgb((234, 95, 95))
commands = '#54AAE3'
comments = '#5feaa5'  # rgb((95, 234, 165))
string = '#eaa25f'  # rgb((234, 162, 95))
function = '#5fd3ea'  # rgb((95, 211, 234))
background = '#2a2a2a'  # rgb((42, 42, 42))
font = 'Consolas 15'

# Define a list of Regex Pattern that should be colored in a certain way
REPL = [
    [
        r'(?:^|\s|\W)(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|' +
        r'for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)(?:$|\s|\W)',
        keywords
    ],
    [r'(?:^|\s|\W)(scan|scancn|cscan|frange|pos|inc|go)(?:$|\s|\W)', commands],
    ['".*?"', string],
    ['\'.*?\'', string],
    ['#.*?$', comments],
]


def search_re(pattern, text, groupid=0):
    matches = []

    text = text.splitlines()
    for i, line in enumerate(text):
        for match in re.finditer(pattern, line):
            if match.groups():
                matches.append((f"{i + 1}.{match.span(1)[0]}", f"{i + 1}.{match.span(1)[1]}"))
            else:
                matches.append((f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}"))
    return matches


class LoopGen:
    """
    Small GUI to select scannable for loops
    """

    def __init__(self, parent):
        """Initialise"""

        self.parent = parent

        # Create Tk inter instance
        self.root = tk.Toplevel(self.parent)
        self.root.wm_title('Create For Loop')
        # self.root.minsize(width=640, height=480)
        self.root.maxsize(width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.root.tk_setPalette(
            background=bkg,
            foreground=txtcol,
            activeBackground=opt_active,
            activeForeground=txtcol
        )
        style = ttk.Style()
        style.configure('.', font=BF, background=bkg)

        # Variables
        self.scannable = tk.StringVar(self.root, 'x')
        self.scan_start = tk.StringVar(self.root, '0')
        self.scan_stop = tk.StringVar(self.root, '1')
        self.scan_step = tk.StringVar(self.root, '0.1')
        self.scan_nsteps = tk.StringVar(self.root, '11')
        self.scan_range = tk.StringVar(self.root, '1')

        frm = ttk.Frame(self.root)
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

        frm = ttk.Frame(self.root)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        var = tk.Button(frm, text='INSERT', font=BF, command=self.insert_command,
                        bg='gold', activebackground=btn_active, fg='black')
        var.pack(side=tk.LEFT, fill=tk.X, padx=4)

        "-------------------------Start Mainloop------------------------------"
        self.root.protocol("WM_DELETE_WINDOW", self.f_exit)

    def command(self):
        scannable = self.scannable.get()
        start = eval(self.scan_start.get())
        stop = eval(self.scan_stop.get())
        step = eval(self.scan_step.get())
        cmd = f"for {scannable}_val in frange({start}, {stop}, {step}):\n    pos {scannable} {scannable}_val\n    "
        return cmd

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
        opt = select_scannable(self.root)
        if opt:
            self.scannable.set(opt)
            if 'start' in SCANNABLES[opt]:
                self.scan_start.set(SCANNABLES[opt]['start'])
            else:
                self.scan_start.set('0')
            if 'stop' in SCANNABLES[opt]:
                self.scan_stop.set(SCANNABLES[opt]['stop'])
            else:
                self.scan_stop.set('1')
            if 'step' in SCANNABLES[opt]:
                self.scan_step.set(SCANNABLES[opt]['step'])
            else:
                self.scan_step.set('0.1')
            self.get_sss()

    def insert_command(self):
        """Insert command in parent, destroy window"""
        self.root.destroy()

    def show(self):
        """Run the selection box, wait for response"""

        # self.root.deiconify()  # show window
        self.root.wait_window()  # wait for window
        return self.command()

    def f_exit(self):
        self.root.destroy()


class ScriptGenerator:
    """

    """

    def __init__(self, filename='', script_string=SCRIPT, parent=None):
        """Initialise"""

        self.parent = parent

        # Create Tk inter instance
        if self.parent is None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(self.parent)
        self.root.wm_title('Script Generator')
        # self.root.minsize(width=640, height=480)
        self.root.maxsize(width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.root.tk_setPalette(
            background=bkg,
            foreground=txtcol,
            activeBackground=opt_active,
            activeForeground=txtcol
        )
        style = ttk.Style()
        style.configure('.', font=BF, background=bkg)

        # Top menu
        menu = {
            'File': {
                'New window': self.menu_new_window,
                'New script': self.menu_new,
                'Open': self.menu_open,
                'Save As...': self.menu_saveas,
                'Save': self.menu_save,
                'Quit': self.f_exit,
            },
            'Tools': {
                'Scan Generator': self.menu_scan,
                'Script timer': self.menu_timer,
            },
            'Help': {
                'Docs': popup_help,
                'About': popup_about,
            }
        }
        topmenu(self.root, menu)

        # Variables
        self.filename = tk.StringVar(self.root, filename)
        self.time_str = tk.StringVar(self.root, '0 s')
        self.script_string = script_string

        "----------- TOP Filename -----------"
        frm = ttk.LabelFrame(self.root, text='Filename', relief=tk.RIDGE)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

        var = tk.Entry(frm, textvariable=self.filename, font=TF, bg=ety, fg=ety_txt)
        var.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=4)

        "----------- MIDDLE LEFT - Buttons -----------"
        mid = ttk.Frame(self.root)
        mid.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        left = ttk.Frame(mid)
        left.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        frm = ttk.LabelFrame(left, text='Insert', relief=tk.RIDGE)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

        var = tk.Button(frm, text='Loop...', command=self.btn_loop,
                        font=BF, bg=btn, activebackground=btn_active)
        var.pack(side=tk.TOP, fill=tk.X, padx=2, pady=6)

        var = tk.Button(frm, text='Scan...', command=self.btn_scan,
                        font=BF, bg=btn, activebackground=btn_active)
        var.pack(side=tk.TOP, fill=tk.X, padx=2, pady=6)

        # Small buttons
        small = ttk.Frame(frm)
        small.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)

        var = tk.Button(small, text='>>', command=self.btn_tabin,
                        font=["Times", 6], bg=btn, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=2, pady=2)
        var = tk.Button(small, text='<<', command=self.btn_tabback,
                        font=["Times", 6], bg=btn, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=2, pady=2)
        var = tk.Button(small, text='#', command=self.btn_comment,
                        font=["Times", 6], bg=btn, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=2, pady=2)

        "----------- MIDDLE RIGHT - Textbox -----------"
        left = ttk.Frame(mid)
        left.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        frm = ttk.LabelFrame(left, text='Insert', relief=tk.RIDGE)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

        # Add a hefty border width so we can achieve a little bit of padding
        self.text = tk.Text(frm, background=background, foreground=normal, insertbackground=normal, relief=tk.FLAT,
                            borderwidth=30, font=font, undo=True, autoseparators=True, maxundo=-1)
        self.text.pack(fill=tk.BOTH, expand=1)
        self.text.insert('1.0', self.script_string)
        self.text.bind('<KeyRelease>', self.changes)
        self.text.bind('<Return>', self.auto_indent)
        self.text.bind('<KP_Enter>', self.auto_indent)
        self.text.bind('<Tab>', self.tab)
        self.text.bind('<Shift-Tab>', self.shift_tab)
        self.text.bind('<Control-slash>', self.comment)
        self.text.bind('<BackSpace>', self.delete)

        # bottom timing
        frm = ttk.Frame(frm)
        frm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)

        var = tk.Button(frm, text='Timeit', command=self.btn_timeit,
                        font=BF, bg=btn, activebackground=btn_active)
        var.pack(side=tk.LEFT, padx=2, pady=6)
        var = ttk.Label(frm, textvariable=self.time_str, font=SF)
        var.pack(side=tk.LEFT, padx=4)

        "-------------------------Start Mainloop------------------------------"
        self.changes()
        self.root.protocol("WM_DELETE_WINDOW", self.f_exit)
        if self.parent is None:
            self.root.mainloop()

    "------------------------------------------------------------------------"
    "--------------------------General Functions-----------------------------"
    "------------------------------------------------------------------------"

    def changes(self, event=None):
        """ Register Changes made to the Editor Content """

        # If actually no changes have been made stop / return the function
        if self.text.get('1.0', tk.END) == self.script_string:
            return

        # Remove all tags so they can be redrawn
        for tag in self.text.tag_names():
            self.text.tag_remove(tag, "1.0", tk.END)

        # Add tags where the search_re function found the pattern
        i = 0
        for pattern, color in REPL:
            for start, end in search_re(pattern, self.text.get('1.0', tk.END)):
                self.text.tag_add(f'{i}', start, end)
                self.text.tag_config(f'{i}', foreground=color)
                i += 1

        # Add tags to multiline comments
        start = None
        for n, line in enumerate(self.text.get('1.0', tk.END).splitlines()):
            for match in re.finditer('\'{3}|\"{3}', line):
                if start:
                    self.text.tag_add(f'{i}', start, f"{n + 1}.{match.end()}")
                    self.text.tag_config(f'{i}', foreground=comments)
                    i += 1
                    start = None
                else:
                    start = f"{n + 1}.{match.start()}"

        self.script_string = self.text.get('1.0', tk.END)

    def tab(self, event=None):
        if event is None:
            text = self.text
        else:
            text = event.widget
        try:
            first = int(text.index(tk.SEL_FIRST).split('.')[0])
            last = int(text.index(tk.SEL_LAST).split('.')[0])
            for lineno in range(first, last+1):
                text.insert('%d.0' % lineno, " " * 4)
        except tk.TclError:
            text.insert(tk.INSERT, " " * 4)
        return 'break'

    def shift_tab(self, event=None):
        if event is None:
            text = self.text
        else:
            text = event.widget
        try: # selection
            first = int(text.index(tk.SEL_FIRST).split('.')[0])
            last = int(text.index(tk.SEL_LAST).split('.')[0])
            for lineno in range(first, last+1):
                line = text.get('%d.0' % lineno, '%d.0 lineend' % lineno)
                spaceno = len(line) - len(line.lstrip())
                spaceno = 4 if spaceno > 4 else spaceno
                text.delete('%d.0' % lineno, '%d.%d' % (lineno, spaceno))
        except tk.TclError: # single point
            lineno = int(text.index('insert').split('.')[0])
            line = text.get('%d.0' % lineno, '%d.0 lineend' % lineno)
            spaceno = len(line) - len(line.lstrip())
            text.delete('%d.0' % lineno, '%d.%d' % (lineno, spaceno))
        return 'break'

    def comment(self, event=None):
        if event is None:
            text = self.text
        else:
            text = event.widget
        try:
            first = int(text.index(tk.SEL_FIRST).split('.')[0])
            last = int(text.index(tk.SEL_LAST).split('.')[0])
            line = text.get('%d.0' % first, '%d.0 lineend' % first)
            if line.startswith('#'):  # remove comments
                for lineno in range(first, last + 1):
                    line = text.get('%d.0' % lineno, '%d.0 lineend' % lineno)
                    if line.startswith('# '):
                        text.delete('%d.0' % lineno, '%d.2' % lineno)
                    elif line.startswith('#'):
                        text.delete('%d.0' % lineno)
            else:  # add comments
                for lineno in range(first, last + 1):
                    line = text.get('%d.0' % lineno, '%d.0 lineend' % lineno)
                    if not line.startswith('#'):
                        text.insert('%d.0' % lineno, '# ')
        except tk.TclError:
            lineno = int(text.index('insert').split('.')[0])
            line = text.get('%d.0' % lineno, '%d.0 lineend' % lineno)
            if line.startswith('# '):
                text.delete('%d.0' % lineno, '%d.2' % lineno)
            elif line.startswith('#'):
                text.delete('%d.0' % lineno)
            else:
                text.insert('%d.0' % lineno, '# ')
        return 'break'

    def auto_indent(self, event=None):
        if event is None:
            text = self.text
        else:
            text = event.widget

        # get leading whitespace from current line
        line = text.get("insert linestart", "insert")
        match = re.match(r'^(\s+)', line)
        whitespace = match.group(0) if match else ""

        # insert the newline and the whitespace
        text.insert("insert", f"\n{whitespace}")

        # return "break" to inhibit default insertion of newline
        return "break"

    def delete(self, event=None):
        if event is None:
            text = self.text
        else:
            text = event.widget
        tabWidth = 4
        line = text.get("insert linestart", "insert")
        previous = text.get("insert -%d chars" % tabWidth, "insert")
        if line == " " * len(line) and len(line) % tabWidth > 0:
            # print('deleting %d chars' % (len(line) % tabWidth))
            text.delete("insert -%d chars" % (len(line) % tabWidth), "insert")
            return "break"
        elif previous == " " * tabWidth:
            # print('delete tab')
            text.delete("insert-%d chars" % tabWidth, "insert")
            return "break"
        elif '\n' in previous:
            # print('delete start of tab %d' % len(line))
            text.delete("insert-%d chars" % len(line), "insert")
            return "break"

    "------------------------------------------------------------------------"
    "---------------------------Menu Callbacks-----------------------------"
    "------------------------------------------------------------------------"

    def menu_new_window(self):
        """Open new instance"""
        ScriptGenerator()

    def menu_new(self):
        """Overwrite"""
        answer = messagebox.askokcancel('Script editor', 'Do you want to replace the current script?')
        if answer:
            self.text.delete('1.0', tk.END)
            self.text.insert('1.0', SCRIPT)
            self.changes()

    def menu_open(self):
        """Open new script"""
        filename = filedialog.askopenfilename(
            title='Open I16 Measurement Script',
            defaultextension='*.py',
            filetypes=(("Python files", "*.py"), ("All files", "*.*"))
        )
        if filename:
            with open(filename, 'r') as f:
                self.script_string = f.read()
            self.text.delete('1.0', tk.END)
            self.text.insert('1.0', self.script_string)
            self.filename.set(filename)
            self.changes()
            self.btn_timeit()
    
    def menu_saveas(self):
        """Save as file"""
        c_filename = self.filename.get()
        filename = filedialog.asksaveasfile(title='I16 Script', initialfile=c_filename, defaultextension='.py')
        if filename:
            with open(filename, 'w') as f:
                f.write(self.script_string)
            print('Written script to %s' % filename)
            self.filename.set(filename)
    
    def menu_save(self):
        """Save script"""
        filename = self.filename.get()
        if filename == '':
            self.menu_saveas()
        with open(filename, 'w') as f:
            f.write(self.script_string)
        print('Written script to %s' % filename)
    
    def menu_scan(self):
        """Start ScanGenerator GUI"""
        ScanGenerator()
    
    def menu_timer(self):
        """Get script time"""
        from i16_script_generator.timing import time_script, time_string
        filename = filedialog.askopenfilename(
            title='Time an I16 measurement script',
            defaultextension='*.py',
            filetypes=(("Python files", "*.py"), ("All files", "*.*"))
        )
        if filename:
            time = time_script(filename)
            msg = "Script: \n%s \nwill take %s" % (filename, time_string(time.total_seconds()))
            messagebox.showinfo('I16 Script Timer', msg)

    "------------------------------------------------------------------------"
    "---------------------------Button Callbacks-----------------------------"
    "------------------------------------------------------------------------"

    def btn_loop(self):
        """Add new loop"""
        loop = LoopGen(self.root).show()
        if loop:
            start = self.text.index('insert linestart')
            stop = self.text.index('insert lineend')
            line = self.text.get(start, stop)
            print('"%r"' % line)
            tabpos = eval_tabpos(line)
            loop = loop.replace('\n', '\n' + "    " * tabpos)
            print(tabpos, '%r' % loop)
            if 'for' in line:  # replace loop
                self.text.delete(start, stop)
                self.text.insert(start, "    " * tabpos + loop)
            else:
                self.text.insert('insert',  loop)
            self.changes()

    def btn_scan(self):
        scan = ScanGenerator(self.root).show()
        if scan:
            start = self.text.index('insert linestart')
            stop = self.text.index('insert lineend')
            line = self.text.get(start, stop)
            tabpos = eval_tabpos(line)
            if 'scan' in line:
                self.text.delete(start, stop)
                self.text.insert(start, "    " * tabpos + scan + '\n' + "    " * tabpos)
            else:
                self.text.insert('insert', scan + '\n' + "    " * tabpos)
            self.changes()

    def btn_tabin(self):
        self.tab()

    def btn_tabback(self):
        self.shift_tab()

    def btn_comment(self):
        self.comment()

    def btn_timeit(self):
        """Time the script"""
        time, self.script_string = time_script_string(self.script_string)
        self.time_str.set(time_string(time.total_seconds()))
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', self.script_string)
        self.changes()

    def f_exit(self):
        self.root.destroy()

