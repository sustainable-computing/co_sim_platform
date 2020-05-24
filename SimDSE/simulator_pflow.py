'''
Created on Jun. 01, 2019
OpenDSS Mosaik interface, and Sensor/Actuator Models

@file    simulator_pflow.py
@author  Evandro de Souza
@date    2019.06.01  
@version 0.1
@company University of Alberta - Computing Science
'''

import mosaik_api
from SimDSS import SimDSS
from LoadGenerator import LoadGenerator
import numpy as np
import math
import opendssdirect as dss
from Sensor import Phasor, Smartmeter, Prober


META = {
    'models': {
        'Sensor': {
            'public': True,
            'params': ['idt', 'step_size', 'verbose'],
            'attrs': ['v', 't'],
        },
        'Prober': {
            'public': True,
            'params': ['idt','cktTerminal','cktPhase','cktProperty','step_size','cktElement','error','verbose'],
            'attrs': ['v', 't'],
        },   
        'Phasor': {
            'public': True,
            'params': ['idt','cktTerminal','cktPhase','step_size','cktElement','error','verbose'],
            'attrs': ['v', 't'],
        },   
        'Smartmeter': {
            'public': True,
            'params': ['idt','cktTerminal','cktPhase','step_size','cktElement','error','verbose'],
            'attrs': ['v', 't'],
        },               
    },
    'extra_methods': [
        'set_next'
    ],    
}


class ProberSim:
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
        self.objProberSim = Prober(cktTerminal,
                                     cktPhase,
                                     cktProperty,
                                     idt, 
                                     step_size, 
                                     objDSS,  
                                     cktElement, 
                                     error, 
                                     verbose)
    
    def updateValues(self, time):
        self.objProberSim.updateValues(time)    
    
    def getLastValue(self):
        return self.objProberSim.getLastValue()    
    

class PhasorSim:
    def __init__(self, 
             cktTerminal,
             cktPhase,
             idt, 
             step_size, 
             objDSS,  
             cktElement, 
             error, 
             verbose):
        self.objPhasorSim = Phasor(cktTerminal,
                                     cktPhase,
                                     idt, 
                                     step_size, 
                                     objDSS,  
                                     cktElement, 
                                     error, 
                                     verbose)
    
    def updateValues(self, time):
        self.objPhasorSim.updateValues(time)    
    
    def getLastValue(self):
        return self.objPhasorSim.getLastValue()  


class SmartmeterSim:
    def __init__(self, 
             cktTerminal,
             cktPhase,
             idt, 
             step_size, 
             objDSS,  
             cktElement, 
             error, 
             verbose):
        self.objSmartmeterSim = Smartmeter(cktTerminal,
                                           cktPhase,
                                           idt, 
                                           step_size, 
                                           objDSS,  
                                           cktElement, 
                                           error, 
                                           verbose)
    
    def updateValues(self, time):
        self.objSmartmeterSim.updateValues(time)    
    
    def getLastValue(self):
        return self.objSmartmeterSim.getLastValue()  


class PFlowSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.data = {}
        self.actives = {}
        self.entities = {}
        self.next = {}
        self.instances = {}
        self.step_size = 1
        self.loadgen_interval = self.step_size


    def init(self, sid, topofile, nwlfile, loadgen_interval, ilpqfile = "", verbose=0):	
        self.sid = sid       
        self.verbose = verbose
        self.loadgen_interval = loadgen_interval
        
        self.swpos = 0
        self.swcycle = 35
        
        if (self.verbose > 0): print('simulator_pflow::init', self.sid)
        if (self.verbose > 1): print('simulator_pflow::init', topofile, nwlfile, ilpqfile, verbose)

        #--- start opendss
        self.dssObj = SimDSS(topofile, nwlfile, ilpqfile)
        if (self.verbose > 2):
            self.dssObj.showLoads()
            self.dssObj.showVNodes()
            self.dssObj.showIinout()
            self.dssObj.showVMagAnglePu()
            dss.run_command("Show Voltages LN nodes")
            dss.run_command("Show Buses")
        
        
        #--- Generate and save AdjMatrix and YMatrix
