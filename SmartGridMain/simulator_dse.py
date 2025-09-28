'''
Created on Nov. 11, 2019
Mosaik interface for the Distribution State Estimation.

@file    simulator_dse.py
@author  Evandro de Souza
@date    2019.11.11  
@version 0.1
@company University of Alberta - Computing Science
'''

import queue
from tabnanny import verbose
import mosaik_api
import numpy as np
import pandas as pd
import os
import sys
import csv
from ast import literal_eval
import scipy.io as spio
import math
from pathlib import Path
import datetime

META = {
	'api-version': '3.0',
	'type': 'hybrid',
    'models': {
        'DSESim': {
            'public': True,
            'params': ['idt', 'ymat_file', 'devs_file', 'acc_period', 'max_iter', 'threshold', 'baseS', 'baseV', 'baseNode', 'basePF', 'se_period', 'se_result', 'pseudo_loads', 'verbose'],
            'attrs': ['v', 't'],
            'trigger': ['v', 't'],
            'non-persistent': ['v', 't'],
        },
    },
}

class Estimator(mosaik_api.Simulator):

    def __init__(self):
        super().__init__(META)
        self.entities = {}
        self.next = {}
        self.instances = {}
        self.devParams = {}
        self.data = {}


    def init(self, sid, time_resolution, eid_prefix=None, verbose=0):
        if eid_prefix is not None:
            self.eid_prefix = eid_prefix
        self.sid       = sid
        self.verbose   = verbose
        self.cktState  = {}
        self.MsgCount  = 0
        self.eventQueue = queue.PriorityQueue()
        self.total_exec_time = 0.0

        return self.meta


    def create(self, num, model, idt, ymat_file, devs_file, acc_period, max_iter, threshold, baseS, baseV, baseNode, basePF, se_period, pseudo_loads, se_result):
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
        self.entities[eid]['se_period']  = se_period
        self.entities[eid]['pseudo_loads']  = pseudo_loads
        self.entities[eid]['se_result']  = se_result
        self.entities[eid]['vecZ']       = {}
        self.entities[eid]['nodes']      = 0
        self.entities[eid]['df_devs']    = pd.DataFrame({})


        ''' read ymat_file and get number of nodes '''
        self.entities[eid]['ymat_data'] = np.load(ymat_file)
        self.entities[eid]['nodes'] = len(self.entities[eid]['ymat_data'])
        self.entities[eid]['ymat_data'] = self.entities[eid]['ymat_data'] / self.entities[eid]['baseY']
        if (self.verbose > 0): print('Estimator::create Nodes YMat:', self.entities[eid]['nodes'])


        ''' get device list '''
        self.entities[eid]['df_devs'] = pd.read_csv(
            devs_file,
            delimiter = ','
        )
        self.entities[eid]['df_devs']['index'] = self.entities[eid]['df_devs']['type'] + '_' \
                                                    + self.entities[eid]['df_devs']['src'].apply(str) + '-' \
                                                    + self.entities[eid]['df_devs']['dst'].apply(str) + '.' \
                                                    + self.entities[eid]['df_devs']['cidx'].apply(str) + '.' \
                                                    + self.entities[eid]['df_devs']['didx'].apply(str)
        self.entities[eid]['df_devs'] = self.entities[eid]['df_devs'].set_index('index')
        self.entities[eid]['df_devs'] = pd.concat([self.entities[eid]['df_devs'], pd.DataFrame({'SPA':[],    # true power phase A
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
                                                                                               'TS':[]})]   # last time stamp
                                                                                            , sort=False)
        if (self.verbose > 1):
            print('Estimator::create Entities:')
            print(self.entities[eid]['df_devs'])


        ''' create vecZ and vecZType '''
        df_devs = self.entities[eid]['df_devs']
        nr_phasors = (df_devs[df_devs['type'] == 'Phasor']).shape[0]

        self.entities[eid]['vecZ'] = np.zeros((int(self.entities[eid]['nodes']) - 3) + # P values
                                              (int(self.entities[eid]['nodes']) - 3) + # Q values
                                              (nr_phasors*3    ) + # Voltage magnitude
                                              (nr_phasors*3 - 1),  # Voltage angles
                                              np.float64)


        entities = []
        self.data[eid] = {}
        self.data[eid]['v'] = []
        self.data[eid]['t'] = []
        self.data[eid]['v'].append(0)
        self.data[eid]['t'].append(0)
        entities.append({'eid': eid, 'type': model})

        return entities


    def step(self, time, inputs, max_advance):
        start = datetime.datetime.now()
        if (self.verbose > 1): print('simulator_dse::step INPUT', time, inputs)

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

                    # For now assume that only one element arrives at a time
                    param = param[0]

                    ''' change to dict because NS-3 need to transmit string '''
                    if isinstance(param, str):
                        param = literal_eval(param)

                    dev_id  = param['IDT']
                    dev_type = param['TYPE']
                    ''' store values already per-unit '''

                    if (self.verbose > 1):
                        print('simulator_dse::step INPUT PROCESSED: ',
                              'TIME:',  time,
                              'TIME_Sent:', param['TS'],
                              'ID:',   dev_id,
                              'TYPE:',  dev_type,
                              'PARMS:', param)


                    for dev_param_key in param.keys():
                        if dev_param_key == 'VA' and dev_type == 'Phasor':
                            df_devs.at[dev_id, 'VMA'] = param['VA'][0] / self.entities[dse_eid]['baseV']
                            df_devs.at[dev_id, 'VAA'] = param['VA'][1]
                        elif dev_param_key == 'VB' and dev_type == 'Phasor':
                            df_devs.at[dev_id, 'VMB'] = param['VB'][0] / self.entities[dse_eid]['baseV']
                            df_devs.at[dev_id, 'VAB'] = param['VB'][1]
                        elif dev_param_key == 'VC' and dev_type == 'Phasor':
                            df_devs.at[dev_id, 'VMC'] = param['VC'][0] / self.entities[dse_eid]['baseV']
                            df_devs.at[dev_id, 'VAC'] = param['VC'][1]
                        elif dev_param_key == 'IA':
                            df_devs.at[dev_id, 'IMA'] = param['IA'][0] / self.entities[dse_eid]['baseI']
                            df_devs.at[dev_id, 'IAA'] = param['IA'][1]
                        elif dev_param_key == 'IB':
                            df_devs.at[dev_id, 'IMB'] = param['IB'][0] / self.entities[dse_eid]['baseI']
                            df_devs.at[dev_id, 'IAB'] = param['IB'][1]
                        elif dev_param_key == 'IC':
                            df_devs.at[dev_id, 'IMC'] = param['IC'][0] / self.entities[dse_eid]['baseI']
                            df_devs.at[dev_id, 'IAC'] = param['IC'][1]
                        elif dev_param_key == 'SPA':
                            df_devs.at[dev_id, 'SPA'] = param['SPA'] / (self.entities[dse_eid]['baseS']*1000)
                            df_devs.at[dev_id, 'SQA'] =  df_devs.at[dev_id, 'SPA'] * np.tan(np.arccos(self.entities[dse_eid]['basePF'] ))
                        elif dev_param_key == 'SPB':
                            df_devs.at[dev_id, 'SPB'] = param['SPB'] / (self.entities[dse_eid]['baseS']*1000)
                            df_devs.at[dev_id, 'SQB'] =  df_devs.at[dev_id, 'SPB'] * np.tan(np.arccos(self.entities[dse_eid]['basePF'] ))
                        elif dev_param_key == 'SPC':
                            df_devs.at[dev_id, 'SPC'] = param['SPC'] / (self.entities[dse_eid]['baseS']*1000)
                            df_devs.at[dev_id, 'SQC'] =  df_devs.at[dev_id, 'SPC'] * np.tan(np.arccos(self.entities[dse_eid]['basePF'] ))
                        elif dev_param_key == 'TS':
                            df_devs.at[dev_id, 'TS']  = param['TS']
                        elif ((dev_param_key == 'VA')  or (dev_param_key == 'VB')  or (dev_param_key == 'VC')) and  (dev_type != 'Phasor'):
                            pass
                        elif (dev_param_key == 'IDT') or (dev_param_key == 'TYPE'):
                            pass
                        else:
                            raise Exception('dev_param_key value unknown:', dev_param_key, "Device:", dev_id)

        for dse_eid in self.entities:
            if (0 == time % self.entities[dse_eid]['acc_period']):
                self.data[dse_eid] = {}
                self.data[dse_eid]['v'] = []
                self.data[dse_eid]['t'] = []
                self.data[dse_eid]['v'].append(self.MsgCount)
                self.data[dse_eid]['t'].append(time)
                self.MsgCount = 0
                self.eventQueue.put(time + self.entities[dse_eid]['acc_period'])

            #(self.entities[dse_eid]['vecZ'], _) = self.createZVectors(dse_eid, len(self.entities[dse_eid]['vecZ']))
        # se_period = 1000
        # if next_step == 500:
        #     print("Check the phasors!")
            if (time > 0) and (time % self.entities[dse_eid]['se_period'] == 0):
            # if time % se_period == 0:
                z, ztype, error_cov = self.get_measurements(self.entities[dse_eid]['df_devs'], time)
                stop_counter = 0
                while stop_counter < 5:
                    v_wls, iter_number = self.state_estimation(self.entities[dse_eid]['ymat_data'], z, ztype, error_cov,
                                                            self.entities[dse_eid]['max_iter'], self.entities[dse_eid]['threshold'])
                    if iter_number > 1 & iter_number < 10:
                        stop_counter = 5
                    else:
                        stop_counter += 1
                # array_name = 'v_wls_{}'.format(int(time /  self.entities[dse_eid]['se_period']))
                array_name = 'v_wls'
                # if Path('C:/OpenDSS/DSSE33DetailedMultiPhase/wls_results.mat').is_file():
                if time / self.entities[dse_eid]['se_period'] > 1:
                        mat = spio.loadmat(self.entities[dse_eid]['se_result'], squeeze_me=True)
                        mat[array_name] = np.vstack((mat[array_name], v_wls))
                        spio.savemat(self.entities[dse_eid]['se_result'], mat)
                else:
                    spio.savemat(self.entities[dse_eid]['se_result'], {array_name: v_wls})
                    
            if time % self.entities[dse_eid]['se_period'] == 0:
                self.eventQueue.put(time + self.entities[dse_eid]['se_period'])

        #--- if there is an event in the future, return next step time
        if not self.eventQueue.empty():
            #--- Filter the next time steps and return the earliest next time step
            self.next_step = self.eventQueue.queue[0]
            while(not self.eventQueue.empty() and time >= self.eventQueue.queue[0]):
                self.next_step = self.eventQueue.get()
            if self.next_step > time:
                if (self.verbose > 0):  print("simulator_dse::next step: ", self.next_step)
                sys.stdout.flush()
                end = datetime.datetime.now()
                self.total_exec_time = self.total_exec_time + (end - start).total_seconds()

                return self.next_step

        end = datetime.datetime.now()
        self.total_exec_time = self.total_exec_time + (end - start).total_seconds()

    def state_estimation(self, ybus, z, ztype, err_cov, iter_max, threshold):
        if (self.verbose > 1):  print("simulator_dse::state estimation")
        ztype= np.array(ztype)
        n = len(ybus)  # number of single phase nodes
        g = np.real(ybus)  # real part of the admittance matrix
        b = np.imag(ybus)  # imaginary art of the admittance matrix
        x = np.concatenate(
            ([-2 * math.pi / 3, -4 * math.pi / 3],
             np.tile([0, -2 * math.pi / 3, -4 * math.pi / 3], math.floor(n / 3) - 1),
             np.ones(n) * (1 + .000001 * np.random.randn(n))))  # our initial guess fot the voltage phasors
        # x = np.concatenate((np.angle(vtrue[1:]), np.abs(vtrue)))
        k = 0
        cont = True
        while k < iter_max and cont:
            v = x[n - 1:]  # voltage magnitudes
            th = np.concatenate(([0], x[0: n - 1]))  # voltage angles. we add a 0 for the reference bus
            # calculating the measurement functions h(x)
            h = np.zeros(len(z))
            for m in range(0, len(z)):
                if ztype[m, 0] == 2:  # Pi active load demand at node i
                    i = ztype[m, 1] - 1
                    for jj in range(n):
                        h[m] += v[i] * v[jj] * (
                                    g[i, jj] * math.cos(th[i] - th[jj]) + b[i, jj] * math.sin(th[i] - th[jj]))
                elif ztype[m, 0] == 4:  # Qi reactive load demand at node i
                    i = ztype[m, 1] - 1
                    for jj in range(n):
                        h[m] += v[i] * v[jj] * (
                                    g[i, jj] * math.sin(th[i] - th[jj]) - b[i, jj] * math.cos(th[i] - th[jj]))
                elif ztype[m, 0] == 5:  # |Vi| voltage phasor magnitude at bus i
                    i = ztype[m, 1] - 1
                    h[m] = v[i]
                elif ztype[m, 0] == 6:  # Theta Vi voltage phasor phase angle at bus i
                    i = ztype[m, 1] - 1
                    h[m] = th[i]
                elif ztype[m, 0] == 7 or ztype[m, 0] == 8:
                    i = ztype[m, 1] - 1  # sending node
                    jj = ztype[m, 2] - 1  # receiving node
                    ph = ztype[m, 3] - 1  # phase
                    a1, b1, c1 = 3 * i + [0, 1, 2]
                    a2, b2, c2 = 3 * jj + [0, 1, 2]
                    yline = -ybus[np.array([a1, b1, c1])[:, None], np.array([a2, b2, c2])]
                    gline = np.real(yline)
                    bline = np.imag(yline)
                    if ztype[m, 0] == 7:  # real part of Iij phasor
                        h[m] = gline[ph, 0] * (v[a1] * math.cos(th[a1]) - v[a2] * math.cos(th[a2])) - \
                               bline[ph, 0] * (v[a1] * math.sin(th[a1]) - v[a2] * math.sin(th[a2])) + \
                               gline[ph, 1] * (v[b1] * math.cos(th[b1]) - v[b2] * math.cos(th[b2])) - \
                               bline[ph, 1] * (v[b1] * math.sin(th[b1]) - v[b2] * math.sin(th[b2])) + \
                               gline[ph, 2] * (v[c1] * math.cos(th[c1]) - v[c2] * math.cos(th[c2])) - \
                               bline[ph, 2] * (v[c1] * math.sin(th[c1]) - v[c2] * math.sin(th[c2]))
                    else:  # imaginary part of Iij phasor
                        h[m] = gline[ph, 0] * (v[a1] * math.sin(th[a1]) - v[a2] * math.sin(th[a2])) + \
                               bline[ph, 0] * (v[a1] * math.cos(th[a1]) - v[a2] * math.cos(th[a2])) + \
                               gline[ph, 1] * (v[b1] * math.sin(th[b1]) - v[b2] * math.sin(th[b2])) + \
                               bline[ph, 1] * (v[b1] * math.cos(th[b1]) - v[b2] * math.cos(th[b2])) + \
                               gline[ph, 2] * (v[c1] * math.sin(th[c1]) - v[c2] * math.sin(th[c2])) + \
                               bline[ph, 2] * (v[c1] * math.cos(th[c1]) - v[c2] * math.cos(th[c2]))
                else:
                    print("Measurement type not defined!")
            # print(h-z)

            # calculating the jacobian of h
            h_jacob = np.zeros([len(z), len(x)])
            for m in range(0, len(z)):
                if ztype[m, 0] == 2:  # Pi active load demand at node i
                    i = ztype[m, 1] - 1
                    for jj in range(n):
                        if jj != i:
                            if jj > 0:
                                h_jacob[m, jj - 1] = v[i] * v[jj] * (g[i, jj] * math.sin(th[i] - th[jj]) -
                                                                     b[i, jj] * math.cos(th[i] - th[jj]))
                            h_jacob[m, jj + n - 1] = v[i] * (g[i, jj] * math.cos(th[i] - th[jj]) +
                                                             b[i, jj] * math.sin(th[i] - th[jj]))
                    if i > 0:
                        h_jacob[m, i - 1] = -v[i] ** 2 * b[i, i]
                        for jj in range(n):
                            h_jacob[m, i - 1] += v[i] * v[jj] * (-g[i, jj] * math.sin(th[i] - th[jj]) +
                                                                 b[i, jj] * math.cos(th[i] - th[jj]))
                    h_jacob[m, i + n - 1] = v[i] * g[i, i]
                    for jj in range(n):
                        h_jacob[m, i + n - 1] += v[jj] * (g[i, jj] * math.cos(th[i] - th[jj]) +
                                                          b[i, jj] * math.sin(th[i] - th[jj]))

                elif ztype[m, 0] == 4:  # Qi reactive load demand at node i
                    i = ztype[m, 1] - 1
                    for jj in range(n):
                        if jj != i:
                            if jj > 0:
                                h_jacob[m, jj - 1] = v[i] * v[jj] * (-g[i, jj] * math.cos(th[i] - th[jj]) -
                                                                     b[i, jj] * math.sin(th[i] - th[jj]))
                            h_jacob[m, jj + n - 1] = v[i] * (g[i, jj] * math.sin(th[i] - th[jj]) -
                                                             b[i, jj] * math.cos(th[i] - th[jj]))
                    if i > 0:
                        h_jacob[m, i - 1] = -v[i] ** 2 * g[i, i]
                        for jj in range(n):
                            h_jacob[m, i - 1] += v[i] * v[jj] * (g[i, jj] * math.cos(th[i] - th[jj]) +
                                                                 b[i, jj] * math.sin(th[i] - th[jj]))
                    h_jacob[m, i + n - 1] = -v[i] * b[i, i]
                    for jj in range(n):
                        h_jacob[m, i + n - 1] += v[jj] * (g[i, jj] * math.sin(th[i] - th[jj]) -
                                                          b[i, jj] * math.cos(th[i] - th[jj]))

                elif ztype[m, 0] == 5:  # |Vi| voltage phasor magnitude at bus i
                    i = ztype[m, 1] - 1
                    h_jacob[m, i + n - 1] = 1

                elif ztype[m, 0] == 6:  # Theta Vi voltage phasor phase angle at bus i
                    i = ztype[m, 1] - 1
                    h_jacob[m, i - 1] = 1

                elif ztype[m, 0] == 7 or ztype[m, 0] == 8:
                    i = ztype[m, 1] - 1  # sending node
                    jj = ztype[m, 2] - 1  # receiving node
                    ph = ztype[m, 3] - 1  # phase
                    a1, b1, c1 = 3 * i + [0, 1, 2]
                    a2, b2, c2 = 3 * jj + [0, 1, 2]
                    yline = -ybus[np.array([a1, b1, c1])[:, None], np.array([a2, b2, c2])]
                    gline = np.real(yline)
                    bline = np.imag(yline)
                    if ztype[m, 0] == 7:  # real part of Iij phasor
                        # derivatives with respect to voltage phase angles
                        if a1 > 0:
                            h_jacob[m, a1 - 1] = -gline[ph, 0] * v[a1] * math.sin(th[a1]) - bline[ph, 0] * v[
                                a1] * math.cos(th[a1])
                        h_jacob[m, b1 - 1] = -gline[ph, 1] * v[b1] * math.sin(th[b1]) - bline[ph, 1] * v[b1] * math.cos(
                            th[b1])
                        h_jacob[m, c1 - 1] = -gline[ph, 2] * v[c1] * math.sin(th[c1]) - bline[ph, 2] * v[c1] * math.cos(
                            th[c1])
                        h_jacob[m, a2 - 1] = gline[ph, 0] * v[a2] * math.sin(th[a2]) + bline[ph, 0] * v[a2] * math.cos(
                            th[a2])
                        h_jacob[m, b2 - 1] = gline[ph, 1] * v[b2] * math.sin(th[b2]) + bline[ph, 1] * v[b2] * math.cos(
                            th[b2])
                        h_jacob[m, c2 - 1] = gline[ph, 2] * v[c2] * math.sin(th[c2]) + bline[ph, 2] * v[c2] * math.cos(
                            th[c2])
                        # derivatives with respect to voltage magnitudes
                        h_jacob[m, a1 + n - 1] = gline[ph, 0] * math.cos(th[a1]) - bline[ph, 0] * math.sin(th[a1])
                        h_jacob[m, b1 + n - 1] = gline[ph, 1] * math.cos(th[b1]) - bline[ph, 1] * math.sin(th[b1])
                        h_jacob[m, c1 + n - 1] = gline[ph, 2] * math.cos(th[c1]) - bline[ph, 2] * math.sin(th[c1])
                        h_jacob[m, a2 + n - 1] = -gline[ph, 0] * math.cos(th[a2]) + bline[ph, 0] * math.sin(th[a2])
                        h_jacob[m, b2 + n - 1] = -gline[ph, 1] * math.cos(th[b2]) + bline[ph, 1] * math.sin(th[b2])
                        h_jacob[m, c2 + n - 1] = -gline[ph, 2] * math.cos(th[c2]) + bline[ph, 2] * math.sin(th[c2])
                    else:  # imaginary part of Iij phasor
                        if a1 > 0:
                            h_jacob[m, a1 - 1] = gline[ph, 0] * v[a1] * math.cos(th[a1]) - bline[ph, 0] * v[
                                a1] * math.sin(th[a1])
                        h_jacob[m, b1 - 1] = gline[ph, 1] * v[b1] * math.cos(th[b1]) - bline[ph, 1] * v[b1] * math.sin(
                            th[b1])
                        h_jacob[m, c1 - 1] = gline[ph, 2] * v[c1] * math.cos(th[c1]) - bline[ph, 2] * v[c1] * math.sin(
                            th[c1])
                        h_jacob[m, a2 - 1] = -gline[ph, 0] * v[a2] * math.cos(th[a2]) + bline[ph, 0] * v[a2] * math.sin(
                            th[a2])
                        h_jacob[m, b2 - 1] = -gline[ph, 1] * v[b2] * math.cos(th[b2]) + bline[ph, 1] * v[b2] * math.sin(
                            th[b2])
                        h_jacob[m, c2 - 1] = -gline[ph, 2] * v[c2] * math.cos(th[c2]) + bline[ph, 2] * v[c2] * math.sin(
                            th[c2])
                        # derivatives with respect to voltage magnitudes
                        h_jacob[m, a1 + n - 1] = gline[ph, 0] * math.sin(th[a1]) + bline[ph, 0] * math.cos(th[a1])
                        h_jacob[m, b1 + n - 1] = gline[ph, 1] * math.sin(th[b1]) + bline[ph, 1] * math.cos(th[b1])
                        h_jacob[m, c1 + n - 1] = gline[ph, 2] * math.sin(th[c1]) + bline[ph, 2] * math.cos(th[c1])
                        h_jacob[m, a2 + n - 1] = -gline[ph, 0] * math.sin(th[a2]) - bline[ph, 0] * math.cos(th[a2])
                        h_jacob[m, b2 + n - 1] = -gline[ph, 1] * math.sin(th[b2]) - bline[ph, 1] * math.cos(th[b2])
                        h_jacob[m, c2 + n - 1] = -gline[ph, 2] * math.sin(th[c2]) - bline[ph, 2] * math.cos(th[c2])

                else:
                    print("Measurement type not defined!")
            # the right hand side of the equation
            rhs = h_jacob.transpose() @ np.linalg.inv(err_cov) @ (z - h)
            # d1 = h_jacob.transpose() @ np.linalg.inv(err_cov)
            # d2 = np.linalg.inv(err_cov) @ (z-h)
            # saving to mat file
            # scipy.io.savemat('C:/Users/Moosa Moghimi/Desktop/testArrays.mat', {'d11': d1, 'd22': d2})
            # print("Array saved")
            # the gain matrix
            gain = h_jacob.transpose() @ np.linalg.inv(err_cov) @ h_jacob

            delta_x = np.linalg.solve(gain, rhs)

            x += delta_x
            if np.max(np.absolute(delta_x)) < threshold:
                cont = False
            k += 1
        v = x[n - 1:]  # voltage magnitudes
        th = np.concatenate(([0], x[0: n - 1]))  # voltage angles. we add a 0 for the reference bus
        v_phasor = v * (np.cos(th) + 1j * np.sin(th))
        return v_phasor, k

    def get_measurements(self, df_devs, time):
        if (self.verbose > 0):  print("simulator_dse::get measurements: time = ", time)
        data = df_devs
        z = []
        z_type = []
        error_cov = []  # covariance matrix of measurement errors

        # Pseudo measurements
        # find the corresponding pseudo measurement
        # Currently the simualation is only running for a few seconds
        # Map the time to indexes accordingly
        device = self.entities[list(self.entities.keys())[0]]
        hour = time // device['se_period'] + 8 # to start at 9 am
        # load the file with pseudo measurements
        mat = spio.loadmat(device['pseudo_loads'], squeeze_me=True)
        p = mat['PpMean']
        q = mat['QpMean']
        p_std = mat['PpStd']
        q_std = mat['QpStd']

        hourIndex = (hour - 1) % 24

        for node in range(4, 3 * 33 + 1):
            z.append(-p[node - 4][hourIndex])
            z_type.append([2, node, 0, 0])
            error_cov.append(np.square(p_std[node - 4][hourIndex]))
            z.append(-q[node - 4][hourIndex])
            z_type.append([4, node, 0, 0])
            error_cov.append(np.square(q_std[node - 4][hourIndex]))
        for device in list(data.index.values):
            # device IDs are no longer integers, but strings
            # extract the node IDs (this will not work if multiple
            # devices are present in a single node)
            node = int(data.loc[device, 'src'])

            # node voltage phasor measurements
            if data.loc[device, 'VMA'] > 0:
                z.append(data.loc[device, 'VMA'])
                z_type.append([5, 3 * node - 2, 0, 0])
                error_cov.append(np.square(data.loc[device, 'error']))
                z.append(data.loc[device, 'VAA'])
                z_type.append([6, 3 * node - 2, 0, 0])
                error_cov.append(np.square(data.loc[device, 'error']))
            if data.loc[device, 'VMB'] > 0:
                z.append(data.loc[device, 'VMB'])
                z_type.append([5, 3 * node - 1, 0, 0])
                error_cov.append(np.square(data.loc[device, 'error']))
                z.append(data.loc[device, 'VAB'])
                z_type.append([6, 3 * node - 1, 0, 0])
                error_cov.append(np.square(data.loc[device, 'error']))
            if data.loc[device, 'VMC'] > 0:
                z.append(data.loc[device, 'VMC'])
                z_type.append([5, 3 * node, 0, 0])
                error_cov.append(np.square(data.loc[device, 'error']))
                z.append(data.loc[device, 'VAC'])
                z_type.append([6, 3 * node, 0, 0])
                error_cov.append(np.square(data.loc[device, 'error']))

            # line current phasor measurements
            if np.abs(data.loc[device, 'IMA']) > 0:
                ns, nr = self.get_line_nodes(device, data)
                current = data.loc[device, 'IMA'] * np.exp(complex(0, data.loc[device, 'IAA']))
                z.append(np.real(current))
                z_type.append([7, ns, nr, 1])
                error_cov.append(np.square(data.loc[device, 'error']))
                z.append(np.imag(current))
                z_type.append([8, ns, nr, 1])
                error_cov.append(np.square(data.loc[device, 'error']))
            if np.abs(data.loc[device, 'IMB']) > 0:
                ns, nr = self.get_line_nodes(device, data)
                current = data.loc[device, 'IMB'] * np.exp(complex(0, data.loc[device, 'IAB']))
                z.append(np.real(current))
                z_type.append([7, ns, nr, 2])
                error_cov.append(np.square(data.loc[device, 'error']))
                z.append(np.imag(current))
                z_type.append([8, ns, nr, 2])
                error_cov.append(np.square(data.loc[device, 'error']))
            if np.abs(data.loc[device, 'IMC']) > 0:
                ns, nr = self.get_line_nodes(device, data)
                current = data.loc[device, 'IMC'] * np.exp(complex(0, data.loc[device, 'IAC']))
                z.append(np.real(current))
                z_type.append([7, ns, nr, 3])
                error_cov.append(np.square(data.loc[device, 'error']))
                z.append(np.imag(current))
                z_type.append([8, ns, nr, 3])
                error_cov.append(np.square(data.loc[device, 'error']))

        return z, z_type, np.diag(error_cov)

    def get_line_nodes(self, device, data):
        line = data.loc[device, 'cktElement'][5:]
        terminal = int(data.loc[device, 'cktTerminal'][3:])
        nodes = line.partition('-')
        ns = 0
        nr = 0
        if terminal == 1:
            ns = int(nodes[terminal - 1])
            nr = int(nodes[terminal + 1])
        elif terminal == 2:
            ns = int(nodes[terminal])
            nr = int(nodes[terminal - 2])
        else:
            print('Error: terminal node can only be 1 or 2')
        return ns, nr


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
            print('Estimator::createZVectors:')
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
            print('Estimator::createZVectors:')
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
            print('Estimator::createZVectors:')
            self.showVector(vecZ, "vecZ")

        return vecZ, vecZType



    def showVector(self, vec, name):
        vector = vec
        for i in range(len(vector)):
            print(name, "[",   "{:3.0f}".format(i),    "]:", "{:12.9f}".format(vector[i]), end=' ')
            if (((i+1)%5) == 0):
                print("")
        print("")


    def finalize(self):
        print("Estimator::finalize:total execution time = ", self.total_exec_time)
        sys.stdout.flush()
