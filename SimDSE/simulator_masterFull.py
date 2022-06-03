'''
Created on Oct. 30, 2019
Main script for DSE simulation (SimDSE)

@file    simulator_master.py
@author  Evandro de Souza
@date    2019.10.30  
@version 0.1
@company University of Alberta - Computing Science
'''

import os
import sys
import csv
import mosaik
import argparse
from datetime import datetime
import numpy as np
from pathlib import Path

#--- Base Directory
BASE_DIR = os.getcwd()
BASE_DIR = str((Path(BASE_DIR)).parent) + "/"

#--- NS3 executables and library directory
NS3_EXE_PATH = BASE_DIR + 'NS3Mosaik'
NS3_LIB_PATH = BASE_DIR + 'ns-allinone-3.33/ns-3.33/build/lib'


#--- Project directory
PRJ_PATH = BASE_DIR + 'SimDSE/'

#--- Configuration files
TOPO_FILE    = PRJ_PATH + 'config/master33Full.dss'
NWL_FILE     = PRJ_PATH + 'config/IEEE33_NodeWithLoadFull.csv'
ADJMAT_FILE  = PRJ_PATH + 'config/IEEE33_AdjMatrixFull.txt'
COORDS_FILE  = PRJ_PATH + 'config/IEEE33_BusXYFull.csv'
DEVS_FILE    = PRJ_PATH + 'config/IEEE33_DevicesNode33Full.csv'


#--- Simulators configuration
SIM_CONFIG = {
    'Collector': {
        'python': 'simulator_collector:Collector',
    },
    'PFlowSim': {
        'python': 'simulator_pflow:PFlowSim',
    },
    'DSESim': {
        'python': 'simulator_dse:DSESim',       
    },   
    'PktNetSim': {
        'cmd': NS3_EXE_PATH + '/NS3MosaikSim %(addr)s',
#        'cmd': NS3_EXE_PATH + '/cosimul-cplusplus %(addr)s',
        'cwd': Path( os.path.abspath( os.path.dirname( NS3_EXE_PATH ) ) ),
        'env': {
                'LD_LIBRARY_PATH': NS3_LIB_PATH
                # 'NS_LOG': "SmartgridDefaultSimulatorImpl=all"
        },
    },
}


#--- Simulation total time
# END_TIME =  59 * 1000 + 1    #  59001 ms
END_TIME = 10000

#--- Devices and application for simulation
devParams = {}

#--- Mosaik Configuration
MOSAIK_CONFIG = {
    # 'execution_graph': True,
    # 'sim_progress': None,
    'start_timeout': 600,  # seconds
    'stop_timeout' : 10,   # seconds    
}


#--- Load Simulation devices and configurations
def readDevices(devsfile):
    
    global devParams
    
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
            next(csvobj)
            for rows in csvobj:
                instance = rows[0] + "_" +  rows[1] + "_" + rows[6]
                devParams[instance] = {}
                devParams[instance]['idt']         = rows[0]
                devParams[instance]['device']      = rows[1]
                devParams[instance]['src']         = rows[2]
                devParams[instance]['dst']         = rows[3]
                devParams[instance]['step_size']   = rows[4]
                devParams[instance]['error']       = rows[5]
                devParams[instance]['cktElement']  = rows[6]
                devParams[instance]['cktTerminal'] = rows[7]
                devParams[instance]['cktPhase']    = rows[8]
                devParams[instance]['cktProperty'] = rows[9] 


def main():
    #--- Process input arguments
    parser = argparse.ArgumentParser(description='Run Smartgrid simulation')
    parser.add_argument( '--devs_file', type=str, help='devices configuration file', default = DEVS_FILE )
    parser.add_argument( '--random_seed', type=int, help='ns-3 random generator seed', default=1 )
    args = parser.parse_args()
    print( 'Starting simulation with args: {0}'.format( vars( args ) ) )
    
    readDevices(args.devs_file)
    world = mosaik.World( sim_config=SIM_CONFIG, mosaik_config=MOSAIK_CONFIG, debug=True )
    create_scenario( world, args )
    world.run( until=END_TIME )
    

