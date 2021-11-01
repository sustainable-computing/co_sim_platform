'''
Created on Jun. 01, 2019
Mosaik interface for the controller simulator.

@file    simulator_controller.py
@author  Evandro de Souza
@date    2019.09.05  
@version 0.3
@company University of Alberta - Computing Science
'''

import mosaik_api


META = {
    'api_version': '3.0',
    'type': 'event-based',
    'models': {
        'RangeControl': {
            'public': True,
            'params': ['idt', 'vset', 'bw', 'tdelay', 'verbose'],
            'attrs': ['v', 't'],           
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

        
    def init(self, sid, time_resolution, eid_prefix=None, control_delay=1, verbose=0):
        if eid_prefix is not None:
            self.eid_prefix = eid_prefix
        self.sid = sid
        #-- The time required to take a control decision
        #-- by default it is the minimum unit = 1 step
        self.control_delay = control_delay
        self.verbose = verbose
        
        return self.meta

    
    def create(self, num, model, idt, vset, bw, tdelay):
        if (self.verbose > 0): print('simulator_controller::create', num, model, idt)
        
        eid = '%s%s' % (self.eid_prefix, idt)
        
        self.entities[eid] = {}
        self.entities[eid]['type'] = model
        self.entities[eid]['idt'] = idt
        self.entities[eid]['vset'] = vset
        self.entities[eid]['bw'] = bw
        self.entities[eid]['tdelay'] = tdelay
        self.entities[eid]['tlast'] = 0
        self.entities[eid]['vmax'] = vset
        self.entities[eid]['vmin'] = vset


        self.data[eid] = {}     
        
        entities = []
        entities.append({'eid': eid, 'type': model})                

        return entities   
    

    def step(self, time, inputs, max_advance):
        if (self.verbose > 0): print('simulator_controller::step: ', time, ' Max Advance: ', max_advance)
        if (self.verbose > 1): print('simulator_controller::step INPUT: ', inputs)

        #--- If there is a tap command to propagate, need to force step
        next_step = time
        self.time = time
        
        #---
        #--- prepare data to be used in get_data and calculate control action
        #---
        for controller_eid, attrs in inputs.items():
            self.data[controller_eid] = {}
            vmeas = list(attrs['v'].values())[0]
            tmeas = list(attrs['t'].values())[0]

            if (vmeas != None and vmeas != 'null' and vmeas != "None"):
                #--- Calculate value_v
                VAR_V = 0
                
                delta_v = vmeas - self.entities[controller_eid]['vset']
                
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
                        #--- if the Vmeas is greatar than set point, increase tap
                        if delta_v > 0:
                            VAR_V = -1
                        #--- if the Vmeas is smaller than set point, decrease tap
                        else:  
                            VAR_V = 1
                            
                self.data[controller_eid]['v'] = VAR_V
            else:
                self.data[controller_eid]['v'] = None               
            
            #--- time              
            if (tmeas != None and tmeas != 'null' and tmeas != "None"):                     
                self.data[controller_eid]['t'] = time
                next_step = time + 1
            else:
                self.data[controller_eid]['t'] = None            
          
        if(next_step > time):  return next_step
    
    
    def get_data(self, outputs):
        if (self.verbose > 0): print('simulator_controller::get_data INPUT', outputs)

        data = {}
        for eid in self.data:
            if(self.data[eid]['t'] and self.data[eid]['t'] != None):
                time = self.data[eid]['t']
                if(self.time >= time + self.control_delay):
                    data[eid] = self.data[eid]

        if (self.verbose > 1): print('simulator_controller::get_data OUTPUT data =', data)
        return data


    def set_next(self, controller, instance, parameters):
        if (self.verbose > 2): print('simulator_controller::set_next', controller, instance, parameters)

        if instance not in self.instances[controller]:
            self.instances[controller][instance] = parameters


#     def finalize(self):
#         print('Controller Params:')
#         for key in self.entities.keys():
#             controller_name = "Control_" +  self.entities[key]['idt']
#             print(controller_name, ": ", "Min =", self.entities[key]['min'], " -- Max =", self.entities[key]['max'])
            

    
