'''
Created on Jul. 26, 2022
Mosaik interface for the controller simulator.
Only to be used with MOSAIK 3 and later versions

@file    simulator_controller_2.py
@author  Talha Ibn Aziz
@date    2022.07.26
@version 0.1
@company University of Alberta - Computing Science
'''

import queue
from tabnanny import verbose
import mosaik_api
import sys
import datetime

META = {
    'api-version': '3.0',
    'type': 'hybrid',
    'models': {
        'RangeControl': {
            'public': True,
            'params': ['eid', 'vset', 'bw', 'tdelay', 'control_delay', 'verbose'],
            'attrs': ['v', 't'],
            'trigger': ['v', 't'],
            'non-persistent': ['v', 't'],
        },      
    },
    'extra_methods': [
        'set_next'
    ],        
}

class ControlSim(mosaik_api.Simulator):
    '''
    Tap control agorithm based on paper:
    "Comparative Study of Tap Changer Control Algorithm for Distributed Networks with
    High Penetration of Renewables; Mariane Hartung, Eva-Maria Baerthlein, and Ara Panosyan;
    CIRED Workshop; Rome 11-12 June 2014" 
    '''
    def __init__(self):
        super().__init__(META)
        self.entities = {}
        self.data = {}
        self.instances = {}
        self.time = 0
        self.eventQueue = queue.PriorityQueue()
        
    def init(self, sid, time_resolution, verbose=0):
        self.sid = sid
        self.verbose = verbose
        self.total_exec_time = 0.0
        self.step_count = 0

        return self.meta

    
    def create(self, num, model, eid, vset, bw, tdelay, control_delay):
        if (self.verbose > 0): print('simulator_controller::create', num, model, ": ", eid)
        
        self.entities[eid] = {}
        self.entities[eid]['type'] = model
        self.entities[eid]['eid'] = eid
        self.entities[eid]['vset'] = vset
        self.entities[eid]['bw'] = bw
        self.entities[eid]['tdelay'] = tdelay
        self.entities[eid]['tlast'] = 0
        self.entities[eid]['vmax'] = vset
        self.entities[eid]['vmin'] = vset
        self.entities[eid]['control_delay'] = int(control_delay)


        self.data[eid] = {}     
        
        entities = []
        entities.append({'eid': eid, 'type': model})                
        sys.stdout.flush()
        return entities   
    
    
    def step(self, time, inputs, max_advance):
        start = datetime.datetime.now()
        self.step_count = self.step_count + 1
        if (self.verbose > 0): print('simulator_controller::step: ', time, ' Max Advance: ', max_advance)
        if (self.verbose > 1): print('simulator_controller::step INPUT: ', inputs)
        if (self.verbose > 3): print('simulator_controller::step DATA: ', self.data)
        
        self.time = time
        #---
        #--- prepare data to be used in get_data and calculate control action
        #---
        for controller_eid, attrs in inputs.items():
            #--- Save control data for processing in next step
            #--- List is used as multiple sensor data might be received
            self.data[controller_eid]['v'] = []
            self.data[controller_eid]['t'] = []

            vlist = list(attrs['v'].values())[0]
            tlist = list(attrs['t'].values())[0]
            
            #--- Handling multiple data simultaneously (if required)
            for i in range(0, len(vlist)):
                vmeas = vlist[i]
                tmeas = tlist[i]

                if (vmeas != None and vmeas != 'null' and vmeas != "None"):
                    #--- Calculate value_v
                    VAR_V = 0
                                    
                    delta_v = float(vmeas.rstrip()) - self.entities[controller_eid]['vset']
                    
                    #--- check if voltage on the range or out
                    if(abs(delta_v) < (self.entities[controller_eid]['bw']/2)):
                        #--- if in range reset the timer and do not send any control signal
                        self.entities[controller_eid]['tlast'] = tmeas
                        VAR_V = 0
                    
                    else:
                        #--- if the voltage is out of band
                        #--- check for how long the voltage
                        #--- count or not the propagation delay
                        if (self.verbose > 1):
                            print("simulator_controller::step Propagation Delay", time-tmeas)
                        
                        delta_t = tmeas - self.entities[controller_eid]['tlast']
                        #--- if the amount of time out of band is larger then allowed
                        if (delta_t > self.entities[controller_eid]['tdelay']):
                            #--- if the Vmeas is greater than set point, increase tap
                            if delta_v > 0:
                                VAR_V = -1
                            #--- if the Vmeas is smaller than set point, decrease tap
                            else:  
                                VAR_V = 1
                                
                    self.data[controller_eid]['v'].append(VAR_V)
                    
                    #--- time
                    self.data[controller_eid]['t'].append(time)


        #--- schedule control events to calculate LBTS
        for controller_eid in self.entities:
            if (time % self.entities[controller_eid]['control_delay'] == 0):
                self.eventQueue.put(time + self.entities[controller_eid]['control_delay'])

        while (not self.eventQueue.empty() and self.eventQueue.queue[0] == time):
            self.eventQueue.get()

        if (self.verbose > 3): print('simulator_controller::step after DATA: ', self.data)
        
        #--- if there is an event in the future, return next step time
        if not self.eventQueue.empty():
            if (self.verbose > 0):
                print ("simulator_controller::step next_step = ", self.eventQueue.queue[0])
            sys.stdout.flush()
	
            end = datetime.datetime.now()
            self.total_exec_time = self.total_exec_time + (end - start).total_seconds()
            return self.eventQueue.queue[0]
        
        sys.stdout.flush()
	
        end = datetime.datetime.now()
        self.total_exec_time = self.total_exec_time + (end - start).total_seconds()

    
    def get_data(self, outputs):
        start = datetime.datetime.now()
        if (self.verbose > 0): print('simulator_controller::get_data INPUT', outputs)      

        data = {}
        #--- Find data that is present and ready for delivery (now)
        for eid in self.data:
            if (self.data[eid] and self.data[eid]['t']):
                #--- check the latest updated control action (only one is generated)
                if (self.time % self.entities[eid]['control_delay'] == 0):
                    data[eid] = {}
                    data[eid]['t'] = []
                    data[eid]['v'] = []
                    #--- send current time + 1 to avoid NS3 roll back
                    data[eid]['t'].append(self.time + 1)
                    data[eid]['v'].append(self.data[eid]['v'][len(self.data[eid]['v'])-1])
                    #--- Need to clear as other controller instances might have input
                    #--- and this data might be returned again (although not required)
                    self.data[eid] = {}

        if (self.verbose > 1): print('simulator_controller::get_data OUTPUT data =', data)
        sys.stdout.flush()
	
        end = datetime.datetime.now()
        self.total_exec_time = self.total_exec_time + (end - start).total_seconds()
        return data


    def set_next(self, controller, instance, parameters):
        if (self.verbose > 2): print('simulator_controller::set_next', controller, instance, parameters)

        if instance not in self.instances[controller]:
            self.instances[controller][instance] = parameters


    def finalize(self):
        # print('Controller Params:')
        # for key in self.entities.keys():
        #     controller_name = "Control_" +  self.entities[key]['idt']
        #     print(controller_name, ": ", "Min =", self.entities[key]['min'], " -- Max =", self.entities[key]['max'])
            
        print("simulator_controller::finalize:total execution time = ", self.total_exec_time)
        print("simulator_controller::finalize:total steps = ", self.step_count)
        sys.stdout.flush()

    
