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
import os
import sys
import csv
from SimDSS import SimDSS
from LoadGenerator import LoadGenerator
from CktDef import CKTTerm, CKTPhase
import numpy as np
import opendssdirect as dss
import math

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
        'Actuator': {
            'public': True,
            'params': ['idt', 'step_size', 'verbose'],
            'attrs': ['v', 't'],
            'trigger': ['v', 't'],
            'non-persistent': ['v', 't'],
        },
        'Prober': {
            'public': True,
            'params': ['idt', 'step_size', 'verbose'],
            'attrs': ['v', 't'],
            'non-persistent': ['v', 't'],
        },        
    },
    'extra_methods': [
        'set_next'
    ],    
}


class ProberSim:
    def __init__(self, idt, step_size, objDSS, action, element, terminal, phase, verbose):
        self.idt        = idt
        self.step_size  = step_size
        self.objDSS     = objDSS
        self.action     = action
        self.elem       = element
        self.term       = terminal
        self.ph         = phase
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None
        
    def updateValues(self, time):
        if (self.verbose > 0): print('ProberSim::updateValues', self.action, self.elem, self.term, self.ph)
        
        if (0 == time % self.step_size):
            if (self.action == "getV"):
                (VComp, _, _) =  self.objDSS.getCktElementState(self.elem, CKTTerm[self.term].value, CKTPhase[self.ph].value)
                val = self.R2P(VComp)[0] #-- only got the real part    
            if (self.action == "getTap"):
                val = self.objDSS.getTrafoTap(self.elem)
            if (self.action == "getVPu"):
                (val, _) =  self.objDSS.getVMagAnglePu(self.elem, CKTPhase[self.ph].value)
            if (self.action == "getLoad"):
                (val, _) = self.objDSS.getPQ(self.elem)       
            if (self.action == "getS"):
                val = self.objDSS.getS(self.elem, CKTTerm[self.term].value, CKTPhase[self.ph].value)          
            
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
    def __init__(self, idt, step_size, objDSS, action, element, terminal, phase, verbose):
        self.idt        = idt
        self.step_size  = step_size
        self.objDSS     = objDSS
        self.action     = action
        self.elem       = element
        self.term       = terminal
        self.ph         = phase
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None
        self.time_diff_resolution = 1e-9
        
        
    def updateValues(self, time):
        if (self.verbose > 0): print('SensorSim::getValue', self.action, self.elem, self.term, self.ph)
        
        if (0 == time % self.step_size):
            if (self.action == "getV"):
                (VComp, _, _) =  self.objDSS.getCktElementState(self.elem, CKTTerm[self.term].value, CKTPhase[self.ph].value)
                val = self.R2P(VComp)[0] #-- only got the real part
            if (self.action == "getTap"):
                val = self.objDSS.getTrafoTap(self.elem)
            self.priorTime  = time + self.time_diff_resolution
            self.priorValue = val
        else:
            self.priorTime  = None
            self.priorValue = None          
            
        if (self.verbose > 0): print('SensorSim::getValue Time = ', self.priorTime, 'Value = ', self.priorValue)
        if (self.verbose > 2): print('SensorSim[', self.idt, ']::getValue v =', val)        


    def getLastValue(self):
        return self.priorValue, self.priorTime

    
    def R2P(self, x):
        return np.abs(x), np.angle(x)