#         self.dssObj.createAdjMatrix("config/IEEE33_AdjMatrixFull.txt")
#         YMatrix = self.dssObj.getYMatrix()
#         np.save('config/IEEE33_YMatrixFull.npy', YMatrix)
             
        #--- create instance of LoadGenerator
        self.objLoadGen = LoadGenerator(nwlfile,
                                        PFLimInf   =  0.95,
                                        PFLimSup   =  0.95,
                                        LoadLimInf =  0.4,
                                        LoadLimSup =  0.9,
                                        AmpGain    =  0.25,
                                        Freq       =  1./1250,
                                        PhaseShift = math.pi)

    
        return self.meta


    def create(self, num, model, idt, **kwargs):
        if (self.verbose > 0): print('simulator_pflow::create ', model, idt)

        eid = '%s_%s' % (model, idt)
        self.data[eid] = {}     
        self.instances[eid] = {}

        if (model == 'Prober'): 
            self.instances[eid] = ProberSim(
                                            cktTerminal  = kwargs['cktTerminal'], 
                                            cktPhase     = kwargs['cktPhase'],  
                                            cktProperty  = kwargs['cktProperty'],
                                            idt          = idt,
                                            step_size    = kwargs['step_size'],
                                            objDSS       = self.dssObj,
                                            cktElement   = kwargs['cktElement'],
                                            error        = kwargs['error'],
                                            verbose      = kwargs['verbose']
                                           )      

        if (model == 'Phasor'): 
            self.instances[eid] = PhasorSim(
                                            cktTerminal  = kwargs['cktTerminal'], 
                                            cktPhase     = kwargs['cktPhase'],  
                                            idt          = idt,
                                            step_size    = kwargs['step_size'],
                                            objDSS       = self.dssObj,
                                            cktElement   = kwargs['cktElement'],
                                            error        = kwargs['error'],
                                            verbose      = kwargs['verbose']
                                           ) 
                
        if (model == 'Smartmeter'): 
            self.instances[eid] = SmartmeterSim(
                                            cktTerminal  = kwargs['cktTerminal'], 
                                            cktPhase     = kwargs['cktPhase'],  
                                            idt          = idt,
                                            step_size    = kwargs['step_size'],
                                            objDSS       = self.dssObj,
                                            cktElement   = kwargs['cktElement'],
                                            error        = kwargs['error'],
                                            verbose      = kwargs['verbose']
                                           ) 
          
        
        return [{'eid': eid, 'type': model}]


    def step(self, time, inputs):
        if (self.verbose > 0): print('simulator_pflow::step time =', time, ' inputs = ', inputs)
 
        next_step = time + 1
               
        #---
        #--- process inputs data
        #---       

        #--- Activate load generator
        if (0 == (time % self.loadgen_interval)):
            #-- get a new sample from loadgen
            # ePQ = self.objLoadGen.createLoads()
            ePQ = self.objLoadGen.readLoads()
            #-- execute processing of the the new elastic load
            self.dssObj.setLoads(ePQ)


        #--- use actuators to update opendss state with actions received by controllers (Mosaik)
        for eid, attrs in inputs.items():
            value_v = list(attrs['v'].values())[0]
            value_t = list(attrs['t'].values())[0]
            if (value_v != 'None' and value_v != None):
                if (self.verbose > 1): print('simulator_pflow::step Propagation delay =', time - value_t)
                self.instances[eid].setControl(value_v, time)
            
               
        #--- 
        #--- Update values from Probers, Phasor, SmartMeters
        #---                  
        for instance_eid in self.instances:
            self.instances[instance_eid].updateValues(time)                
         
        return next_step
 
 
    def get_data(self, outputs):
        if (self.verbose > 0): print('simulator_pflow::get_data INPUT', outputs)
        
        for instance_eid in self.instances:
            val_v, val_t = self.instances[instance_eid].getLastValue()
            self.data[instance_eid]['v']  = val_v
            self.data[instance_eid]['t']  = val_t         
  

        if (self.verbose > 0): print('simulator_pflow::get_data OUPUT data:', self.data)

        return self.data 
 
 
    def set_next(self, pflow, instance, parameters):
        if (self.verbose > 2): print('simulator_pflow::set_next', instance, parameters)
        
        if instance not in self.instances[pflow]:
            self.instances[pflow][instance] = parameters    

#     def finalize(self):
#         print('OpenDSS Final Results:')
#         self.dssObj.showIinout()       