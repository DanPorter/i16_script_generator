# i16_script_generator
Python module and GUIs for automatic creation of experiment scripts.

**Version 1.0**

By Dan Porter, PhD
Diamond Light Source Ltd.
2022

![GUI Window](https://github.com/DanPorter/i16_scan_generator/blob/master/i16_scan_generator.PNG?raw=true)

#### Usage:
Start the GUI from a terminal
```text
$ python -m i16_script_generator.py
```
Or, start the window from another tkinter GUI

```python
import tkinter as tk
from i16_script_generator import ScanGenerator

root = tk.Tk()
cmd = ScanGenerator(root).show()  # Waits for user to press "insert"
```

For comments, queries or bugs - email [dan.porter@diamond.ac.uk](mailto:dan.porter@diamond.ac.uk)

# Installation
**Requirements:** 
Python 3+ with packages: *Numpy*, *Tkinter*.
BuiltIn packages used: *sys*, *os*, *re*


Download latest version from GitHub, then run the file
```text
$ git clone https://github.com/DanPorter/i16_scan_generator.git
$ cd i16_scan_generator
$ python -m i16_scan_generator.py
```



