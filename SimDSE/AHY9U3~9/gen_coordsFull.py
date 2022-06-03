'''
Created on Dec. 02, 2019
Generate all coordinates for NS3

@file    gen_coords.py
@author  Evandro de Souza
@date    2019.12.02  
@version 0.1
@company University of Alberta - Computing Science
'''

import numpy as np

fname_hvcoords     = 'config/IEEE33_BusXY.csv'
fname_lvloads      = 'config/XX_LVLoadCoords.txt'
fname_FullCoords   = 'config/XX_IEEE33_BusXYFull.csv'
fname_NodeWithLoad = 'config/XX_IEEE33_NodeWithLoadFull.csv'
fname_AdjMatrix    = 'config/XX_IEEE33_AdjMatrixFull.txt'
fname_Devices      = 'config/XX_IEEE33_DevicesFull.csv'
fname_Loads        = 'config/loadData33Full.dss'

''' read HV buscoords '''
hvcoords = {}
with open(fname_hvcoords, 'r') as file:
    for line in file:
        items = line.split(',')
        #print(items[0], items[1], items[2])
        hvcoords[int(items[0])] = (items[1], items[2])

lvloads = {}
with open(fname_lvloads, 'r') as file:
    for line in file:
        items = line.split()
        #print(items[0], items[1], items[2], items[3])
        lvloads[int(items[0])] = (items[1], items[2], items[3])
        
        
fullCoords = []

''' add HV nodes '''
for idx in hvcoords.keys():
    fullCoords.append((idx, int(hvcoords[idx][0]), int(hvcoords[idx][1])))


''' add load coords '''
for keyBus in hvcoords.keys():
    for keyLoad in lvloads.keys():
        if keyBus != 1:
            #load_name = str(keyBus*1000 + keyLoad + 55) + '.' + lvloads[keyLoad][2]
            load_name = str(keyBus*1000 + keyLoad + 55)
            fullCoords.append((load_name,
                              int(hvcoords[keyBus][0]) + 10  + int(lvloads[keyLoad][0]),
                              int(hvcoords[keyBus][1]) + 140 - int(lvloads[keyLoad][1]))) 


''' print name and coords '''
#for i in range(len(fullCoords)):
    #print(fullCoords[i][0], fullCoords[i][1], fullCoords[i][2])
    
''' save in file for coords '''
with open(fname_FullCoords, 'w') as f:
    for item in fullCoords:
        rec = str(item[0]) + ',' + str(item[1]) + ',' + str(item[2])
        f.write(rec+'\n')


''' *** NODEWITHLOAD *** '''
''' save in file for NWL'''
hvx = len(hvcoords)
idx = 1
with open(fname_NodeWithLoad, 'w') as f:
    for item in fullCoords:
        rec = str(item[0]) + ',1'
        if (idx > hvx):
            f.write(rec+'\n')  
        idx = idx + 1 
        
        
''' *** ADJMATRIX *** '''
adjmat = []
adjmat.append((1,2))
adjmat.append((2,3))
adjmat.append((3,4))
adjmat.append((4,5))
adjmat.append((5,6))
adjmat.append((6,7))
adjmat.append((7,8))
adjmat.append((8,9))
adjmat.append((9,10))
adjmat.append((10,11))
adjmat.append((11,12)) 
adjmat.append((12,13)) 
adjmat.append((13,14))
adjmat.append((14,15))
adjmat.append((15,16))
adjmat.append((16,17))
adjmat.append((17,18))
adjmat.append((2,19))
adjmat.append((19,20))    
adjmat.append((20,21))
adjmat.append((21,22))
adjmat.append((3,23))
adjmat.append((23,24))
adjmat.append((24,25))
adjmat.append((6,26))
adjmat.append((26,27))
adjmat.append((27,28))
adjmat.append((28,29))
adjmat.append((29,30))
adjmat.append((30,31))
adjmat.append((31,32))
adjmat.append((32,33))
for keyBus in hvcoords.keys():
    for keyLoad in lvloads.keys():
        if keyBus != 1:
            load_name = str(keyBus*1000 + keyLoad + 55) + '.' + lvloads[keyLoad][2]
            adjmat.append((load_name,keyBus))

dimMat = len(fullCoords)
adjMatrix = np.zeros((dimMat, dimMat), dtype=bool)
''' first 32 links are HV network '''
idx = 0
for idx in range(len(hvcoords)-1): 
    pos_src = adjmat[idx][0] - 1
    pos_dst = adjmat[idx][1] - 1
    adjMatrix[pos_src, pos_dst] = True
    adjMatrix[pos_dst, pos_src] = True
    idx = idx + 1
''' connections in the LV network '''
idx += 1
while idx < len(adjmat):
    pos_src = idx
    pos_dst = adjmat[idx][1] - 1
    adjMatrix[pos_src, pos_dst] = True
    adjMatrix[pos_dst, pos_src] = True    
    idx += 1
''' save adj matrix file '''
np.savetxt(fname_AdjMatrix, adjMatrix, fmt='%d')


''' *** DEVICES *** '''
''' createfile with phasor on all HV nodes and all loads '''
dst = 1
period = 50
error = 0.0001667
phase = "PHASE_123"
with open(fname_Devices, 'w') as f:
    ''' headers '''
    rec = 'idn,type,src,dst,period,error,cktElement,cktTerminal,cktPhase,cktProperty'
    #003,phasor,33,1,10,0.0001667,line.32-33,BUS2,PHASE_123,None
    f.write(rec+'\n')
    ''' phasors on HV '''
    for idx in range(len(hvcoords.keys())): 
        rec = "00" 
        rec += str(idx+1)
        rec += ",phasor,"
        rec += str(idx+1)
        rec += ','
        rec += str(dst)
        rec += ','
        rec += str(period)
        rec += ','
        rec += str(error)
        rec += ","
        rec += "line." + str(adjmat[idx-1][0]) + "-" + str(adjmat[idx-1][1])
        rec += ",BUS2,"
        rec += phase
        rec += ",None"
        f.write(rec+'\n')
        
    with open(fname_Loads, 'r') as file:
        for line in file:
            items = line.split(' ')
            node = items[1].split('.')[1]
            phase = items[1].split('.')[2]
            rec = "00" 
            rec += str(node)
            rec += ",smartmeter,"
            rec += str(node)
            rec += ','
            rec += str(dst)
            rec += ','
            rec += str(period)
            rec += ','
            rec += str(error)
            rec += ","
            rec += items[1]
            rec += ",BUS1,"
            rec += "PHASE_" + phase
            rec += ",None"
            f.write(rec+'\n')        
              
    
    

