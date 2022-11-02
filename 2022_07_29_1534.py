"""
Experiment script: /dls_sw/i16/scripts/2022/cm31138-12/2022_07_29_1534.py
2022-07-29T16:34:41.219000
I16 Experiment cm31138-12
Data directory: /dls/i16/data/2022/cm31138-12
Scripts: /dls_sw/i16/scripts/2022/cm31138-12
Script function: Temperature dependence with permanent magnet
First scan number: 945136
Run with:
script_runner('2022_07_29_1534.py')
"""

pos shutter 1
pos x1 1 # fast shutter
pos ss [.5,.5]
pos atten 0
#pos do do.pil

#con delta 0 eta 0 phi 35

#fitproc = i16_gda_functions.peakfit_processor('tempdep_001_field.dat', 'Ta')

#hkl001 = [0,0,1]

#pos do 0
#pos energy 3.146
#pos hkl hkl001
#pos pol 0
#scancn mu 0.05 121 merlin 5 mroi2 
#scan energy 3.12 3.19 0.0005 hkl hkl001 pol 0 merlin 5 mroi2

#pos energy 3.146
#pos hkl hkl001
#pos pol 90
#scancn mu 0.05 121 merlin 5 mroi2 
#scan energy  3.12 3.19 0.0005 hkl hkl001 pol 90 merlin 5 mroi2

"""
for tempval in frange(320, 360, 5):
    pos tset tempval
    w(300)
    pos energy 3.146
    pos do do.pil 
    pos hkl hkl001 
    scancn mu 0.05 121 fitproc pil 1 
    go peak 
    hkl001 = hkl()
    scan energy 3.12 3.19 0.0005 hkl hkl001 pil 1 roi2 
"""
# 360K
#pos do 0
#pos energy 3.146
#pos hkl hkl001
#pos pol 0
#scancn mu 0.05 121 merlin 5 mroi2 
#scan energy 3.12 3.19 0.0005 hkl hkl001 pol 0 merlin 5 mroi2

pos do 0
pos energy 3.146
pos hkl hkl001
pos pol 90
scancn mu 0.05 121 merlin 5 mroi2 
scan energy 3.12 3.19 0.0005 hkl hkl001 pol 90 merlin 5 mroi2

# Cooling
print('Cooling')
pos tset 295
pos energy 3.146
pos do do.pil 
pos hkl [0,0,0.5]
scan x 1 3600 1 Ta pil 1 roi2

hklvals = [
    [0,0,1],
    [0,0,2],
    [0,0,3]
]

for tempval in frange(300, 360, 5):
    pos tset tempval
    w(300)
    pos energy 3.146
    pos do do.pil 
    con delta 0 eta 0 phi 35
    pos hkl [0,0,0.5]
    scancn mu 0.05 121 pil 10 roi2 
    
    con delta 0 eta 0 phi -55
    pos hkl [0,0,0.5]
    scancn mu 0.05 121 pil 10 roi2
    go maxval
    hklnew = hkl()

    for hklval in hklvals:
        pos hkl hklval
        scancn hkl [0,0,0.01] 31 pil 1 roi2

print('Finished')