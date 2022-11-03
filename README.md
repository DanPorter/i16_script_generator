# i16_script_generator
Python module and GUIs for automatic creation of experiment scripts.

### Features
The script editing window has the following features:
 - Script timing - analyse script and determine estimate of how long it will take.
 - Buttons to add new loops and scans
 - Scan command GUI to create and insert custom scan commands
 - Python syntax highlighting, including beamline commands
 - Auto-tab, easy-indenting, commenting etc.

**Version 1.0**

By Dan Porter, PhD
Diamond Light Source Ltd.
2022

![GUI Window](https://github.com/DanPorter/i16_script_generator/blob/master/i16_script_generator.PNG?raw=true)

#### Usage:
Start the GUI from a terminal
```text
$ python -m i16_script_generator
```
Or, start the window from a python script:

```python
from i16_script_generator import ScriptGenerator

filename = 'mm12345-1/temp_dep.py'
with open(filename) as f:
    script = f.read()
ScriptGenerator(filename, script)
```

For comments, queries or bugs - email [dan.porter@diamond.ac.uk](mailto:dan.porter@diamond.ac.uk)

# Installation
**Requirements:** 
Python 3+ with packages: *Numpy*.

BuiltIn packages used: *sys*, *os*, *re*, *datetime*, *Tkinter*, *ttk*


Download latest version from [GitHub](https://github.com/DanPorter/i16_script_generator), then run the file
```text
$ git clone https://github.com/DanPorter/i16_script_generator.git
$ cd i16_script_generator
$ python -m i16_script_generator
```

