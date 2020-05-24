'''
Created on Mar. 22, 2019
Sensor superclass with derivatives of phasor,
smartmeter, prober 

@file    Sesnor.py
@author  Evandro de Souza
@date    2019.11.15  
@version 0.1
@company University of Alberta - Computing Science
'''


import numpy as np
import random
from CktDef import CKTTerm, CKTPhase

class Sensor:
    def __init__(self, 
                 idt, 
                 step_size, 
                 objDSS,  
                 cktElement, 
                 error, 
                 verbose):
        self.idt        = idt
        self.step_size  = int(step_size)
        self.objDSS     = objDSS
        self.cktElement = cktElement
        self.error      = float(error)
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None
        self.time_diff_resolution = 1e-9
        self.randomTime = random.randint(0, 1)
        
    def getLastValue(self):
        if(self.priorValue != None):
            self.priorValue['TS'] = self.priorTime
        return self.priorValue, self.priorTime

    def R2P(self, x):
        return np.abs(x), np.angle(x)
    
    def addNoise(self, x):
        noiseReal = np.random.normal(0, self.error, 1)
        noiseImag = np.random.normal(0, self.error, 1)
        noise = complex(noiseReal, noiseImag)
        return x + noise
    

class Phasor(Sensor):
    def __init__(self, 
                 cktTerminal,
                 cktPhase,
                 idt, 
                 step_size, 
                 objDSS,  
                 cktElement, 
                 error,
                 verbose):
        
        super().__init__(idt, step_size, objDSS, cktElement, error, verbose)
        self.cktTerminal = cktTerminal
        self.cktPhase = cktPhase
        
    def updateValues(self, time):
        if (self.verbose > 2): print('Phasor::updateValues', 
                                     self.cktElement, self.cktTerminal, self.cktPhase)
        
        if (0 == (time % self.step_size)):
            val = {}
            val['IDT'] = self.idt  
            val['TYPE'] = 'Phasor'
            
            if (self.cktPhase == 'PHASE_1'):
                phases = ['PHASE_1']
            elif (self.cktPhase == 'PHASE_2'):
                phases = ['PHASE_2']
            elif (self.cktPhase == 'PHASE_3'):
                phases = ['PHASE_3']
            elif (self.cktPhase == 'PHASE_12'):
                phases = ['PHASE_1', 'PHASE_2']            
            elif (self.cktPhase == 'PHASE_13'):
                phases = ['PHASE_1', 'PHASE_3']
            elif (self.cktPhase == 'PHASE_23'):
                phases = ['PHASE_2', 'PHASE_3']              
            elif (self.cktPhase == 'PHASE_123'):
                phases = ['PHASE_1', 'PHASE_2', 'PHASE_3']

            for ph in phases:
                (VComp, IComp, _) = self.objDSS.getCktElementState(self.cktElement, 
                                                     CKTTerm[self.cktTerminal].value, 
                                                     CKTPhase[ph].value)

                VComp = self.addNoise(VComp)
                IComp = self.addNoise(IComp)
                (VMag, VAng) = self.R2P(VComp)
                (IMag, IAng) = self.R2P(IComp)
                
                if (ph == 'PHASE_1'):
                    val['VA'] = (VMag, VAng)
                    val['IA'] = (IMag, IAng)
                elif (ph == 'PHASE_2'):
                    val['VB'] = (VMag, VAng)
                    val['IB'] = (IMag, IAng)
                elif (ph == 'PHASE_3'):
                    val['VC'] = (VMag, VAng)
                    val['IC'] = (IMag, IAng)

            self.priorTime  = time + self.time_diff_resolution
            self.priorValue = val
        else:
            self.priorTime  = None
            self.priorValue = None          
            
        if (self.verbose > 0 and self.priorValue != None): print('Phasor::updateValues Time = ', self.priorTime, 'Value = ', self.priorValue)
        if (self.verbose > 2): print('Phasor[', self.idt, ']::updateValues v =', val) 


