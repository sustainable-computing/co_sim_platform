'''
Created on Jul. 23, 2019
Data analysis of the simulation results.

@file    analysis.py
@author  Evandro de Souza
@date    2019.07.23  
@version 0.1
@company University of Alberta - Computing Science
'''

import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
import csv

#--- select dataset file
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = 'config/YY_loadData33Full.dss'

newData = 'config/ZZ_loadData33Full.dss'
fileData=open(newData, 'w')

newNWL = 'config/ZZ_IEEE33_NodeWithLoadFull.csv'
fileNWL=open(newNWL, 'w')

with open(filename, 'r') as file:
    for line in file:
        items = line.split(' ')
        
        ''' new load file'''
        phase = items[3].split('.')[1]
        items[1] = items[1] + '.' + phase
        newLine = items[0]
        for i in range(1, len(items)):
            newLine = newLine + " " + items[i]
        fileData.write(newLine)
        ''' new nwl file '''
        
        bus = items[3].split('=')[1]
        newNWLline = bus + ',1'
        fileNWL.write(newNWLline + os.linesep)       