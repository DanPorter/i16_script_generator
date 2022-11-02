# i16_script_generator
Python module and GUIs for automatic creation of experiment scripts.

**Version 0.9**

By Dan Porter, PhD
Diamond Light Source Ltd.
2022

![GUI Window](https://github.com/DanPorter/i16_script_generator/blob/master/i16_script_generator.PNG?raw=true)

#### Usage:
Start the GUI from a terminal
```text
$ python -m i16_script_generator
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
Python 3+ with packages: *Numpy*.
BuiltIn packages used: *sys*, *os*, *re*, *datetime*, *Tkinter*, *ttk*


Download latest version from GitHub, then run the file
```text
$ git clone https://github.com/DanPorter/i16_script_generator.git
$ cd i16_script_generator
$ python -m i16_script_generator.py
```



