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
import queue
import sys


META = {
    'api-version': '3.0',
    'type': 'hybrid',
    'models': {
        'Sensor': {
            'public': True,
            'params': ['idt', 'step_size', 'verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
        },
        'Prober': {
            'public': True,
            'params': ['idt','cktTerminal','cktPhase','cktProperty','step_size','cktElement','error','verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
        },   
        'Phasor': {
            'public': True,
            'params': ['idt','cktTerminal','cktPhase','step_size','cktElement','error','verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
        },   
        'Smartmeter': {
            'public': True,
            'params': ['idt','cktTerminal','cktPhase','step_size','cktElement','error','verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
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
        self.step_size = step_size
    
    def updateValues(self, time):
        self.objProberSim.updateValues(time)
        if(0 == (time % self.step_size)):
            return (time + self.step_size)
        else:
            return -1
    
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
        self.step_size = step_size
    
    def updateValues(self, time):
        self.objPhasorSim.updateValues(time)
        if(0 == (time % self.step_size)):
            return (time + self.step_size)
        else:
            return -1
    
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
        self.step_size = step_size
    
    def updateValues(self, time):
        self.objSmartmeterSim.updateValues(time)
        if(0 == (time % self.step_size)):
            return (time + self.step_size)
        else:
            return -1
    
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
        self.next_steps = queue.PriorityQueue()
        self.loadgen_interval = 1
        self.prev_step = 0


    def init(self, sid, time_resolution, topofile, nwlfile, loadgen_interval, test, ilpqfile = "", verbose=0):	
        self.sid = sid       
        self.verbose = verbose
        self.loadgen_interval = loadgen_interval
        self.test = test
        
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
                                            step_size    = int(kwargs['step_size']),
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
                                            step_size    = int(kwargs['step_size']),
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
                                            step_size    = int(kwargs['step_size']),
                                            objDSS       = self.dssObj,
                                            cktElement   = kwargs['cktElement'],
                                            error        = kwargs['error'],
                                            verbose      = kwargs['verbose']
                                           ) 
          
        
        return [{'eid': eid, 'type': model}]


    def step(self, time, inputs, max_advance):
        if (self.verbose > 0): print('simulator_pflow::step time =', time, ' inputs = ', inputs)
               
        #---
        #--- process inputs data
        #---       

        #--- Activate load generator

        #--- Calculate how many times load generator
        #--- needs to be called
        for i in range(self.prev_step+1, time+1):
            if(i%self.loadgen_interval == 0):
                #-- get a new sample from loadgen
                # ePQ = self.objLoadGen.createLoads()
                if (self.verbose > 1): print("simulator_pflow::Generating Load for time: ", i)
                if(self.test):
                    ePQ = self.objLoadGen.readLoads(True)
                else:
                    ePQ = self.objLoadGen.readLoads(False)
                #-- execute processing of the the new elastic load
                self.dssObj.setLoads(ePQ)

        #--- use actuators to update opendss state with actions received by controllers (Mosaik)
        # for eid, attrs in inputs.items():
        #     value_v = list(attrs['v'].values())[0]
        #     value_t = list(attrs['t'].values())[0]
        #     if (value_v != 'None' and value_v != None):
        #         if (self.verbose > 1): print('simulator_pflow::step Propagation delay =', time - value_t)
        #         self.instances[eid].setControl(value_v, time)
            
               
        #--- 
        #--- Update values from Probers, Phasor, SmartMeters
        #---                  
        for instance_eid in self.instances:
            next_step = self.instances[instance_eid].updateValues(time)
            if(next_step != -1):
                self.next_steps.put(next_step)
        
        #--- Filter the next time steps and return the earliest next time step
        next_step = self.next_steps.get()
        while(not self.next_steps.empty() and next_step == self.next_steps.queue[0]):
            next_step = self.next_steps.get()

        self.prev_step = time
        if (self.verbose > 0):
            print("simulator_pflow::next step time: ", next_step)
        sys.stdout.flush()
        return next_step
 
 
    def get_data(self, outputs):
        if (self.verbose > 0): print('simulator_pflow::get_data INPUT', outputs)
        
        data = {}
        for instance_eid in self.instances:
            val_v, val_t = self.instances[instance_eid].getLastValue()
            self.data[instance_eid]['v']  = val_v
            self.data[instance_eid]['t']  = val_t         
            if (val_t != None):
                    data[instance_eid] = {}
                    data[instance_eid]['v'] = []
                    data[instance_eid]['t'] = []
                    data[instance_eid]['v'].append(self.data[instance_eid]['v'])
                    data[instance_eid]['t'].append(self.data[instance_eid]['t'])

        if (self.verbose > 0): print('simulator_pflow::get_data OUPUT data:', data)

        return data 
 
 
    def set_next(self, pflow, instance, parameters):
        if (self.verbose > 2): print('simulator_pflow::set_next', instance, parameters)
        
        if instance not in self.instances[pflow]:
            self.instances[pflow][instance] = parameters    

#     def finalize(self):
#         print('OpenDSS Final Results:')
#         self.dssObj.showIinout()       