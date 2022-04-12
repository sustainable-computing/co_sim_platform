'''
Created on Mar. 22, 2019
Based on Code from Cosimulator-Framework Project

@file    LoadGenerator.py
@author  Evandro de Souza
@date    2019.12.218 
@version 0.2
@company University of Alberta - Computing Science
'''

import os
import sys
import numpy as np
import logging
import math
import scipy.io as spio
import pandas as pd

class LoadGenerator(object):
    '''
    Class that generates a household demand, very simple distribution between 
    the thresholds
    
    Attributes
    ----------
    _nodewithload : str
        Name of the node with load file
    _totalNumberHomes : int
        Total number of homes to create load
    _nNodes        : int
        number of nodes in the circuit
    _time : int
        Time sequence for sine load generation
    _PFLimInf : float
        Power factor inferior limit
    _PFLimSup : float
        Power factor superior limit
    _LoadLimInf : flost
        Load value inferior limit
    _LoadLimSup : float
        Load value supeior limit
    _AmpGain : float
        Load amplitude sine gain
    _Freq : float
        Sine frequency
    _PhaseShift : float
        Sine phase shift

    '''
    
    def __init__(self, 
                 nwlfile, 
                 PFLimInf,
                 PFLimSup,
                 LoadLimInf,
                 LoadLimSup,
                 AmpGain,
                 Freq,
                 PhaseShift):
        '''
        Initialize class and load the node with loads file to determine how many
        houses per node
        '''    
            
        self._totalNumberHomes = 0
        self._nodewithload     = None
        self._nNodes           = 0
        self._time             = 0
        
        self._PFLimInf = PFLimInf
        self._PFLimSup = PFLimSup
        self._LoadLimInf = LoadLimInf
        self._LoadLimSup = LoadLimSup
        self._AmpGain = AmpGain
        self._Freq = Freq
        self._PhaseShift = PhaseShift

        
        #np.random.seed(0)
        np.random.seed(None)
        
        logging.disable(logging.NOTSET)
        logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stderr, level=logging.DEBUG)  
        
        self._readNodeWithLoad(nwlfile)

        logging.debug('Start LoadGenerator Class')
        logging.debug('Node With Load file: %s', nwlfile)
        logging.debug('Total number of homes: %s', self._totalNumberHomes)


    #-------------------#
    #- Private Methods -#
    #-------------------#

    def _readNodeWithLoad(self, nwlfile):
        '''
        Read NodeWithLoad file
             
        It is assumed that the file is in the current directory
        
        Parameters
        ----------
        nwlfile : str
            Name of the file
        '''
        current_directory = os.path.dirname(os.path.realpath(__file__))
        pathToFile = os.path.abspath(
            os.path.join(current_directory, nwlfile)
        )
        if not os.path.isfile(pathToFile):
            print('File NodeWithLoad does not exist: ' + pathToFile)
            sys.exit()
        else:
            self._nodewithload = np.genfromtxt(pathToFile, dtype="U25,f8", delimiter=",")
            self._nNodes = len(self._nodewithload)
            for i in range(len(self._nodewithload)):
                self._totalNumberHomes += int(self._nodewithload[i][1])


    #------------------#
    #- Public Methods -#
    #------------------#

    def createLoads(self):
        '''
        Generate loads for a list of nodes with true power 
        random uniform distribution and power factor also a 
        random uniform distribution
        
        Returns
        -------
        loads : numpy array [node_name, P(true power), Q(reactive power)]
                It returns a list of tuples of 'node name', P and Q
        '''
    
        #-- create artificial samples of random uniform distribution with sinusoidal aspect    
        sLoadP = np.random.uniform(self._LoadLimInf + self._AmpGain*math.sin(2 * math.pi * self._Freq*self._time + self._PhaseShift), 
                                   self._LoadLimSup + self._AmpGain*math.sin(2 * math.pi * self._Freq*self._time + self._PhaseShift), 
                                   self._totalNumberHomes)

        self._time += 1
        sPF    = np.random.uniform(self._PFLimInf,   self._PFLimSup,   self._totalNumberHomes)       
        sLoadQ = np.sqrt(1/(sPF*sPF)-1)*sLoadP
        
        #-- create collection to return
        loadsPQ = []
        
        i = 0
        for j in range(len(self._nodewithload)):
            #-- clean variable for new node load
            ndLoad = [self._nodewithload[j][0], 0, 0]
            for k in range(int(self._nodewithload[j][1])):
                #-- add true power
                ndLoad[1] +=  sLoadP[i]
                #-- add reactive power
                ndLoad[2] += sLoadQ[i]
                i += 1
                k += 1
            #-- append to the list to return
            loadsPQ.append((ndLoad[0], ndLoad[1], ndLoad[2]))
        
        return loadsPQ

    def readLoads(self, test):
        #For testing version configuration
        if(test):
            mat = spio.loadmat('config/loadHour933.mat', squeeze_me=True)
        else:
            mat = spio.loadmat('config/loadHour9.mat', squeeze_me=True)
        
        # Checking the contents of mat file
        # test = {k:v for k, v in mat.items()}
        # data = pd.DataFrame({k: pd.Series(v[0]) for k, v in test.items() if len(v) != 0})
        # data.to_csv("load_mat.csv")

        p = np.array(mat['P'])
        q = np.array(mat['Q'])
        # There are 96 load nodes for test version
        # print("Load Generator: P load size:", len(p))
        # print("Load Generator: Q load size:", len(q))
        # There are 1320 load values per node
        # print("Load Generator: P node 1 load size:", len(p[0]))
        # print("Load Generator: Q node 1 load size:", len(q[0]))
        loadNode = mat['loadNode']
        loadsPQ = []
        for row in range(0, len(p[:, 0])):
            loadsPQ.append((str(loadNode[row]), p[row, self._time], q[row, self._time]))
        self._time += 1
        return loadsPQ


if __name__ == '__main__':
    print('LoadGenerator class file')

        
    
