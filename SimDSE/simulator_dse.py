'''
Created on Nov. 11, 2019
Mosaik interface for the Distribution State Estimation.

@file    simulator_dse.py
@author  Evandro de Souza
@date    2019.11.11  
@version 0.1
@company University of Alberta - Computing Science
'''

import mosaik_api
import numpy as np
import pandas as pd
import os
import sys
import csv
from ast import literal_eval

META = {
    'models': {
        'Estimator': {
            'public': True,
            'params': ['idt', 'ymat_file', 'devs_file', 'acc_period', 'max_iter', 'threshold', 'baseS', 'baseV', 'baseNode', 'basePF', 'verbose'],
            'attrs': ['v', 't'],           
        },      
    },       
}

class DSESim(mosaik_api.Simulator):

    def __init__(self):
        super().__init__(META)
        self.entities = {}
        self.next = {}
        self.instances = {}
        self.devParams = {}
        self.data = {}
        
        
    def init(self, sid, eid_prefix=None, step_size=1, verbose=0):
        if eid_prefix is not None:
            self.eid_prefix = eid_prefix
        self.sid       = sid
        self.step_size = step_size
        self.verbose   = verbose
        self.cktState  = {}
        self.MsgCount  = 0
        
        return self.meta
  
    
    def create(self, num, model, idt, ymat_file, devs_file, acc_period, max_iter, threshold, baseS, baseV, baseNode, basePF):
        if (self.verbose > 0): print('simulator_dse::create', num, model, idt)
        
        eid = '%s%s' % (self.eid_prefix, idt)
        
        self.entities[eid] = {}
        self.entities[eid]['ymat_file']  = ymat_file
        self.entities[eid]['devs_file']  = devs_file
        self.entities[eid]['acc_period'] = acc_period
        self.entities[eid]['max_iter']   = max_iter
        self.entities[eid]['threshold']  = threshold
        self.entities[eid]['type']       = model
        self.entities[eid]['baseS']      = baseS       
        self.entities[eid]['baseV']      = baseV
        self.entities[eid]['baseI']      = baseS/baseV
        self.entities[eid]['baseY']      = baseS/np.power(baseV,2)
        self.entities[eid]['baseNode']   = baseNode     
        self.entities[eid]['basePF']     = basePF
        self.entities[eid]['vecZ']       = {}
        self.entities[eid]['nodes']      = 0
        self.entities[eid]['df_devs']    = pd.DataFrame({})


        ''' read ymat_file and get number of nodes '''
        self.entities[eid]['ymat_data'] = np.load(ymat_file)
        self.entities[eid]['nodes'] = len(self.entities[eid]['ymat_data'])
        self.entities[eid]['ymat_data'] = self.entities[eid]['ymat_data'] / self.entities[eid]['baseY']
        if (self.verbose > 0): print('DSESim::create Nodes YMat:', self.entities[eid]['nodes'])
        

        ''' get device list '''
        self.entities[eid]['df_devs'] = pd.read_csv(devs_file, delimiter = ',', index_col = 'idn')      
        self.entities[eid]['df_devs']= pd.concat([self.entities[eid]['df_devs'], pd.DataFrame({'SPA':[],    # true power phase A
                                                                                               'SQA':[],    # reactive power phase A
                                                                                               'SPB':[],    # true power phase B  
                                                                                               'SQB':[],    # reactive power phase B
                                                                                               'SPC':[],    # true power phase C
                                                                                               'SQC':[],    # reactive power phase C
                                                                                               'VMA':[],    # voltage magnitude phase A
                                                                                               'VAA':[],    # voltage angle phase A
                                                                                               'VMB':[],    # voltage magnitude phase B
                                                                                               'VAB':[],    # voltage angle phase B
                                                                                               'VMC':[],    # voltage magnitude phase C
                                                                                               'VAC':[],    # voltage angle phase C
                                                                                               'IMA':[],    # current magnitude phase A
                                                                                               'IAA':[],    # current angle phase A
                                                                                               'IMB':[],    # current magnitude phase B
                                                                                               'IAB':[],    # current angle phase B
                                                                                               'IMC':[],    # current magnitude phase C
                                                                                               'IAC':[],    # current angle phase C
                                                                                               'TS':[]})]   # time stamp of measurement
                                                                                            , sort=False)
        if (self.verbose > 1): 
            print('DSESim::create Entities:')
            print(self.entities[eid]['df_devs'])
           
             
        ''' create vecZ and vecZType '''
        df_devs = self.entities[eid]['df_devs']
        nr_phasors = (df_devs[df_devs['type'] == 'phasor']).shape[0]    
            
        self.entities[eid]['vecZ'] = np.zeros((int(self.entities[eid]['nodes']) - 3) + # P values
                                              (int(self.entities[eid]['nodes']) - 3) + # Q values
                                              (nr_phasors*3    ) + # Voltage magnitude
                                              (nr_phasors*3 - 1),  # Voltage angles
                                              np.float64)

        
        entities = []
        self.data[eid] = {}
        self.data[eid]['v'] = 0
        self.data[eid]['t'] = 0  
        entities.append({'eid': eid, 'type': model})      

        return entities  
    

    def step(self, time, inputs):
        if (self.verbose > 5): print('simulator_dse::step INPUT', time, inputs)

        next_step = time + self.step_size
        
        ''' prepare data to be used in get_data '''
        #self.data = {}
        
        ''' prepare data to be used in get_data and calculate system state '''
        
        ''' for each instance '''
        for dse_eid, attrs in inputs.items():
            attr_v = attrs['v']
            df_devs = self.entities[dse_eid]['df_devs']
            ''' for each smartmeter/phasor '''
            for dev_instance, param in attr_v.items():
                if (param != None and param != 'null' and param != "None"):
                    
                    self.MsgCount += 1 
                    
                    ''' change to dict because NS-3 need to transmit string '''
                    if isinstance(param, str):
                        param = literal_eval(param)
                        
                    dev_idn  = (param['IDT']).split("_")[1]
                    dev_type = param['TYPE']
                    dev_name = dev_instance.split(".")[1]
                    ''' store values already per-unit '''
                    
                    if (self.verbose > 1): 
                        print('simulator_dse::step INPUT PROCESSED: ',
                              'TIME:',  time,
                              'TIME_Sent:', param['TS'],
                              'IDN:',   dev_idn,
                              'TYPE:',  dev_type,
                              'NAME:',  dev_name, 
                              'PARMS:', param)                    
                    
                    
                    for dev_param_key in param.keys():

                        if dev_param_key == 'VA' and dev_type == 'Phasor':
                            df_devs.at[int(dev_idn), 'VMA'] = param['VA'][0] / self.entities[dse_eid]['baseV']
                            df_devs.at[int(dev_idn), 'VAA'] = param['VA'][1]     
                        elif dev_param_key == 'VB' and dev_type == 'Phasor':
                            df_devs.at[int(dev_idn), 'VMB'] = param['VB'][0] / self.entities[dse_eid]['baseV']
                            df_devs.at[int(dev_idn), 'VAB'] = param['VB'][1]                                              
                        elif dev_param_key == 'VC' and dev_type == 'Phasor':
                            df_devs.at[int(dev_idn), 'VMC'] = param['VC'][0] / self.entities[dse_eid]['baseV']
                            df_devs.at[int(dev_idn), 'VAC'] = param['VC'][1]                      
                        elif dev_param_key == 'IA':
                            df_devs.at[int(dev_idn), 'IMA'] = param['IA'][0] / self.entities[dse_eid]['baseI']
                            df_devs.at[int(dev_idn), 'IAA'] = param['IA'][1]                          
                        elif dev_param_key == 'IB':
                            df_devs.at[int(dev_idn), 'IMB'] = param['IB'][0] / self.entities[dse_eid]['baseI']
                            df_devs.at[int(dev_idn), 'IAB'] = param['IB'][1]                         
                        elif dev_param_key == 'IC':
                            df_devs.at[int(dev_idn), 'IMC'] = param['IC'][0] / self.entities[dse_eid]['baseI']
                            df_devs.at[int(dev_idn), 'IAC'] = param['IC'][1]                          
                        elif dev_param_key == 'SPA':
                            df_devs.at[int(dev_idn), 'SPA'] = param['SPA'] / (self.entities[dse_eid]['baseS']*1000)
                            df_devs.at[int(dev_idn), 'SQA'] =  df_devs.at[int(dev_idn), 'SPA'] * np.tan(np.arccos(self.entities[dse_eid]['basePF'] ))                           
                        elif dev_param_key == 'SPB':
                            df_devs.at[int(dev_idn), 'SPB'] = param['SPB'] / (self.entities[dse_eid]['baseS']*1000)
                            df_devs.at[int(dev_idn), 'SQB'] =  df_devs.at[int(dev_idn), 'SPB'] * np.tan(np.arccos(self.entities[dse_eid]['basePF'] ))                                 
                        elif dev_param_key == 'SPC':
                            df_devs.at[int(dev_idn), 'SPC'] = param['SPC'] / (self.entities[dse_eid]['baseS']*1000)
                            df_devs.at[int(dev_idn), 'SQC'] =  df_devs.at[int(dev_idn), 'SPC'] * np.tan(np.arccos(self.entities[dse_eid]['basePF'] ))    
                        elif dev_param_key == 'TS':
                            df_devs.at[int(dev_idn), 'TS']  = param['TS']
                        elif ((dev_param_key == 'VA')  or (dev_param_key == 'VB')  or (dev_param_key == 'VC')) and  (dev_type != 'Phasor'):
                            pass
                        elif (dev_param_key == 'IDT') or (dev_param_key == 'TYPE'):
                            pass
                        else:
                            raise Exception('dev_param_key value unknown:', dev_param_key, "Device:", dev_name) 
                          

            if (0 == time % self.entities[dse_eid]['acc_period']):
                self.data[dse_eid]['v'] = self.MsgCount
                self.data[dse_eid]['t'] = time   
                self.MsgCount = 0
                           
            #(self.entities[dse_eid]['vecZ'], _) = self.createZVectors(dse_eid, len(self.entities[dse_eid]['vecZ']))
       
        return next_step   
    
    
    def get_data(self, outputs):
        if (self.verbose > 0): print('simulator_dse::get_data INPUT', outputs)      
        if (self.verbose > 1): print('simulator_dse::get_data OUTPUT data =', self.data)
        
           

        return self.data   


    def readDevices(self, devsfile):
        
        devs_data = {}
        idx_dev = 0
        current_directory = os.path.dirname(os.path.realpath(__file__))
        pathToFile = os.path.abspath(
            os.path.join(current_directory, devsfile)
        )
        if not os.path.isfile(pathToFile):
            print('File Actives does not exist: ' + pathToFile)
            sys.exit()
        else:
            with open(pathToFile, 'r') as csvFile:
                csvobj = csv.reader(csvFile)
                next(csvobj, None)
                for rows in csvobj:
                    devs_data[idx_dev] = {}
                    devs_data[idx_dev]['idn']    = rows[0]
                    devs_data[idx_dev]['device'] = rows[1]
                    devs_data[idx_dev]['src']    = rows[2]
                    devs_data[idx_dev]['error']  = np.float64(rows[5])
                    idx_dev = idx_dev + 1
 
        return devs_data
    
    
    def createZVectors(self, eid, length):
        vecZ = np.zeros(length, np.float64)
        vecZType = {}
        df_devs = self.entities[eid]['df_devs']
        bus_list = df_devs.src.unique()
        bus_list.sort()
        
        ''' P/Q values '''
        pwr_fields = ['SPA', 'SQA', 'SPB', 'SQB', 'SPC', 'SQC']
        sm_bus = np.delete(bus_list, 0, 0)
        sm_bus = sm_bus.astype(int)
        len_vec = len(sm_bus) 
        for bus in sm_bus:
            df_power = df_devs[df_devs['src'] == bus]
            rec_power = pd.concat([pd.Series(df_power[c].dropna().values, name=c) for c in pwr_fields], axis=1)
            if not rec_power.empty:
                vecZ[(bus-2)*3]   = rec_power.iloc[0]['SPA']
                vecZ[(bus-2)*3+1] = rec_power.iloc[0]['SPB']
                vecZ[(bus-2)*3+2] = rec_power.iloc[0]['SPC']
                vecZ[len_vec*3 + (bus-2)*3]   = rec_power.iloc[0]['SQA']
                vecZ[len_vec*3 + (bus-2)*3+1] = rec_power.iloc[0]['SQB']
                vecZ[len_vec*3 + (bus-2)*3+2] = rec_power.iloc[0]['SQC']
            
        if (self.verbose > 3): 
            print('DSESim::createZVectors:')
            self.showVector(vecZ, "vecZ")   
        
            
        ''' V values '''
        len_vec = len_vec * 3 * 2       
        vm_fields = ['VMA', 'VMB', 'VMC']        
        ph_bus = df_devs[df_devs['type'] == 'phasor']
        ph_bus = ph_bus.loc[:,"src"]
        ph_bus = ph_bus.astype(int) 
        ph_bus = list(ph_bus)
        idx = 0    
        for bus in ph_bus:
            df_vm = df_devs[(df_devs['src'] == bus) & (df_devs['type'] == 'phasor')]
            rec_vm = pd.concat([pd.Series(df_vm[c].dropna().values, name=c) for c in vm_fields], axis=1) 
            if not rec_vm.empty:                  
                vecZ[len_vec + (idx)*3]   = abs(rec_vm.iloc[0]['VMA'])
                vecZ[len_vec + (idx)*3+1] = abs(rec_vm.iloc[0]['VMB'])
                vecZ[len_vec + (idx)*3+2] = abs(rec_vm.iloc[0]['VMC'])
            idx = idx + 1
        if (self.verbose > 3): 
            print('DSESim::createZVectors:')
            self.showVector(vecZ, "vecZ")   

        
        ''' Theta values '''
        len_vec = len_vec + len(ph_bus) * 3
        baseNode = self.entities[eid]['baseNode']
        base_angle = df_devs.at[baseNode, 'VAA']
        va_fields = ['VAA', 'VAB', 'VAC']
        idx = 0 
        for bus in ph_bus:
            df_va = df_devs[(df_devs['src'] == bus) & (df_devs['type'] == 'phasor')]
            rec_va = pd.concat([pd.Series(df_va[c].dropna().values, name=c) for c in va_fields], axis=1)    
            if bus != baseNode:
                if not rec_va.empty:                            
                    vecZ[len_vec + idx]   = rec_va.iloc[0]['VAA'] - base_angle
                    vecZ[len_vec + idx+1] = rec_va.iloc[0]['VAB'] - base_angle
                    vecZ[len_vec + idx+2] = rec_va.iloc[0]['VAC'] - base_angle
                idx = idx+3
            else:
                if not rec_va.empty:                 
                    vecZ[len_vec + idx]   = rec_va.iloc[0]['VAB'] - base_angle
                    vecZ[len_vec + idx+1] = rec_va.iloc[0]['VAC'] - base_angle         
                idx = idx+2      

        if (self.verbose > 1): 
            print('DSESim::createZVectors:')
            self.showVector(vecZ, "vecZ")   

        return vecZ, vecZType
 
    
    
    def showVector(self, vec, name):
        vector = vec
        for i in range(len(vector)):
            print(name, "[",   "{:3.0f}".format(i),    "]:", "{:12.9f}".format(vector[i]), end=' ')
            if (((i+1)%5) == 0):
                print("")
        print("")        
        
        
    
    