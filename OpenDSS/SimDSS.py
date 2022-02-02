'''
 # OpenDSS wrapper class for SmartGrid studies
'''

__author__    = "Evandro de Souza"
__copyright__ = "Copyright (c) 2019, Evandro de Souza"
__credits__   = "University of Alberta / FES"
__license__   = "GPL-3"
__version__   = "0.0.5-alpha"


import os
import sys
import csv
import opendssdirect as dss
import numpy as np
import logging


class SimDSS(object):
 
    '''
    Class that encapsulates opendssdirect.py library and provides
    easy way to calculate/update the circuit system state

    Attributes
    ----------
    _nNodes        : int
        number of nodes in the circuit
    _NodeList      : list
        name of the nodes
    _terminal2node : dict
        mapping of: key(node name), value(node index according YNodeOrder)
    _YMatrix       = numpy array
        complex values of the admittance matrix of the last solution 
        with dimension (nNode x nNodes)
    _YMatrixPrev
        same as _YMatrix, but from the previous solution
    _nodewithload  : list
        0/1 list meaning the absence or presence of load in the nodes (YNodeOrder)
    _iPQ           = numpy array
        complex values of the tuples <P,Q> of inelastic load dimension (nNode)
    _hasIPQ        = boolean
        set True if there is inelastic load for the nodes
    _Vckt          = numpy array
        complex values of the node voltages of the last solution
    _VcktPrev      
        same as _Vckt, but from the previous solution
    _I_in          = numpy array
        complex values of the node input current of the last solution
    _I_inPrev
        same as _I_in, but from the previous solution
    _I_out         = numpy array
        complex values of the node output current of the last solution
    _I_outPrev
        same as _I_out, but from the previous solution
    '''


    def __init__(self, topofile, nwlfile, ilpqfile = ""):
        '''
        Initialize class and and obtain initial solution given by the initial parameters
        
        Parameters
        ----------
        topofile : str
            Name of the topology file
        nwlfile : str
            Name of the node with load file
        ilpqfile : str
            Name of the inelastic load file
        '''

        self._nNodes        = None
        self._NodeList      = []
        self._terminal2node = []
        self._YMatrix       = None
        self._YMatrixPrev   = None
        self._nodewithload  = None
        self._iPQ           = None
        self._hasIPQ        = False
        self._Vckt          = None
        self._I_in          = None
        self._I_out         = None   
        self._VMagAnglePu   = None

        logging.disable(logging.NOTSET)
        logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stderr, level=logging.ERROR)  
      
        self._readTopo(topofile)
        self._nNodes = dss.Circuit.NumNodes()
        self._mapTerminal2Node()
        #--- Remove Ymatrix calculation because slows down too much for large circuits
        #self._YMatrix = self._constructYMatrix()
        self._readNodeWithLoad(nwlfile)
        if (ilpqfile != ""):
            self._iPQ = self._readInelasticLoadPQ(ilpqfile)
            self._hasIPQ = True
        self._Vckt  = np.zeros((self._nNodes), dtype=complex)
        self._I_in  = np.zeros((self._nNodes), dtype=complex)
        self._I_out = np.zeros((self._nNodes), dtype=complex)
        self._calcVComplex()
        self._calcInOutCurrent()
        self._calcVMagAnglePu()

        logging.debug('Start SimDSS Class')
        logging.debug('Topology file: %s', topofile)
        logging.debug('Circuit.AllNodeNames: %s', dss.Circuit.AllNodeNames())
        logging.debug('nNode: %s', self._nNodes)
        logging.debug('terminal2node: %s', self._terminal2node)                
        #logging.debug('YMatrix shape: %s', self._YMatrix.shape)
        logging.debug('NodeWithLoad File: %s', nwlfile) 
        logging.debug('NodeWithLoad %s', self._nodewithload)                 

    #-------------------#
    #- Private Methods -#
    #-------------------#

    def _mapTerminal2Node(self):
        '''
        Create a mapping between node name to a index
        '''
        NList = dss.Circuit.YNodeOrder()
        for idx in range(self._nNodes):
            self._NodeList.insert(idx, (NList[idx]).lower())
        valueArray = range(self._nNodes)
        self._terminal2node = dict(zip(self._NodeList, valueArray))
 
    
    def _readTopo(self, topofile):
        '''
        Read circuit topology from file
        
        The class assumes that the file is in the current directory
        
        Parameters
        ----------
        arg1 : str
            Name of the file
        '''
        current_directory = os.path.dirname(os.path.realpath(__file__))
        pathTopoFile = os.path.abspath(
            os.path.join(current_directory, topofile)
        )
        if not os.path.isfile(pathTopoFile):
            print('File does not exist: ' + pathTopoFile)
            sys.exit()
        else:
            dss.Solution.Cleanup()
            areg = dss.run_command('Redirect ' + pathTopoFile)
            if areg:
                print('Config file error: ' + areg)
                sys.exit()
            dss.Solution.Solve()

 
    def _readNodeWithLoad(self, nwlfile):
        '''
        Read NodeWithLoad file
             
        It is assumed that the file is in the current directory
        
        Parameters
        ----------
        arg1 : str
            Name of the file
        '''
        current_directory = os.path.dirname(os.path.realpath(__file__))
        pathToFile = os.path.abspath(
            os.path.join(current_directory, nwlfile)
        )
        if not os.path.isfile(pathToFile):
            print('File LoadsPerNode does not exist: ' + pathToFile)
            sys.exit()
        else:
            with open(pathToFile, 'r') as csvFile:
                csvobj = csv.reader(csvFile)
                self._nodewithload = {rows[0]:int(rows[1]) for rows in csvobj}
 
          
    def _readInelasticLoadPQ(self, file):
        '''
        Read inelastic load from file
        
        The class assumes that the file is in the current directory
        After the file is read, the load is inserted in the circuit and
        a new solution is calculated
        
        Parameters
        ----------
        arg1 : str
            Name of the file
            
        Returns
        -------
        numpy array
                It returns an array of P and Q tuples, for each node
        '''
        current_directory = os.path.dirname(os.path.realpath(__file__))
        pathToFile = os.path.abspath(
            os.path.join(current_directory, file)
        )
        if not os.path.isfile(pathToFile):
            print('File does not exist: ' + pathToFile)
            sys.exit()
        else:
            with open(pathToFile, 'r') as csvFile:
                csvobj = csv.reader(csvFile)
                data = list(csvobj)
                
            PQ = np.zeros((self._nNodes, 2))
            for i in range(len(data)):
                nodeName = data[i][0]
                idx = self._terminal2node[nodeName]
                if self._nodewithload[nodeName] > 0:
                    PQ[idx][0] = float(data[i][1])
                    PQ[idx][1] = float(data[i][2])
                    logging.debug('New Load.' + nodeName +
                                  ' Bus1='    + nodeName +
                                  ' kW='      + data[i][1] +
                                  ' kvar='    + data[i][2])                  
                    dss.run_command(
                        'New Load.' + nodeName + 
                        ' Bus1='    + nodeName +
                        ' kW='      + data[i][1] +
                        ' kvar='    + data[i][2])
            #-- after loading a new solution is necessary
            dss.Solution.Solve()
                    
        return PQ

        
    def _constructYMatrix(self):
        '''
        Calculate the nodal admittance matrix YMatrix
            
        Returns
        -------
        numpy array
                It returns a complex array of Y admittance matrix        
        '''
        #- disconnect vsources and loads
        dss.run_command('vsource.source.enabled = no')
        dss.run_command('batchedit load..* enabled=no')
        #- extract YMatrix
        dss.Solution.Solve()
        Ybus   = dss.Circuit.SystemY()  #--- slow
        Yres   = np.reshape(Ybus, (self._nNodes, self._nNodes*2)) #--- slow
        #- populate complex polyphase nodal Y
        Y = np.zeros((self._nNodes, self._nNodes), dtype=complex)
        for i in range(self._nNodes):   #--- very very slow
            Y[:, i] = Yres[:, 2*i] + 1j*Yres[:, 2*i + 1]
        self._YMatrixPrev = self._YMatrix
        self._YMatrix = Y
        #- reconnect vsources and loads
        dss.run_command('vsource.source.enabled = yes')
        dss.run_command('batchedit load..* enabled=yes')
        #- return to the previous solution
        dss.Solution.Solve()    
    
        return Y    
    

    def _calcVComplex(self):
        '''
        Calculate V: a vector of size NODES containing complex voltage at each node
            
        Returns
        -------
        numpy array
            It returns an array of Voltage for each node
        '''
        vckt = dss.Circuit.YNodeVArray()
        V = np.zeros(int(self._nNodes), dtype=complex)
        
        for i in range(int(self._nNodes)):
            V[i] = vckt[2*i] + 1j*vckt[2*i + 1]
            self._Vckt[i] = V[i]
        
        return V
   

    def _calcVMagAnglePu(self):
        '''
        Calculate BusMagAnglePu: the voltage magnitude and angle in p.u. for each bus node. BusVMagAngle[bus][node][property]
        '''        
        BusNames = dss.Circuit.AllBusNames()
        self._VMagAnglePu = {}
        for bus in BusNames:
            self._VMagAnglePu[bus] = {}
            dss.Circuit.SetActiveBus(bus)
            puVmagAngle = dss.Bus.puVmagAngle()
            Nodes = dss.Bus.Nodes()
            for j in range(len(Nodes)):
                self._VMagAnglePu[bus][Nodes[j]] = {}
                self._VMagAnglePu[bus][Nodes[j]]['VMag']  = puVmagAngle[2*j]
                self._VMagAnglePu[bus][Nodes[j]]['Angle'] = puVmagAngle[2*j + 1]        


    def _calcInOutCurrent(self):
        '''
        Calculate input/output current for the circuit
         
        Returns
        -------
        numpy arrays
            It returns two arrays, one for I_in and other for I_out, for each node
        ''' 
        # sender-end currents
        I_1 = np.zeros(self._nNodes, dtype=complex)
        # receiving-end currents
        I_2 = np.zeros(self._nNodes, dtype=complex)
        
        #-- get current for the line elements
        line_elem = dss.Lines.First()
        while line_elem > 0:
            dss.Circuit.SetActiveElement('Line.' + dss.Lines.Name())
            # get buses that are connected by a given line
            blist = dss.CktElement.BusNames()
            # extract the sender node name
            senderBus = blist[0].split('.')[0]
            # extract the receiver node name
            receiverBus = blist[1].split('.')[0]
            # extract currents passing through the line (real and img components)
            CArray = dss.CktElement.Currents()
            CArray = np.array(CArray)
            # this returns real and img parts of current flow for each phase in A
            OArray = dss.CktElement.NodeOrder()

            for p in range(int(len(CArray)/4)):
                # get complex current at the sending-end
                idx = self._terminal2node[senderBus + '.' + str(OArray[p])]
                I_1[idx] = I_1[idx] + CArray[2*p] + CArray[2*p+1]*1j

            for p in range(int(len(CArray)/4), int(len(CArray)/2)):
                # get complex current at the receiving-end
                idx = self._terminal2node[receiverBus + '.' + str(OArray[p])]
                I_2[idx] = I_2[idx] + CArray[2*p] + CArray[2*p+1]*1j             
 
            line_elem = dss.Lines.Next()        
  
        #-- get current for the transformer elements
        line_elem = dss.Transformers.First()
        while line_elem > 0:
            dss.Circuit.SetActiveElement('Transformer.' + dss.Transformers.Name())
            # get buses that are connected by a given line
            blist = dss.CktElement.BusNames()
            # extract the sender node name
            senderBus = blist[0].split('.')[0]
            # extract the receiver node name
            receiverBus = blist[1].split('.')[0]
            # extract currents passing through the line (real and img components)
            CArray = dss.CktElement.Currents()
            CArray = np.array(CArray)
            # this returns real and img parts of current flow for each phase in A
            OArray = dss.CktElement.NodeOrder()

            for p in range(int(len(CArray)/4)-1):
                # get complex current at the sending-end
                idx = self._terminal2node[senderBus + '.' + str(OArray[p])]
                I_1[idx] = I_1[idx] + CArray[2*p] + CArray[2*p+1]*1j

            for p in range(int(len(CArray)/4), int(len(CArray)/2)-1):
                # get complex current at the receiving-end
                idx = self._terminal2node[receiverBus + '.' + str(OArray[p])]
                I_2[idx] = I_2[idx] + CArray[2*p] + CArray[2*p+1]*1j                
 
            line_elem = dss.Transformers.Next()                
        
        self._I_in  = I_1
        self._I_out = I_2
        
        return I_1, I_2


    def _updateSystemState(self):
        '''
        Method for execute all the operation necessary to update the system state after a change has happened
        '''
        #self._YMatrix = self._constructYMatrix()
        dss.Solution.Solve()
        self.Vckt = self._calcVComplex()
        (self._In, self._I_out) = self._calcInOutCurrent()
        self._calcVMagAnglePu()
        

    def _runPF(self, ePQ=[]):
        '''
        Recalculate the system state
        
        The method can calculate the system state for the following conditions:
        (a) inelastic load only: without input parameters
        (b) inelastic and elastic load: with ePQ parameter 

        Parameters
        ----------
        arg1 : numpy array
            Array with <P,Q> tuples for each node in the system
            
        Returns
        -------
        V       - Voltage per node
        I_in    - Input current per node
        I_out   - Output current per node
        YMatrix - Admittance matrix
        '''
        if ePQ == []:
            logging.debug('Running *runPF* for Inelastic load')
            #-- set system load using only inelastic load
            for i in range(self._nNodes):
                logging.debug('Edit Load.' + format(self._nodewithload[i][0]) + 
                                  ' Bus1='     + self._nodewithload[i][0] +
                                  ' kW='       + str(self._iPQ[i][0]) +
                                  ' kvar='     + str(self._iPQ[i][1]))       
                dss.run_command(
                    'Edit Load.' + format(self._nodewithload[i][0]) + 
                    ' Bus1='     + self._nodewithload[i][0] +
                    ' kW='       + str(self._iPQ[i][0]) +
                    ' kvar='     + str(self._iPQ[i][1]))
        else:
            logging.debug('Running *runPF* for Inelastic and Elastic load')   
            #-- set system load using inelastic and elastic loads
            for i in range(self._nNodes):
                if int(self._nodewithload[i][1]) > 0:
                    logging.debug('Edit Load.' + format(self._nodewithload[i][0]) + 
                                  ' Bus1='     + self._nodewithload[i][0] +
                                  ' kW='       + str(self._iPQ[i][0] + ePQ[i][0]/1000) +
                                  ' kvar='     + str(self._iPQ[i][1] + ePQ[i][1]/1000))       
                    dss.run_command(
                        'Edit Load.' + format(self._nodewithload[i][0]) + 
                        ' Bus1='     + self._nodewithload[i][0] +
                        ' kW='       + str(self._iPQ[i][0] + ePQ[i][0]/1000) +
                        ' kvar='     + str(self._iPQ[i][1] + ePQ[i][1]/1000))    
                else:
                    logging.debug('Edit Load.' + format(self._nodewithload[i][0]) + 
                                  ' Bus1='     + self._nodewithload[i][0] +
                                  ' kW='       + str(self._iPQ[i][0]) +
                                  ' kvar='     + str(self._iPQ[i][1]))       
                    dss.run_command(
                        'Edit Load.' + format(self._nodewithload[i][0]) + 
                        ' Bus1='     + self._nodewithload[i][0] +
                        ' kW='       + str(self._iPQ[i][0]) +
                        ' kvar='     + str(self._iPQ[i][1]))                                           
                    
        #-- solve circuit
        dss.Solution.Solve()     
        
        #-- if circuit converge
        if dss.Solution.Converged():
            
            #-- calculate V in the nodes
            V = self._calcVComplex()
            
            #-- calculate I_in and I_out
            (I_in, I_out) = self._calcInOutCurrent()
            
            #-- caculate YMatrix
            #-- maybe not necessary because there was no topology change
            YMatrix = self._constructYMatrix()
            
            #-- return Y, V, I1, I2
            return V, I_in, I_out, YMatrix
        
        else:
            return 0,0,0,0



    #------------------#
    #- Public Methods -#
    #------------------#
    
    #-----------#
    #--- GET ---#
    #-----------#

    def getnNodes(self):
        '''
        Return the number of nodes of the current circuit
        
        Returns
        -------
        _nNodes : int
        '''
                
        return self._nNodes      
    

    def getNodeWithLoad(self):
        '''
        Retruns the list of nodes that have load
        
        Returns
        -------
        nodewithload : list
        '''
        
        return self._nodewithload
    
    
    def getCktElementState(self, cktElement, cktTerminal, cktPhase):
        '''
        Method to retrieve V and I from a circuit element.
        cktTerminal must be 1 or 2
        cktPhase must be 1, 2 or 3. The case of ground conductor is not addressed
        
        Parameters
        ----------
        cktElement : str
            Name of the circuit element to probe
        cktTerminal : int
            Number to designate the terminal of the element to probe
            1 - BUS1, 2 - BUS2
        cktPhase : int
            Phase number
        
        Returns
        -------
        VComp : Voltage complex number value for the specific, circuit element, terminal and phase
        IComp : Current complex number value for the specific, circuit element, terminal and phase 
        ''' 
        
        #-- set element as active
        dss.Circuit.SetActiveElement(cktElement)
        
        #-- get the number of terminals, conductors and phases           
        nTerm   = dss.CktElement.NumTerminals()
        nPhases = dss.CktElement.NumPhases()  
        ndOrder = dss.CktElement.NodeOrder()             
        elemNames = dss.Circuit.AllElementNames()

        #-- Verify if parameters are fine for the circuit
        if cktElement.lower() not in (name.lower() for name in elemNames):
            raise Exception('cktElement:', cktElement, ' not in the circuit')
        if cktTerminal > nTerm:
            raise Exception('ckTerminal value', cktTerminal, ' exceeds the number of terminals on this circuit element: {}'.format(nTerm))
        if cktTerminal < 1:
            raise Exception('ckTerminal value is invalid: {}'.format(cktTerminal))
        if cktPhase < 1:
            raise Exception('ckPhase value is invalid: {}'.format(cktPhase)) 
                     
       
        #-- Get voltages and currents
        VArray = dss.CktElement.Voltages()
        VArray = np.array(VArray)
        CArray = dss.CktElement.Currents()
        CArray = np.array(CArray)
        PArray = dss.CktElement.Powers()
        PArray = np.array(PArray)
            
        #-- calculate the position in the array
        if cktTerminal == 1:
            st = 0
        else:
            st = int(len(ndOrder) / 2)
        idx = 0
        while (idx < nPhases):
            if (ndOrder[st+idx] == cktPhase):
                pos = (st+idx)*2
                break
            idx = idx + 1
        
        #-- extract values
        VComp = VArray[pos] + VArray[pos+1]*1j
        IComp = CArray[pos] + CArray[pos+1]*1j
        PComp = PArray[pos] + PArray[pos+1]*1j

        return VComp, IComp, PComp


    def getYMatrix(self):
        '''
        Return the admittance matrix
        
        
        Returns
        -------
        YMatrix : numpy array
                It returns a complex array of Y admittance matrix in node order
        '''        

        return self._constructYMatrix()
    
    
    def getTrafoTap(self, cktTrafo):
        '''
        Get the TAP of the tranformer cktTrafo

        Parameters
        ----------
        cktTrafo : str
            Name of the transformer circuit element decrease
            
        Returns
        -------
        Current Tap : float
        '''        
    
        nameTrafo = cktTrafo.split('.')[1]
        trafoList = dss.Transformers.AllNames()
        if nameTrafo.lower() not in trafoList:
            raise Exception('cktTrafo:', cktTrafo, ' not in the circuit')
         
        dss.Transformers.Name(nameTrafo)
        return dss.Transformers.Tap()   
 
    
    def getPQ(self, cktElement):
        '''
        Method to retrieve P and Q from a element
        
        Parameters
        ----------
        cktElement : str
            Name of the circuit element to probe. Bus name

        
        Returns
        -------
        P  : KiloWatts in the load
        Q  : Reactive Kvar in the load 
        ''' 
        
        #-- Verify if parameters are fine for the circuit
        nameLoad = cktElement.split('.',1)[1]
        LoadNames = dss.Loads.AllNames()
        if (nameLoad.lower() not in LoadNames):
            raise Exception('cktElement:', cktElement, ' not in the circuit')

        dss.Loads.Name(nameLoad)

        return dss.Loads.kW(), dss.Loads.kvar()        
        
        
    def getSwitch(self,cktElement, cktTerminal, cktPhase):
        '''
        Get postion of a specified terminal conductor switch. All conductors in the terminals of all circuit
        elements have an inherent switch. This command can be used to open one or more conductors
        in a specified terminal.
        
        Parameters
        ----------
        cktElement : str
            Name of the element to open
        cktTerminal : int
            terminal of the element
        cktPhase: int
            phase of the terminal. If it is 0, all phases are opened
            
        Returns
        -------
        Pos  : int
            Switch postion 
        ''' 
        
        #-- Verify if parameters are fine for the circuit
        nameLines = cktElement.split('.')[1]
        LineList = dss.Lines.AllNames()
        if nameLines.lower() not in LineList:
            raise Exception('cktTrafo:', cktElement, ' not in the circuit')
        
        #-- set element as active
        dss.Circuit.SetActiveElement(cktElement)            

        #-- get the number of terminals, conductors and phases
        nTerm   = dss.CktElement.NumTerminals()   
        elemNames = dss.Circuit.AllElementNames()

        #-- Verify if parameters are fine for the circuit
        if cktElement.lower() not in (name.lower() for name in elemNames):
            raise Exception('cktElement:', cktElement, ' not in the circuit')
        if cktTerminal > nTerm:
            raise Exception('ckTerminal value', cktTerminal, ' exceeds the number of terminals on this circuit element: {}'.format(nTerm))
        if cktTerminal < 1:
            raise Exception('ckTerminal value is invalid: {}'.format(cktTerminal))
        if cktPhase < 0:
            raise Exception('ckPhase value is invalid: {}'.format(cktPhase)) 

        pos = dss.CktElement.IsOpen(cktTerminal, cktPhase)

        return pos 
 

    def getVMagAnglePu(self, cktElement, cktPhase):
        '''
        Method to retrieve VMag and Angle from a node in a bus
        cktPhase must be 1, 2 or 3. The case of ground conductor is not addressed
        
        Parameters
        ----------
        cktElement : str
            Name of the circuit element to probe. Bus name
        cktPhase : int
            Phase number
        
        Returns
        -------
        VMag  : Voltage magnitude in p.u. 
        Angle : Angle of voltage 
        ''' 
        
        #-- Verify if parameters are fine for the circuit
        BusNames = dss.Circuit.AllBusNames()
        if (cktElement.lower() not in BusNames):
            raise Exception('cktElement:', cktElement, ' not in the circuit')
        if cktPhase < 1:
            raise Exception('ckPhase value is invalid: {}'.format(cktPhase)) 
        
        if (cktPhase in (self._VMagAnglePu[cktElement.lower()]).keys()):
            return self._VMagAnglePu[cktElement.lower()][cktPhase]['VMag'], self._VMagAnglePu[cktElement.lower()][cktPhase]['Angle']
        else:
            raise Exception('ckPhase does not exist for this node bus')

    
        
    #-----------#
    #--- SET ---#
    #-----------#

    def setLoads(self, ePQ):
        '''
        Update circuit state with new set of loads. Add new load set to the 
        inelastic loads 

        Parameters
        ----------
        arg1 : numpy array
            Array with <nodeName, P, Q> tuples for each node in the system        
        '''
        
        #-- for each load record received
        for i in range(len(ePQ)):
            #-- extract the node 
            nodeName = ePQ[i][0]
            #-- find the index according to terminal2node map
            idx = self._terminal2node[nodeName]
            #-- if the number of homes in the load is greater than zero 
            if self._nodewithload[nodeName] > 0:
                if (self._hasIPQ == True):
                    logging.debug('New Load.' + nodeName +
                                  ' Bus1='    + nodeName +
                                  ' kW='      + str(self._iPQ[idx][0] + ePQ[i][1]) +
                                  ' kvar='    + str(self._iPQ[idx][1] + ePQ[i][2]))                  
                    
                    dss.run_command(
                        'New Load.' + nodeName + 
                        ' Bus1='    + nodeName +
                        ' kW='      + str(self._iPQ[idx][0] + ePQ[i][1]) +
                        ' kvar='    + str(self._iPQ[idx][1] + ePQ[i][2]))
                else:
                    logging.debug('New Load.' + nodeName +
                                  ' Bus1='    + nodeName +
                                  ' kW='      + str(ePQ[i][1]) +
                                  ' kvar='    + str(ePQ[i][2]))                  
                    
                    dss.run_command(
                        'New Load.' + nodeName + 
                        ' Bus1='    + nodeName +
                        ' kW='      + str(ePQ[i][1]) +
                        ' kvar='    + str(ePQ[i][2]))                    
                
        #-- after setting a new load, a new system state has to be calculated
        self._updateSystemState()


    def setSwitch(self, operation, cktElement, cktTerminal, cktPhase):
        '''
        Open/Close a specified terminal conductor switch. All conductors in the terminals of all circuit
        elements have an inherent switch. This command can be used to open one or more conductors
        in a specified terminal. If the 'Cond=' field is 0 or omitted, all conductors are opened.
        
        Parameters
        ----------
        operation : int
            0 - open switch, 1 - close switch
        cktElement : str
            Name of the element to open
        cktTerminal : int
            terminal of the element
        cktPhase: int
            phase of the terminal. If it is 0, all phases are opened
        ''' 

        #-- Verify if parameters are fine for the circuit
        if operation not in [0, 1]:
            raise Exception('Switch Operation:', operation, ' not valid')    

        #-- set element as active
        dss.Circuit.SetActiveElement(cktElement)            

        #-- get the number of terminals, conductors and phases 
        nTerm   = dss.CktElement.NumTerminals()   
        elemNames = dss.Circuit.AllElementNames()

        #-- Verify if parameters are fine for the circuit
        if cktElement.lower() not in (name.lower() for name in elemNames):
            raise Exception('cktElement:', cktElement, ' not in the circuit')
        if cktTerminal > nTerm:
            raise Exception('ckTerminal value', cktTerminal, ' exceeds the number of terminals on this circuit element: {}'.format(nTerm))
        if cktTerminal < 1:
            raise Exception('ckTerminal value is invalid: {}'.format(cktTerminal))
        if cktPhase < 0:
            raise Exception('ckPhase value is invalid: {}'.format(cktPhase)) 

        if (operation == 0):
            dss.CktElement.Open(cktTerminal, cktPhase)
        else:
            dss.CktElement.Close(cktTerminal, cktPhase)

        #-- topology change. Need a new solution
        self._updateSystemState()


    def setTrafoTap(self, cktTrafo, tapOrientation=0, tapUnits=1):
        '''
        Decrease one TAP to the tranformer cktTrafo
        The increase is calculated by:
           NewTapSettings = (MaxTap - MinTap)/NumTaps
        up to the limit of MaxTap

        Parameters
        ----------
        cktTrafo : str
            Name of the transformer circuit element decrease
        tapOrientation: str
            Direction of tap: Up (increase ratio), Down (decrease ratio)
        tapUnits: integer
            Number of taps to change the current state
        '''
        
        tapOrientation = int(tapOrientation)
        if tapOrientation not in [-1, 0, 1]:
            raise Exception('tap value:', tapOrientation, ' not valid')
        
        nameTrafo = cktTrafo.split('.')[1]
        trafoList = dss.Transformers.AllNames()
        if nameTrafo.lower() not in trafoList:
            raise Exception('cktTrafo:', cktTrafo, ' not in the circuit')

        dss.Transformers.Name(nameTrafo)
        maxtap  = dss.Transformers.MaxTap()
        mintap  = dss.Transformers.MinTap()
        numtaps = dss.Transformers.NumTaps()
        curtap  = dss.Transformers.Tap()    
            
        newtap  = curtap + tapOrientation * ((maxtap - mintap)/numtaps) * tapUnits        

        if(newtap > mintap and newtap < maxtap):        
            dss.Transformers.Tap(newtap)
            curtap  = dss.Transformers.Tap()
            self._updateSystemState()
    
    
    #------------#
    #--- SHOW ---#
    #------------#

    def showLoads(self):
        '''
        Print a formatted version for P and Q values per node, using openDSS format
        '''
        load_elem = dss.Loads.First()
        print('Loads on circuit: ', dss.Circuit.Name())
        while load_elem > 0:
            dss.Circuit.SetActiveElement('Load.' + dss.Loads.Name())
            lName = dss.Loads.Name()
            blist = dss.CktElement.BusNames()
            senderBus = blist[0].split('.')[0]
            loadPF   = dss.Loads.PF()
            loadKW   = dss.Loads.kW()
            loadKVAR = dss.Loads.kvar()
            print('LOAD: name =', lName.ljust(10), 
                  ' SenderBus =', senderBus.ljust(10),
                  ' PF =',        "{:.{}f}".format(loadPF,2), 
                  ' kW =',        "{:10.4f}".format(loadKW), 
                  ' kvar =',      "{:10.4f}".format(loadKVAR))            
            load_elem = dss.Loads.Next()           


    def showVNodes(self):
        '''
        Print a formatted version of the voltage per node
        '''
        
        print('Show Voltage by node')
        for i in range(int(self._nNodes)):
            nodeName = list(self._terminal2node.keys())[list(self._terminal2node.values()).index(i)] 
            print(nodeName.ljust(12), "({0.real:15.4f} + {0.imag:15.4f}i)".format(self._Vckt[i],4), "{:13.4f}".format(np.abs(self._Vckt[i])))       


    def showIinout(self):
        '''
        Print a formatted version of the Input/Output current per node
        '''

        print('Show I2 / I1 Currents by node')
        print('Receiver side         I2-Real       I2-Imaginary  |  Sender side           I1-Real       I1-Imaginary')
        print('-----------------------------------------------------------------------------------------------------')
        for i in range(int(self._nNodes)):
            nodeName = list(self._terminal2node.keys())[list(self._terminal2node.values()).index(i)]        
            print(nodeName.ljust(12), 
                  "({0.real:15.4f} + {0.imag:15.4f}i)".format(self._I_out[i],4), '               ',
                  "({0.real:15.4f} + {0.imag:15.4f}i)".format(self._I_in[i],4))


    def showVMagAnglePu(self):
        '''
        Print a formatted version for VMag and Angle values per node in p.u.
        '''
        print('VMag and Angle in Pu (L-N): ')
        BusNames = dss.Circuit.AllBusNames()
        for bus in BusNames:
            Nodes = self._VMagAnglePu[bus].keys()
            print(bus.ljust(10), end=" ")
            for nd in Nodes:
                print("Phase:", nd,  end = " ")
                print("VMag:",  "{:6.4f}".format(np.round(self._VMagAnglePu[bus][nd]['VMag'],4)), end = " ")
                print("Angle:", "{:7.2f}".format(np.round(self._VMagAnglePu[bus][nd]['Angle'],2)), end = "   ")
            print("")


    def showYMatrixDiff(self):
        '''
        Show the admittance matrix difference
        '''
        
        def R2P(x):
            return np.abs(x), np.angle(x)
        
        Ydiff = self._YMatrix - self._YMatrixPrev
        (i,j) = np.where(Ydiff != 0)    
        n = len(i)
        for k in range(n):
            print('RECT  ', k, i[k], j[k], self._YMatrixPrev[i[k],j[k]], self._YMatrix[i[k],i[k]])
            print('POLAR ', k, i[k], j[k], R2P(self._YMatrixPrev[i[k],j[k]]), R2P(self._YMatrix[i[k],i[k]]))

    
    def showYMatrix(self):
        '''
        Print a formatted version of the admittance matrix
        '''   

        YMatrix = self._constructYMatrix()
        NList = dss.Circuit.YNodeOrder()
        print('Show Admitance Matrix - Size:', YMatrix.shape)
        print(" ".ljust(13), end = '')
        for nodeName in NList:
            print(nodeName.ljust(21), end = '')
        print()
        
        for row in range(self._nNodes):
            print(NList[row].ljust(13), end = '')
            for col in range(self._nNodes):
                print("({0.real:7.4f} + {0.imag:7.4f}i)".format(YMatrix[row, col],4), end=' ')
            print()   


    #--------------#
    #--- CREATE ---#
    #--------------#

    def createAdjMatrix(self, fname):
        '''
        Method to save adjacency matrix of the eletric network
        The circuit must have been already loaded
        
        Parameters
        ----------
        fname : str
            Name of the file to save the matrix
        
        Returns
        -------
        None
        ''' 

        ''' extract all bus names and attribute an index '''
        bus_names = dss.Circuit.AllBusNames()
        
        ''' create adj matrix all zero '''
        adjMatrix = np.zeros((len(bus_names), len(bus_names)), dtype=bool)
        edgeList = []
        
        ''' list all lines and extract src/dst '''
        ''' populate a links list without duplication'''
        ''' add 1 to matrix index src-dst and dst-src '''
        line_elem = dss.Lines.First()
        while line_elem > 0:
            lName = dss.Lines.Name()
            blist = dss.CktElement.BusNames()
            src = blist[0].split('.')[0]
            dst = blist[1].split('.')[0]
            pos_src = bus_names.index(src)
            pos_dst = bus_names.index(dst)
            adjMatrix[pos_src, pos_dst] = True
            adjMatrix[pos_dst, pos_src] = True
            if ((pos_src, pos_dst)) not in edgeList:
                edgeList.append((pos_src, pos_dst))
            print(lName,  src, dst)
            line_elem = dss.Lines.Next()     
                 
        ''' repeat for all transformers '''
        transf_elem = dss.Transformers.First()
        while transf_elem > 0:
            lName = dss.Transformers.Name()
            blist = dss.CktElement.BusNames()
            src = blist[0].split('.')[0]
            dst = blist[1].split('.')[0]
            pos_src = bus_names.index(src)
            pos_dst = bus_names.index(dst)
            adjMatrix[pos_src, pos_dst] = True
            adjMatrix[pos_dst, pos_src] = True
            if ((pos_src, pos_dst)) not in edgeList:
                edgeList.append((pos_src, pos_dst))
            print(lName,  src, dst)
            transf_elem = dss.Transformers.Next()             
            
        ''' save adj matrix file '''
        np.savetxt(fname, adjMatrix, fmt='%d')
        

if __name__ == '__main__':
    print('SimDSS class file. Version: ', __version__)

   
    
