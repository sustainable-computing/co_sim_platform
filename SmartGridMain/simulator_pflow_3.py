'''
Created on Jul. 26, 2022
OpenDSS Mosaik interface, and Sensor/Actuator Models
Works only with MOSAIK 3 and later versions

@file    simulator_pflow_3.py
@author  Talha Ibn Aziz
@date    2022.07.26  
@version 0.1
@company University of Alberta - Computing Science
'''

import queue
import random
import mosaik_api_v3 as mosaik_api
import os
import sys
import csv
from SimDSS import SimDSS
from LoadGenerator import LoadGenerator
from CktDef import CKTTerm, CKTPhase
import numpy as np
import opendssdirect as dss
import math
import datetime

META = {
    'api-version': '3.0',
    'type': 'hybrid',
    'models': {
        'Sensor': {
            'public': True,
            'params': ['eid', 'cktTerminal', 'cktPhase', 'cktProperty', 'step_size', 'cktElement', 'error', 'verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
        },
        'Actuator': {
            'public': True,
            'params': ['eid', 'cktTerminal', 'cktPhase', 'cktProperty', 'step_size', 'cktElement', 'error', 'verbose'],
            'attrs': ['v', 't'],
            'trigger': ['v', 't'],
            'non-persistent': ['v', 't'],
        },
        'Prober': {
            'public': True,
            'params': ['eid', 'cktTerminal', 'cktPhase', 'cktProperty', 'step_size', 'cktElement', 'error', 'verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
        },
        'Phasor': {
            'public': True,
            'params': ['eid', 'cktTerminal', 'cktPhase', 'cktProperty', 'step_size', 'cktElement', 'error', 'verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
        },   
        'Smartmeter': {
            'public': True,
            'params': ['eid', 'cktTerminal', 'cktPhase', 'cktProperty', 'step_size', 'cktElement', 'error', 'verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
        },    
    },
    'extra_methods': [
        'set_next'
    ],    
}

class PhasorSim:
    def __init__(self,
             sid,
             cktTerminal,
             cktPhase,
             step_size, 
             objDSS,  
             cktElement, 
             error, 
             verbose):
        self.idt        = sid
        self.objDSS     = objDSS
        self.cktElement = cktElement
        self.cktTerminal = cktTerminal
        self.cktPhase   = cktPhase
        self.error      = float(error)
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None
        self.time_diff_resolution = 1e-9
        self.randomTime = random.randint(0, 1)
        self.step_size = int(step_size)
    
    def updateValues(self, time):
        if (self.verbose > 2): print(self.idt,'::updateValues', 
                                     self.cktElement, self.cktTerminal, self.cktPhase)

        if(0 == (time % self.step_size)):
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
            if (self.verbose > 0): print('Phasor::updateValues Time = ', self.priorTime, 'Value = ', self.priorValue)
            if (self.verbose > 2): print('Phasor[', self.idt, ']::updateValues v =', val) 

            return (time + self.step_size)
        else:
            self.priorTime  = None
            self.priorValue = None
            if (self.verbose > 2): print('Phasor[', self.idt, ']::updateValues v =', val) 

            return -1

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


class SmartmeterSim:
    def __init__(self,
             sid,
             cktTerminal,
             cktPhase,
             step_size, 
             objDSS,  
             cktElement, 
             error, 
             verbose):
        self.idt        = sid
        self.objDSS     = objDSS
        self.cktElement = cktElement
        self.cktTerminal = cktTerminal
        self.cktPhase   = cktPhase
        self.error      = float(error)
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None
        self.time_diff_resolution = 1e-9
        self.randomTime = random.randint(0, 1)
        self.step_size = int(step_size)
    
    def updateValues(self, time):
        if(0 == (time % self.step_size)):
            if (self.verbose > 2): print('Smartmeter::updateValues', 
                                    self.cktElement, self.cktTerminal, self.cktPhase)
        
        # if (0 == time % (self.step_size + self.randomTime)):
        # for now assume that there is no randomTime
        if (0 == time % (self.step_size)):
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
            if (self.verbose > 0): print('Smartmeter::updateValues Time = ', self.priorTime, 'Value = ', self.priorValue)
            if (self.verbose > 2): print('Smartmeter[', self.idt, ']::updateValues v =', val)
        
            return (time + self.step_size)
        else:
            self.priorTime  = None
            self.priorValue = None 
            if (self.verbose > 2): print('Smartmeter[', self.idt, ']::updateValues v =', val)
        
            return -1 

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


class ProberSim:
    def __init__(self, eid, step_size, objDSS, element, terminal, phase, verbose):
        self.idt        = eid
        self.step_size  = int(step_size)
        self.objDSS     = objDSS
        # self.action     = action
        self.elem       = element
        self.term       = terminal
        self.ph         = phase
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None
        
    def updateValues(self, time):
        if (self.verbose > 0): print('ProberSim::updateValues', self.idt, self.elem, self.term, self.ph)
        
        if (0 == time % self.step_size):
            # No more action variable, use cidx and didx to determine
            eid = self.idt
            eid = eid.split('.')
            cidx = eid[1]
            didx = eid[2]
            # 0 = voltage, 1 = tap, 2 = load, 3 = voltage phase angle
            if (cidx == '0'):
                (VComp, _, _) =  self.objDSS.getCktElementState(self.elem, CKTTerm[self.term].value, CKTPhase[self.ph].value)
                val = self.R2P(VComp)[0] #-- only got the real part    
            if (cidx == '1'):
                val = self.objDSS.getTrafoTap(self.elem)
            if (cidx == '3'):
                (val, _) =  self.objDSS.getVMagAnglePu(self.elem, CKTPhase[self.ph].value)
            if (cidx == '2'):
                (val, _) = self.objDSS.getPQ(self.elem)       
            # if (self.action == "getS"):
            #     val = self.objDSS.getS(self.elem, CKTTerm[self.term].value, CKTPhase[self.ph].value)          
            
            self.priorTime  = time
            self.priorValue = val
        else:
            self.priorTime  = None
            self.priorValue = None          
            
        if (self.verbose > 0): print('ProberSim::updateValues Time = ', self.priorTime, 'Value = ', self.priorValue)
        if (self.verbose > 2): print('ProberSim[', self.idt, ']::updateValues v =', val)   
    
    def getLastValue(self):
        return self.priorValue, self.priorTime
     
    def R2P(self, x):
        return np.abs(x), np.angle(x)



class SensorSim:
    def __init__(self, eid, step_size, objDSS, element, terminal, phase, verbose):
        self.idt        = eid
        self.step_size  = int(step_size)
        self.objDSS     = objDSS
        # self.action     = action
        self.elem       = element
        self.term       = terminal
        self.ph         = phase
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None
        self.time_diff_resolution = 1e-9
        
        
    def updateValues(self, time):
        if (self.verbose > 0): print('SensorSim::getValue', self.elem, self.term, self.ph)
        
        if (0 == time % self.step_size):
            # no action choice - default action is get voltage value
            # if (self.action == "getV"):
            (VComp, _, _) =  self.objDSS.getCktElementState(self.elem, CKTTerm[self.term].value, CKTPhase[self.ph].value)
            val = self.R2P(VComp)[0] #-- only got the real part
            # if (self.action == "getTap"):
            #     val = self.objDSS.getTrafoTap(self.elem)
            self.priorTime  = time + self.time_diff_resolution
            self.priorValue = val
            if (self.verbose > 0): print('SensorSim::getValue Time = ', self.priorTime, 'Value = ', self.priorValue)
            if (self.verbose > 1): print('SensorSim::getValue Next step = ', time + self.step_size)
            if (self.verbose > 2): print('SensorSim[', self.idt, ']::getValue v =', val)        

            return (time + self.step_size)
        else:
            self.priorTime  = None
            self.priorValue = None
            if (self.verbose > 0): print('SensorSim::getValue Time = ', self.priorTime, 'Value = ', self.priorValue)
            if (self.verbose > 2): print('SensorSim[', self.idt, ']::getValue v =', val)        

            return -1
            
        

    def getLastValue(self):
        return self.priorValue, self.priorTime

    
    def R2P(self, x):
        return np.abs(x), np.angle(x)



class ActuatorSim:
    def __init__(self, eid, step_size, objDSS, element, terminal, phase, verbose):
        self.eid        = eid
        self.step_size  = int(step_size)
        self.objDSS     = objDSS
        # self.action     = action
        self.elem       = element
        self.term       = terminal
        self.ph         = phase
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None

        
    def setControl(self, value, time):
        if (self.verbose > 0): print('ActuatorSim::setControl', self.action, self.elem, self.term, self.ph, value)
        
        if (value != 0 and value != None):
            # No more action choices - default action is set tap
            # if (self.action == "ctlS"):
            #     self.objDSS.operateSwitch(int(value), self.elem, CKTTerm[self.term].value, CKTPhase[self.ph].value)
            # if (self.action == "setTap"):
            self.objDSS.setTrafoTap(self.elem, tapOrientation=value, tapUnits=1)                
             
        self.priorTime  = time
        self.priorValue = value

        if (self.verbose > 2): print('ActuatorSim[', self.idt, ']::setControl c =', value, 'time = ', time)        


    def getLastValue(self):
        if (self.verbose > 0): print('ActuatorSim::getLastValue', self.priorValue, self.priorTime)
        value =  self.priorValue
        time = self.priorTime
        #--- reset value after to has been extract by another simulator
        #--- it will not send the same value twice
        self.priorValue = None
        self.priorTime = None
        
        return value, time



class PFlowSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.data = {}
        self.next_step = 0
        self.instances = {}
        self.loadgen_interval = 1
        self.time = -1
        self.next_steps = queue.PriorityQueue()


    def init(self, sid, time_resolution, topofile, nwlfile, loadgen_interval, ilpqfile="", verbose=0):	
        self.sid = sid       
        self.verbose = verbose
        self.loadgen_interval = loadgen_interval
        
        self.swpos = 0
        self.swcycle = 35
        self.total_exec_time = 0.0
        self.step_count = 0
        
        if (self.verbose > 0): print('simulator_pflow::init', self.sid)
        if (self.verbose > 1): print('simulator_pflow::init', topofile, nwlfile, ilpqfile, verbose)

        #--- start opendss
        self.dssObj = SimDSS(topofile, nwlfile, ilpqfile)
        if (self.verbose > 2):
            self.dssObj.showLoads()
            self.dssObj.showVNodes()
            self.dssObj.showIinout()
            self.dssObj.showVMagAnglePu()
            dss.run_command("Show Buses")
            dss.run_command("Show Voltages LN nodes")
            dss.run_command("Show Taps")
            
        #--- create instance of LoadGenerator
        #--- IEEE13
        self.objLoadGen = LoadGenerator(nwlfile,
                                        PFLimInf   =  0.95,
                                        PFLimSup   =  0.99,
                                        LoadLimInf = -1.65,
                                        LoadLimSup =  0.70,
                                        AmpGain    =  0.30,
                                        # Freq       =  1./8640,
                                        Freq       =  1./100,
                                        PhaseShift = math.pi)
        
        #--- IEEE33
        # self.objLoadGen = LoadGenerator(nwlfile,
        #                                 PFLimInf   =  0.95,
        #                                 PFLimSup   =  0.95,
        #                                 LoadLimInf =  0.4,
        #                                 LoadLimSup =  0.9,
        #                                 AmpGain    =  0.25,
        #                                 Freq       =  1./1250,
        #                                 PhaseShift = math.pi)
    
        sys.stdout.flush()
        return self.meta

    def create(self, num, model, cktTerminal, cktPhase, eid, step_size, cktElement, error, verbose):
        if (self.verbose > 0): print('simulator_pflow::create ', model, ": ", eid)

        self.data[eid] = {}     
        self.instances[eid] = {}

        if (model == 'Phasor'): 
            self.instances[eid] = PhasorSim(eid,
                                            cktTerminal  = cktTerminal, 
                                            cktPhase     = cktPhase,
                                            step_size    = step_size,
                                            objDSS       = self.dssObj,
                                            cktElement   = cktElement,
                                            error        = error,
                                            verbose      = verbose
                                           ) 
                
        if (model == 'Smartmeter'): 
            self.instances[eid] = SmartmeterSim(eid,
                                            cktTerminal  = cktTerminal, 
                                            cktPhase     = cktPhase,
                                            step_size    = step_size,
                                            objDSS       = self.dssObj,
                                            cktElement   = cktElement,
                                            error        = error,
                                            verbose      = verbose
                                           )

        if (model == 'Prober'):
            self.instances[eid] = ProberSim(eid,
                                        step_size = step_size, 
                                        objDSS    = self.dssObj,
                                        element   = cktElement, 
                                        terminal  = cktTerminal, 
                                        phase     = cktPhase,
                                        verbose   = verbose)

        if (model == 'Sensor'):
            self.instances[eid] = SensorSim(eid,
                                        step_size = step_size, 
                                        objDSS    = self.dssObj,
                                        element   = cktElement, 
                                        terminal  = cktTerminal, 
                                        phase     = cktPhase,
                                        verbose   = verbose)
            
        if (model == 'Actuator'):
            self.instances[eid] = ActuatorSim(eid, 
                                        step_size = step_size,
                                        objDSS    = self.dssObj,
                                        element   = cktElement, 
                                        terminal  = cktTerminal, 
                                        phase     = cktPhase,
                                        verbose   = verbose)            
        
        sys.stdout.flush()
        return [{'eid': eid, 'type': model}]

    def step(self, time, inputs, max_advance):
        start = datetime.datetime.now()
        self.step_count = self.step_count + 1
        if (self.verbose > 0): print('simulator_pflow::step time = ', time, ' Max Advance = ', max_advance)
        if (self.verbose > 1): print('simulator_pflow::step inputs = ', inputs)

        self.prev_step = self.time
        self.time = time
        #--- Based on Sensor data interval, LoadGen called accordingly

        #--- Actuation data may arrive at the same time step as Sensor data
        #--- generation and thus trigger the same time step multipe times.
        #--- Avoid duplicate processing of load data.
        if (time != self.prev_step):
            #---
            #--- process inputs data
            #--- 

            #--- Calculate how many times load generator
            #--- needs to be called
            if  (self.prev_step < 0):
                loadGen_cnt = 1
            else:   loadGen_cnt = math.floor(time/self.loadgen_interval) \
                    - math.floor(self.prev_step/self.loadgen_interval)

            #--- Activate load generator
            for i in range(0, loadGen_cnt):
                if (self.verbose > 1): print("Generating load for: ", \
                    self.loadgen_interval * ( math.ceil( (self.prev_step+1)/self.loadgen_interval ) + i))
                #-- get a new sample from loadgen

                #-- IEEE13 Generate new randomized loads
                ePQ = self.objLoadGen.createLoads()

                #-- IEEE33 Get loads for standard FULL dataset
                # ePQ = self.objLoadGen.readLoads(False)

                #-- IEEE33 Get loads for standard TEST dataset
                # ePQ = self.objLoadGen.readLoads(True)

                #-- execute processing of the the new elastic load
                self.dssObj.setLoads(ePQ)

        #--- Create step load on Bus 611
#         if (time > 50 and time < 350):
#             dss.run_command("New Load.611.3 Bus1=611.3  kW=206.4   kvar=96")   # 20%
#             self.dssObj._updateSystemState()      
#         else:
#             dss.run_command("New Load.611.3 Bus1=611.3  kW=170   kvar=80") 
#             self.dssObj._updateSystemState()           



        #--- Attack at the switch
#         period = 90000 # half of the t_delay
#         xx = 0 if (np.abs(np.sin(2 * np.pi * (1./period)*time + 3/4*np.pi)) > 0.97) else 1 
#          
#         if (0 == xx):
#             #--- switch off
#             self.dssObj.operateSwitch(0, "Line.671692", (CKTTerm.SNDBUS).value, (CKTPhase.PHASE_ALL).value)
#         else: 
#             #-- switch on
#             self.dssObj.operateSwitch(1, "Line.671692", (CKTTerm.SNDBUS).value, (CKTPhase.PHASE_ALL).value)


        #--- Switch on PVSystem
#         if (time > 200 and time < 400):
#             dss.run_command("New XYCurve.MyPVsT_680 npts=4 xarray=[19.044 22.106 29.697 25.297] yarray=[0 0.781 0.966 0.030]")
#             dss.run_command("New PVSystem.PV_680 phases=3 bus1=680 kV=4.16 conn=wye kVA=800  irrad=1.016  Pmpp=523.589 temperature=29.049 PF=1 P-TCurve=MyPVsT_680")
#             self.dssObj._updateSystemState()      
#         else:
#             dss.run_command("New PVSystem.PV_680 phases=3 bus1=680 kV=4.16 conn=wye kVA=0") 
#             self.dssObj._updateSystemState()            
    


        #--- Use actuators to update opendss state with actions received by controllers (Mosaik)
        for eid, attrs in inputs.items():
            vlist = list(attrs['v'].values())[0]
            tlist = list(attrs['t'].values())[0]
            for i in range(0, len(vlist)):
                value_v = vlist[i]
                value_t = tlist[i]
                if (value_v != 'None' and value_v != None):
                    if (self.verbose > 1): print('simulator_pflow::step Propagation delay =', time - value_t)
                    self.instances[eid].setControl(value_v, time)
            
        #--- 
        #--- get new set of sensor data from OpenDSS
        #---   
        for instance_eid in self.instances:
            if (instance_eid.find("Sensor") > -1) or \
                (instance_eid.find("Phasor") > -1) or \
                (instance_eid.find("SmartMeter") > -1):
                self.next_step = self.instances[instance_eid].updateValues(time)
                if self.next_step != -1:
                    self.next_steps.put(self.next_step)

        #--- 
        #--- get new set of prober data from OpenDSS
        #---   
        for instance_eid in self.instances:
            if instance_eid.find("Prober") > -1:
                self.instances[instance_eid].updateValues(time)
                    

        #--- Filter the next time steps and return the earliest next time step
        self.next_step = self.next_steps.queue[0]
        #--- For a time-based simulator, there is always a next step
        while(self.time >= self.next_steps.queue[0]):
            self.next_step = self.next_steps.get()
        self.next_step = self.next_steps.queue[0]

        if(self.verbose > 1):
            print('simulator_pflow::step next_step = ', self.next_step)
        sys.stdout.flush()
	
        end = datetime.datetime.now()
        self.total_exec_time = self.total_exec_time + (end - start).total_seconds()
        return self.next_step


    def get_data(self, outputs):
        start = datetime.datetime.now()
        if (self.verbose > 0): print('simulator_pflow::get_data INPUT', outputs)
        
        data = {}
        for instance_eid in self.instances:
            # Acuators provide data only when there is actuation
            if (instance_eid.find("Actuator") > -1):
                val_v, val_t = self.instances[instance_eid].getLastValue()
                self.data[instance_eid]['v'] = val_v
                self.data[instance_eid]['t'] = val_t
                if (val_t != None):
                    data[instance_eid] = {}
                    data[instance_eid]['v'] = []
                    data[instance_eid]['t'] = []
                    data[instance_eid]['v'].append(self.data[instance_eid]['v'])
                    data[instance_eid]['t'].append(self.data[instance_eid]['t'])
            # All other models provide data at their own fixed intervals
            elif (self.time % self.instances[instance_eid].step_size == 0):
                val_v, val_t = self.instances[instance_eid].getLastValue()
                self.data[instance_eid]['v'] = val_v
                self.data[instance_eid]['t'] = val_t
                data[instance_eid] = {}
                data[instance_eid]['v'] = []
                data[instance_eid]['t'] = []
                data[instance_eid]['v'].append(self.data[instance_eid]['v'])
                data[instance_eid]['t'].append(self.data[instance_eid]['t'])

        if (self.verbose > 1): print('simulator_pflow::get_data data:', data)

        sys.stdout.flush()
	
        end = datetime.datetime.now()
        self.total_exec_time = self.total_exec_time + (end - start).total_seconds()
        return data 

    def set_next(self, pflow, instance, parameters):
        if (self.verbose > 2): print('simulator_pflow::set_next', instance, parameters)
        
        if instance not in self.instances[pflow]:
            self.instances[pflow][instance] = parameters    

    def finalize(self):
        # print('OpenDSS Final Results:')
        # self.dssObj.showIinout()
        print("simulator_pflow::finalize:total execution time = ", self.total_exec_time)
        print("simulator_pflow::finalize:total steps = ", self.step_count)
        sys.stdout.flush()