def  create_scenario( world, args ):
    #---
    #--- Simulators configuration
    #---
    pflowsim    = world.start('PFlowSim',    
                              topofile = TOPO_FILE,
                              nwlfile  = NWL_FILE,
                              loadgen_interval = 1000,
                              test = False,
                              verbose = 0)        


    collector   = world.start('Collector',   
                              eid_prefix='Collector_',
                              verbose = 0,
                              out_list = False,
                              h5_save = True,
                              h5_panelname = 'Collector',
                              h5_storename='data/CollectorStore_Full.hd5')

    
    dsesim      = world.start('DSESim', 
                              eid_prefix='Estimator_',
                              verbose = 0)


    pktnetsim = world.start( 'PktNetSim',
        model_name    = 'TransporterModel',
        eid_prefix    = 'Transp_',
        adjmat_file   = ADJMAT_FILE, 
        coords_file   = COORDS_FILE, 
        appcon_file   = DEVS_FILE,
        linkRate      = "1024Kbps",
        linkDelay     = "1ms",
        linkErrorRate = "0.0001",
        start_time    = 0,
        stop_time     = END_TIME,
        random_seed   = args.random_seed,        
        verbose       = 0,
        tcpOrUdp      = "tcp", # transport layer protocols: tcp/udp (udp only for single client)
        network       = "P2P" # network architecture: P2P/CSMA/P2Pv6/CSMAv6 (supported architectures)
    )



    #---
    #--- Simulators Instances configuration
    #---

    #--- Phasor instances
    phasors = []
    for key in devParams.keys():
        if (devParams[key]['device'] == 'phasor'):
            created_phasor = False
            for phasor in phasors:
                phasor_instance = 'Phasor_' + devParams[key]['src'] + '_' + devParams[key]['idt']
                if (phasor_instance == phasor.eid):
                    created_phasor = True            
            if not created_phasor:
                phasors.append(pflowsim.Phasor(
                                 cktTerminal = devParams[key]['cktTerminal'],
                                 cktPhase = devParams[key]['cktPhase'],
                                 idt = devParams[key]['src'] + '_' + devParams[key]['idt'], 
                                 step_size = devParams[key]['step_size'],  
                                 cktElement = devParams[key]['cktElement'], 
                                 error = devParams[key]['error'], 
                                 verbose = 0))                   

    #--- SmartMeter instance
    smartmeters = []
    for key in devParams.keys():
        if (devParams[key]['device'] == 'smartmeter'):
            created_smartmeter = False
            for smartmeter in smartmeters:
                smartmeter_instance = 'Smartmeter_' + devParams[key]['src']
                if (smartmeter_instance == smartmeter.eid):
                    created_smartmeter = True            
            if not created_smartmeter:
                smartmeters.append(pflowsim.Smartmeter(
                                 cktTerminal = devParams[key]['cktTerminal'],
                                 cktPhase = devParams[key]['cktPhase'],
                                 idt = devParams[key]['src'] + '_' + devParams[key]['idt'], 
                                 step_size = devParams[key]['step_size'],  
                                 cktElement = devParams[key]['cktElement'], 
                                 error = devParams[key]['error'], 
                                 verbose = 0))  


    #--- Transporter instances (Pktnet)
    transporters = []
    for key in devParams.keys():
        client = devParams[key]['src']
        server = devParams[key]['dst']
        # Why same source or destination? I do not know.
        # Ans: To test, not exactly feasible or realistic
        if (client == server):  continue
        created_transporter = False       
        for transporter in transporters:
            transporter_instance = 'Transp_' + str(client) + '-' + str(server)
            if (transporter_instance == transporter.eid):
                created_transporter = True            
        if not created_transporter:
            transporters.append(pktnetsim.Transporter(src=client, dst=server))  


    #--- DSE instance
    estimator = dsesim.Estimator(idt = 1, 
                                 ymat_file = 'config/IEEE33_YMatrix.npy', 
                                 devs_file = DEVS_FILE,
                                 acc_period = 100, 
                                 max_iter = 5, 
                                 threshold = 0.001,
                                 baseS = 100e3/3,            # single phase power base
                                 baseV = 12.66e3/np.sqrt(3),
                                 baseNode = 1,               # single phase voltage base
                                 basePF = 0.99,
                                 se_period = 1000, # state estimation period in ms
                                 pseudo_loads = 'config/loadPseudo.mat',
                                 se_result = 'wls_results.mat' # save the wls results
                                 )


    #--- Monitor instances
    monitor = collector.Monitor()

    #---
    #--- Simulators interconnections
    #---
    
    #--- Phasor to DSE
