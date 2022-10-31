"""
Regex scan types


scan scn1 start stop step [scnN [start [stop [step]]]] ...
scan x 1 2 1 z                  --> loop x, for each step read value/position of z
scan x 1 2 1 z 1                --> loop x, for each step expose/move z for/to 1
scan x 1 2 1 y 10 11 1 z 1      --> loop x, for each x loop y, for each (x,y) step expose/move z for/to 1
scan x 1 2 1 y 10 11 z 1        --> loop x and y together (no ystop required), for each step expose/move z for/to 1
scan x 1 2 1 y 10 11 1 z 1 a b  --> combine any of the above!

scancn scn stepsize numpoints [scnN [start [stop [step]]]]

cscan scn1 halfwidth step [scnN halfwidth step]... [scnN [absolute_pos]]...
  Performs a centroid scan from current-halfwidth to current+halfwidth, and returns to original position.
cscan x 5 1 z                       --> if starting at 10, loops x from -5 to 15 and reads z for each step
cscan x 5 1 y 2 1 z                 --> if starting at 10, loops x from -5 to 15, at each step similarly scans y reading z for each step

rscan scn1 relstart relstop step [scnN relstart relstop step]... [scnN relstart step] [scnN [absolute_pos]]...
  As scan except positions of scannables to be scanned (but not simply moved) are relative. The former will be
  returned to their initial positions.
rscan x -1 2 1 z                 --> loop x, for each step read value/position of z
rscan x -1 2 1 z 3               --> loop x, for each step expose/move z for/to 3
rscan x -1 2 1 y -10 11 1 z 3    --> loop x, for each x loop y, for each (x,y) step expose/move z for/to 3
rscan x -1 2 1 y -1 1 z 3        --> loop x and y together (no ystop required), for each step expose/move z for/to 3
rscan x -1 2 1 y -2 2 1 z 3 a b  --> combine any of the above!

pscan PD first last Nsteps
pscan PD start step Nsteps * On testing, this doesn't always work, especially with steps < 1
Standard scan ending at last point, but giving number of steps
"""

import re
from i16_script_generator.timing import scan_command_time, time_script

scans = [
    'scan x 1 2 0.1',
    'scan eta 20.5 22.8 0.01 checkbeam pil 1 roi2',
    'scan x 1 2 0.1 y 2 3 0.05 merlin 0.1',
    'scan th 10 20 0.5 tth 20 1 w .5 diode',
    'scancn energy 0.001 101 hkl [0,0,1] pol 90 pil 1',
    'cscan eta 0.5 0.01 Ta Tb t 1',
    'scancn sx 0.1 31 sy 0.1 31',
    'pos x1 1; scan x 1 2 1',
    'scan hkl [0,0, 0] [1, 1, 1] [0.1,0.1,0.1] pil 1 roi2',
    'pos ',
    'scan hkl [0,0, 0] [0, 0, 1] [0,0,0.01] y -2 0 1 pil 1 roi2'
]

for cmd in scans:
    tot_time, tot_points = scan_command_time(cmd)
    print(f"{cmd:60s} | {tot_time:8.2f}s  {tot_points:4d}")

examples = [
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   126.96, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   125.44, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   156.35, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   124.48, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   126.71, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   125.48, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   154.71, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   126.26, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   126.18, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   125.44, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   127.21, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   157.00, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   126.12, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   127.81, 'points':   61},
    {'cmd': 'scan eta 29.711 30.311 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   127.57, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   159.22, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   130.17, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   129.41, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   130.49, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   160.47, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   130.53, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   131.51, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   131.11, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   161.33, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   131.83, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   131.18, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   132.14, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   160.62, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   131.67, 'points':   61},
    {'cmd': 'scan eta 42.599 43.199 0.01 BeamOK pil3_100k 1 roi2         ', 'time':   131.39, 'points':   61},
    {'cmd': 'scan eta 44.823 45.623 0.02 pil3_100k 1 roi2 roi1           ', 'time':    89.50, 'points':   41},
    {'cmd': 'scan eta 45.023 45.423 0.01 pil3_100k 1 roi2 roi1           ', 'time':    90.27, 'points':   41},
    {'cmd': 'scan phi 0 130 0.5 pil3_100k 1 roi2                         ', 'time':   580.54, 'points':  261},
    {'cmd': 'scan eta 20.8 23 0.05 merlin 30                             ', 'time':  1455.95, 'points':   45},
    {'cmd': 'scan th 3.375 13.375 0.1 BeamOK merlin 1                    ', 'time':   214.69, 'points':  101},
    {'cmd': 'scan th 10.02 10.52 0.01 merlins 5                          ', 'time':   330.74, 'points':   51},
    {'cmd': 'scan delta -0.95 1 0.05 merlins 1                           ', 'time':    83.88, 'points':   40},
    {'cmd': 'scan gam -0.95 1 0.05 merlins 1                             ', 'time':   103.34, 'points':   40},
    {'cmd': 'scan Base_z -0.367 0.033 0.01 Waittime 1 diode              ', 'time':   131.97, 'points':   41},
    {'cmd': 'scan x 1 10 1 bpm 1.0E-4                                    ', 'time':     4.20, 'points':   10},
    {'cmd': 'scan x 1 10 1                                               ', 'time':     1.21, 'points':   10},
    {'cmd': 'scan x 1 10 1 pil2ms 1                                      ', 'time':    47.35, 'points':   10},
    {'cmd': 'scan thp -11.304 -11.254 0.001 merlin 1                     ', 'time':   127.66, 'points':   51},
]

print('\n\nExamples:')
print('Command                                                      |   Predicted      |   Measured     ')
for example in examples:
    cmd = example['cmd']
    ex_time = example['time']
    ex_points = example['points']
    tot_time, tot_points = scan_command_time(cmd)
    print(f"{cmd:50s} | {tot_time:8.2f}s  {tot_points:4d}  | {ex_time:8.2f}s  {ex_points:4d}")

# Script time
file = '2022_07_29_1534.py'
time = time_script(file, True)
print('%s: %s' % (file, time))


