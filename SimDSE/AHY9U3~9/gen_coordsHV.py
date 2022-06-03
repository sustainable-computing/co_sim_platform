'''
Created on Dec. 02, 2019
Generate LV coordinates.

@file    gen_coords.py
@author  Evandro de Souza
@date    2019.12.02  
@version 0.1
@company University of Alberta - Computing Science
'''

#import sys
#import os
import numpy as np

fname_buscoords = 'config/XX_Buscoords.csv'
fname_loads = 'config/XX_Loads.txt'
fname_newbuscoords = 'config/XX_LVLoadCoords.txt'

#fd_buscoords=open(fname_buscoords, 'r')
#fd_loads=open(fname_loads, 'r')
fd_newbuscoords=open(fname_newbuscoords, 'w')


''' read buscoords completely '''
coords = {}
with open(fname_buscoords, 'r') as file:
    for line in file:
        items = line.split()
        coords[items[0]] = (items[1], items[2])


loadbus = np.zeros((55, 4), dtype=int)

with open(fname_loads, 'r') as file:
    for line in file:
        items = line.split()
        ''' get load name '''
        lname = items[1].split('.')[1]
        lname = lname[4:]
        bname = items[3].split('=')[1]
        phase = int(bname.split('.')[1])
        bname = bname.split('.')[0]

        print(lname, coords[bname][0], coords[bname][1])
        loadbus[int(lname)-1, 0] = int(lname)
        loadbus[int(lname)-1, 1] = int(coords[bname][0])
        loadbus[int(lname)-1, 2] = int(coords[bname][1])
        loadbus[int(lname)-1, 3] = phase
        
''' minimize the coords '''
min_x = min(loadbus[:,1])
max_x = max(loadbus[:,1])
min_y = min(loadbus[:,2])
max_y = max(loadbus[:,2])
print (max_x-min_x, max_y-min_y)

''' parametrize the coords '''
for i in range(len(loadbus[:,0])):
    loadbus[i, 1] = loadbus[i, 1] - min_x
    loadbus[i, 2] = loadbus[i, 2] - min_y
    
print(loadbus)
np.savetxt(fname_newbuscoords, loadbus, fmt='%d')
 