class ActuatorSim:
    def __init__(self, idt, step_size, objDSS, action, element, terminal, phase, verbose):
        self.idt        = idt
        self.step_size  = step_size
        self.objDSS     = objDSS
        self.action     = action
        self.elem       = element
        self.term       = terminal
        self.ph         = phase
        self.verbose    = verbose
        self.priorValue = None
        self.priorTime  = None

        
    def setControl(self, value, time):
        if (self.verbose > 0): print('ActuatorSim::setControl', self.action, self.elem, self.term, self.ph, value)
        
        if (value != 0 and value != None):
            if (self.action == "ctlS"):
                self.objDSS.operateSwitch(int(value), self.elem, CKTTerm[self.term].value, CKTPhase[self.ph].value)
            if (self.action == "setTap"):
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
        self.actives = {}
        self.entities = {}
        self.next = {}
        self.instances = {}
        self.step_size = 1
        self.loadgen_interval = self.step_size


    def init(self, sid, time_resolution, topofile, nwlfile, ilpqfile, actsfile, step_size, loadgen_interval, verbose=0):	
        self.sid = sid       
        self.verbose = verbose
        self.loadgen_interval = loadgen_interval
        self.step_size = step_size
        
        self.swpos = 0
        self.swcycle = 35
        
        if (self.verbose > 0): print('simulator_pflow::init', self.sid)
        if (self.verbose > 1): print('simulator_pflow::init', topofile, nwlfile, ilpqfile, actsfile, verbose)

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
        self.objLoadGen = LoadGenerator(nwlfile,
                                        PFLimInf   =  0.95,
                                        PFLimSup   =  0.99,
                                        LoadLimInf = -1.65,
                                        LoadLimSup =  0.70,
                                        AmpGain    =  0.30,
                                        #Freq       =  1./8640,
                                        Freq       =  1./100,
                                        PhaseShift = math.pi)
        
        #--- read acts file
        self.readActives(actsfile)
    
        sys.stdout.flush()
        return self.meta


    def create(self, num, model, idt, step_size, verbose):
        if (self.verbose > 0): print('simulator_pflow::create ', model, idt)

        eid = '%s_%s' % (model, idt)
        self.data[eid] = {}     
        self.instances[eid] = {}

        if (model == 'Prober'):
            self.instances[eid] = ProberSim(idt,
                                           step_size = step_size, 
                                           objDSS    = self.dssObj, 
                                           action    = self.actives[eid]['action'], 
                                           element   = self.actives[eid]['CKTElement'], 
                                           terminal  = self.actives[eid]['CKTTerminal'], 
                                           phase     = self.actives[eid]['CKTPhase'],
                                           verbose   = verbose)

        if (model == 'Sensor'):
            self.instances[eid] = SensorSim(idt,
                                           step_size = step_size, 
                                           objDSS    = self.dssObj, 
                                           action    = self.actives[eid]['action'], 
                                           element   = self.actives[eid]['CKTElement'], 
                                           terminal  = self.actives[eid]['CKTTerminal'], 
                                           phase     = self.actives[eid]['CKTPhase'],
                                           verbose   = verbose)
            
        if (model == 'Actuator'):
            self.instances[eid] = ActuatorSim(idt, 
                                           step_size = step_size,
                                           objDSS   = self.dssObj, 
                                           action   = self.actives[eid]['action'], 
                                           element  = self.actives[eid]['CKTElement'], 
                                           terminal = self.actives[eid]['CKTTerminal'], 
                                           phase    = self.actives[eid]['CKTPhase'],
                                           verbose  = verbose)            
        
        sys.stdout.flush()
        return [{'eid': eid, 'type': model}]


    def step(self, time, inputs, max_advance):
        if (self.verbose > 0): print('simulator_pflow::step time = ', time, ' Max Advance = ', max_advance)
        if (self.verbose > 1): print('simulator_pflow::step inputs = ', inputs)
 
        self.time = time
        #--- Based on Sensor data interval, LoadGen called accordingly
        next_step = time + self.step_size

        # If this is an event-based step or duplicate step, only perform Actuation
        # As this is a priority simulator, input only comes after the step is performed
        if (time % self.step_size == 0):
               
            #---
            #--- process inputs data
            #--- 

            #--- Calculate how many times load generator
            #--- needs to be called
            prev_step = time - self.step_size
            if  (prev_step < 0):
                loadGen_cnt = 1
                prev_step = -1
            else:   loadGen_cnt = math.floor(time/self.loadgen_interval) \
                    - math.floor(prev_step/self.loadgen_interval)

            #--- Activate load generator
            for i in range(0, loadGen_cnt):
                if (self.verbose > 1): print("Generating load for: ", \
                    self.loadgen_interval * ( math.ceil( (prev_step+1)/self.loadgen_interval ) + i))
                #-- get a new sample from loadgen
                ePQ = self.objLoadGen.createLoads()
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
            if(instance_eid.find("Sensor") > -1)  :
                self.instances[instance_eid].updateValues(time)
        
        #--- 
        #--- get new set of prober data from OpenDSS
        #---   
        for instance_eid in self.instances:
            if(instance_eid.find("Prober") > -1)  :
                self.instances[instance_eid].updateValues(time)        
         
        sys.stdout.flush()
        if (time % self.step_size == 0):
            return next_step
 
 
    def get_data(self, outputs):
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
            # All other models provide data at fixed intervals
            elif (self.time % self.step_size == 0):
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
        return data 
 
 
    def set_next(self, pflow, instance, parameters):
        if (self.verbose > 2): print('simulator_pflow::set_next', instance, parameters)
        
        if instance not in self.instances[pflow]:
            self.instances[pflow][instance] = parameters    

#     def finalize(self):
#         print('OpenDSS Final Results:')
#         self.dssObj.showIinout()       
 
 
    def readActives(self, actsfile):

        current_directory = os.path.dirname(os.path.realpath(__file__))
        pathToFile = os.path.abspath(
            os.path.join(current_directory, actsfile)
        )
        if not os.path.isfile(pathToFile):
            print('File Actives does not exist: ' + pathToFile)
            sys.exit()
        else:
            with open(pathToFile, 'r') as csvFile:
                csvobj = csv.reader(csvFile)
                for rows in csvobj:
                    eid = rows[0]
                    self.actives[eid] = {}
                    self.actives[eid]['action']      = rows[1]
                    self.actives[eid]['CKTElement']  = rows[2]
                    self.actives[eid]['CKTTerminal'] = rows[3]
                    self.actives[eid]['CKTPhase']    = rows[4]  
                
                if (self.verbose > 1):
                    print ('simulator_pflow::readActives:')
                    for key in self.actives:                
                        print(key, self.actives[key])  