#     mosaik.util.connect_many_to_one(world, phasors, estimator, 'v', 't')
#     for phasor in phasors:
#         print('Connect', phasor.eid, 'to', estimator.sid)    
        
    #--- Phasor to PktNet(Transporter)
    for key in devParams.keys():
        client = devParams[key]['src']
        server = devParams[key]['dst']
        device   = devParams[key]['device']
        if (device == 'phasor'):
            phasor_instance = 'Phasor_' + devParams[key]['src'] + '_' + devParams[key]['idt']     
            transporter_instance = 'Transp_' + str(client) + '-' + str(server)              
            for phasor in phasors:
                if (phasor_instance == phasor.eid):
                    for transporter in transporters:
                        if (transporter_instance == transporter.eid):
                            world.connect(phasor, transporter, 'v', 't')
                            #print('Connect', phasor.eid, 'to', transporter.eid)       
   
    #--- Smartmeter to DSE
#     mosaik.util.connect_many_to_one(world, smartmeters, estimator, 'v', 't')
#     for smartmeter in smartmeters:
#         print('Connect', smartmeter.eid, 'to', estimator.sid)  

    #--- Smartmeter to PktNet(Transporter)
    for key in devParams.keys():
        client = devParams[key]['src']
        server = devParams[key]['dst']
        device   = devParams[key]['device']
        if (device == 'smartmeter'):
            smartmeter_instance = 'Smartmeter_' + devParams[key]['src'] + '_' + devParams[key]['idt']     
            transporter_instance = 'Transp_' + str(client) + '-' + str(server)              
            for smartmeter in smartmeters:
                if (smartmeter_instance == smartmeter.eid):
                    for transporter in transporters:
                        if (transporter_instance == transporter.eid):
                            world.connect(smartmeter, transporter, 'v', 't')
                            #print('Connect', smartmeter.eid, 'to', transporter.eid) 


    #--- PktNet(Transporter) to DSE
    created_estimator_conn = [] 
    for key in devParams.keys():
        client = devParams[key]['src']
        server = devParams[key]['dst']
        device = devParams[key]['device']  
        if (device == 'phasor' or device == 'smartmeter'):    
            transporter_instance = 'Transp_' + str(client) + '-' + str(server)   
            if transporter_instance not in created_estimator_conn:
                for transporter in transporters:
                    if (transporter_instance == transporter.eid):
                        created_estimator_conn.append(transporter_instance) 
                        world.connect(transporter, estimator, 'v', 't')
                        #print('Connect', transporter.eid, 'to', estimator.eid)    

           
    #--- Phasor to Monitor
    mosaik.util.connect_many_to_one(world, phasors, monitor, 'v', 't')
    #for phasor in phasors:
        #print('Connect', phasor.eid, 'to', monitor.sid)      
 
    #--- Smartmeter to Monitor
    mosaik.util.connect_many_to_one(world, smartmeters, monitor, 'v', 't')
    #for smartmeter in smartmeters:
        #print('Connect', smartmeter.eid, 'to', monitor.sid)   
 
    #--- DSE to Monitor
    world.connect(estimator, monitor, 'v', 't')
 
if __name__ == '__main__':
    sim_start_time = datetime.now()

    # Run the simulation.
    main()

    delta_sim_time = datetime.now() - sim_start_time
    print( 'simulation took {} seconds'.format( delta_sim_time.total_seconds() ) )  
    
    