class Smartmeter(Sensor):
    def __init__(self, 
                 cktTerminal,
                 cktPhase,
                 idt, 
                 step_size, 
                 objDSS,  
                 cktElement, 
                 error, 
                 verbose):
        
        super().__init__(idt, step_size, objDSS, cktElement, error, verbose)
        self.cktTerminal = cktTerminal
        self.cktPhase    = cktPhase
        
    def updateValues(self, time):
        if (self.verbose > 2): print('Smartmeter::updateValues', 
                                    self.cktElement, self.cktTerminal, self.cktPhase)
        
        if (0 == time % (self.step_size + self.randomTime)):
            val = {}
            val['IDT'] = self.idt
            val['TYPE'] = 'Smartmeter'
            
            if (self.cktPhase == 'PHASE_1'):
                phases = ['PHASE_1']
            elif (self.cktPhase == 'PHASE_2'):
                phases = ['PHASE_2']
            elif (self.cktPhase == 'PHASE_3'):
                phases = ['PHASE_3']
            elif (self.cktPhase == 'PHASE_12'):
                phases = ['PHASE_1', 'PHASE_2']            
            elif (self.cktPhase == 'PHASE_13'):
                phases = ['PHASE_1', 'PHASE_3']
            elif (self.cktPhase == 'PHASE_23'):
                phases = ['PHASE_2', 'PHASE_3']              
            elif (self.cktPhase == 'PHASE_123'):
                phases = ['PHASE_1', 'PHASE_2', 'PHASE_3']

            for ph in phases:
                (VComp, IComp, _) = self.objDSS.getCktElementState(self.cktElement,                               
                                                     CKTTerm[self.cktTerminal].value, 
                                                     CKTPhase[ph].value)
                
                VComp = self.addNoise(VComp)
                IComp = self.addNoise(IComp)                
                (VMag, _) = self.R2P(VComp)
                SP = (VComp * np.conj(-IComp)).real
                
                #--- for voltage
                if (ph == 'PHASE_1'):
                    val['VA'] = VMag
                    val['SPA'] = SP
                elif (ph == 'PHASE_2'):
                    val['VB'] = VMag
                    val['SPB'] = SP
                elif (ph == 'PHASE_3'):
                    val['VC'] = VMag
                    val['SPC'] = SP

            self.priorTime  = time + self.time_diff_resolution
            self.priorValue = val
        else:
            self.priorTime  = None
            self.priorValue = None          
            
        if (self.verbose > 0 and self.priorValue != None): print('Smartmeter::updateValues Time = ', self.priorTime, 'Value = ', self.priorValue)
        if (self.verbose > 2): print('Smartmeter[', self.idt, ']::updateValues v =', val)
        

class Prober(Sensor):
    def __init__(self, 
                 cktTerminal,
                 cktPhase,
                 cktProperty,
                 idt, 
                 step_size, 
                 objDSS,  
                 cktElement, 
                 error, 
                 verbose):
        
        super().__init__(idt, step_size, objDSS, cktElement, error, verbose)
        self.cktTerminal = cktTerminal
        self.cktPhase    = cktPhase
        self.cktProperty = cktProperty
        
    def updateValues(self, time):
        if (self.verbose > 0): print('Prober::updateValues', 
                                    self.cktElement, self.cktTerminal, self.cktPhase, self.cktProperty)
        
        if (0 == time % (self.step_size + self.randomTime)):
            val = {}
            (VComp, IComp, PComp) = self.objDSS.getCktElementState(self.cktElement, 
                                                     CKTTerm[self.cktTerminal].value, 
                                                     CKTPhase[self.cktPhase].value)
            VComp = self.addNoise(VComp)
            IComp = self.addNoise(IComp)
            PComp = self.addNoise(PComp)
            if ((self.cktProperty == 'V')):
                val['V'] = self.R2P(VComp)
            elif  ((self.cktProperty == 'I')):
                val['I'] = self.R2P(IComp)
            elif   ((self.cktProperty == 'S')):
                val['S'] = (np.abs(PComp.real), np.abs(PComp.imag))
            
            self.priorTime  = time + self.time_diff_resolution
            self.priorValue = val
        else:
            self.priorTime  = None
            self.priorValue = None          
            
        if (self.verbose > 0): print('Prober::updateValues Time = ', self.priorTime, 'Value = ', self.priorValue)
        if (self.verbose > 2): print('Prober[', self.idt, ']::updateValues v =', val)
    