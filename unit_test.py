"""
I16 Script Generator
Unit Tests
"""

from i16_script_generator import time_script_string
from i16_script_generator.timing import time_string

script = """
scan x 1 2 0.1
scan eta 20.5 22.8 0.01 checkbeam pil 1 roi2
scan x 1 2 0.1 y 2 3 0.05 merlin 0.1
scan th 10 20 0.5 tth 20 1 w .5 diode
scancn energy 0.001 101 hkl [0,0,1] pol 90 pil 1
cscan eta 0.5 0.01 Ta Tb t 1
scancn sx 0.1 31 sy 0.1 31
pos x1 1; scan x 1 2 1
scan hkl [0,0, 0] [1, 1, 1] [0.1,0.1,0.1] pil 1 roi2
pos 
scan hkl [0,0, 0] [0, 0, 1] [0,0,0.01] y -2 0 1 pil 1 roi2

scan eta 45.023 45.423 0.01 pil3_100k 1 roi2 roi1
scan phi 0 130 0.5 pil3_100k 1 roi2
scan eta 20.8 23 0.05 merlin 30
scan th 3.375 13.375 0.1 BeamOK merlin 1
scan th 10.02 10.52 0.01 merlins 5
scan delta -0.95 1 0.05 merlins 1
scan gam -0.95 1 0.05 merlins 1
scan Base_z -0.367 0.033 0.01 Waittime 1 diode
scan x 1 10 1 bpm 1.0E-4
scan x 1 10 1
scan x 1 10 1 pil2ms 1
scan thp -11.304 -11.254 0.001 merlin 1


pos shutter 1
pos x1 1

scancn eta 0.01 101 pil 1 roi2

for chi_val in frange(84, 96, 2):
    pos chi chi_val
    scancn eta 0.01 101 pil 1 roi2


ini_chi = chi()
stop_script = False
for chival in frange(ini_chi-5, ini_chi+5, 1):
    if stop_script: break
    pos chi chival
    scancn eta 0.05 61 checkbeam pil 1 roi1 roi2


setnhkl([1,0,0]) # azimuth reference vector (h,k,l)
con gam 0 mu 0 psi 0  # fixed psi mode

hklval = [0,0,1]
psi_range = frange(-180, 180,5)

# Simulation
for psival in psi_range:
    pos psic psival
    out = simhkl(hklval)

# Measurement
script_stop = False
for psival in psi_range:
    if script_stop: break
    pos psic psival
    pos hkl hklval
    scancn eta 0.05 61 checkbeam pil 1 roi1 roi2


# szc.calibrate('4K',Ta) # calibrate before start
fitproc = i16_gda_functions.peakfit_processor('tempdep.dat', 'Ta')  # saves in script dir

hkl_list = [[0, 0, 1], [0, 0, 2]]

temp_stop = False
for tval in frange(10, 100, 5) + frange(110, 300, 10):
    if temp_stop: break
    pos tset tval
    while abs(Ta() - tval) > 0.2:
        print('Waiting...Ta = %5.1f K, Tb = %5.1f K' % (Ta(), Tb()))
        w(30)
    print('Stabilising...Ta = %5.1f K, Tb = %5.1f K' % (Ta(), Tb()))
    w(30)

    print('Adjusting height')
    pos szc 0

    for n in range(len(hkl_list)):
        pos hkl hkl_list[n]
        scancn eta 0.05 61 checkbeam fitproc pil 1 roi1 roi2
        go peak
        pil2max()
        hkl_list[n] = hkl()



pos shutter 1
pos x1 1 # fast shutter
pos ss [.02,.02]
pos atten 0
pos do do.pil
con gam 0 mu 0 phi 0 # fixed phi

ini_sx = sx()
ini_sy = sy()
iperp = sperp()
ipara = spara()
x_min, x_max, x_step = -0.2, 0.2, 0.01
y_min, y_max, y_step = -0.2, 0.2, 0.01

script_stop = False
line_stop = False
for sxval in frange(iperp+x_min, iperp+x_max, x_step):
    if script_stop or line_stop:
        break
    pos sperp sxval
    for syval in frange(ipara+y_min, ipara+y_max, y_step):
        if script_stop:
            break
        pos sperp sxval
        pos spara syval
        scancn eta 0.05 41 checkbeam pil 1 roi1 roi2

# Return to original positions
pos sx ini_sx
pos sy ini_sy

print('Finished')
"""

tot_time, new_script = time_script_string(script)
print('Example Script\n---------------------')
print(new_script)
print('Total time: %s' % time_string(tot_time.total_seconds()))
print(' Should be: 47 hours, 57 mins, 23s')
