'''
Created on Jun. 01, 2019
Mosaik script to initialize, interconnect and manage simulators

@file    simulator_demo.py
@author  Evandro de Souza, Amrinder S. Grewal
@date    2019.06.01  
@version 0.1
@company University of Alberta - Computing Science
'''

import os
import sys
import csv
import mosaik
import argparse
from datetime import datetime
from pathlib import Path

#--- Base Directory
BASE_DIR = os.getcwd()
BASE_DIR = str((Path(BASE_DIR)).parent) + "/"

#--- OpenDSS warp scripts directory
DSS_EXE_PATH = BASE_DIR + 'SmartGridMain/'

#--- Path relative to OpenDSS scripts directory 
# IEEE13
TOPO_RPATH_FILE = 'IEEE13/IEEE13Nodeckt.dss'
NWL_RPATH_FILE  = 'IEEE13/IEEE13Nodeckt_NodeWithLoad.csv'
ILPQ_RPATH_FILE = 'IEEE13/IEEE13Nodeckt_InelasticLoadPQ.csv'
DEVS_RPATH_FILE = 'IEEE13/IEEE13_Devices.csv'
# IEEE33
# TOPO_RPATH_FILE = 'IEEE33/master33Full.dss'
# NWL_RPATH_FILE  = 'IEEE33/IEEE33_NodeWithLoadFull.csv'
# ILPQ_RPATH_FILE = 'IEEE33/IEEE33_InelasticLoadPQ.csv'
# ACTS_RPATH_FILE = 'IEEE33/IEEE33_Nodeckt_Actives_Tap.csv'

#--- NS3 executables and library directory
NS3_EXE_PATH = BASE_DIR + 'NS3Mosaik'
NS3_LIB_PATH = BASE_DIR + 'ns-allinone-3.33/ns-3.33/build/lib'

#--- Paths relative to NS3 exec program directory
# IEEE13
ADJMAT_RPATH_FILE = DSS_EXE_PATH + 'IEEE13/IEEE13Node-adjacency_matrix.txt'
COORDS_RPATH_FILE = DSS_EXE_PATH + 'IEEE13/IEEE13Node_BusXY.csv'
# IEEE33
# ADJMAT_RPATH_FILE   = DSS_EXE_PATH + 'IEEE33/IEEE33_AdjMatrixFull.txt'
# COORDS_RPATH_FILE   = DSS_EXE_PATH + 'IEEE33/IEEE33_BusXYFull.csv'
# APPCON_RPATH_FILE   = DSS_EXE_PATH + 'IEEE33/IEEE33_NodeAppConnections_Tap.csv'

#--- Application config path
# IEEE13
# IEEE33
# APPCON_FILE = DSS_EXE_PATH + 'IEEE33/IEEE33_NodeAppConnections_Tap.csv'


#--- Simulators configuration
SIM_CONFIG = {
    'Collector': {
        'python': 'simulator_collector:Collector',
    },
    'ControlSim': {
        'python': 'simulator_controltap:ControlSim',       
    },
    'PFlowSim': {
        'python': 'simulator_pflow:PFlowSim',
    },
     'PktNetSim': {
          'cmd': NS3_EXE_PATH + '/NS3MosaikSim %(addr)s',
          'cwd': Path( os.path.abspath( os.path.dirname( NS3_EXE_PATH ) ) ),
          'env': {
                   'LD_LIBRARY_PATH': NS3_LIB_PATH,
                   'NS_LOG': "SmartgridNs3Main=all",
          }
    },
}

#--- Simulation total time
END_TIME =  10000	#  10 secs

#--- Application connection links
appconLinks = {}

#--- Sensors and actuators parameters
devParams = {}

#--- Mosaik Configuration
MOSAIK_CONFIG = {
    'execution_graph': False,
    'sim_progress': None,
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
                if(len(rows) == 11):
                    instance = rows[0] + "_" +  rows[1] + "-" + rows[2] \
                                + '.' + rows[3] + '.' + rows[4]
                    devParams[instance] = {}
                    devParams[instance]['device']      = rows[0]
                    devParams[instance]['src']         = rows[1]
                    devParams[instance]['dst']         = rows[2]
                    devParams[instance]['cidx']        = rows[3]
                    devParams[instance]['didx']        = rows[4]
                    devParams[instance]['period']      = rows[5]
                    devParams[instance]['error']       = rows[6]
                    devParams[instance]['cktElement']  = rows[7]
                    devParams[instance]['cktTerminal'] = rows[8]
                    devParams[instance]['cktPhase']    = rows[9]
                    devParams[instance]['cktProperty'] = rows[10] 

def readActives(actives_tap):

    global activesTap

    current_directory = os.path.dirname(os.path.realpath(__file__))
    pathToFile = os.path.abspath(
        os.path.join(current_directory, actives_tap)
    )
    if not os.path.isfile(pathToFile):
        print('File does not exist: ' + pathToFile)
        sys.exit()
    else:
        with open(pathToFile, 'r') as csvFile:
            csvobj = csv.reader(csvFile)
            activesTap = {(rows[0], rows[1], rows[2], rows[3], rows[4]) for rows in csvobj}
        csvFile.close()

def main():
    #--- Process input arguments
    parser = argparse.ArgumentParser(description='Run Smartgrid simulation')
    parser.add_argument( '--devs_file', type=str, help='devices connections file', default = DEVS_RPATH_FILE )
    parser.add_argument( '--random_seed', type=int, help='ns-3 random generator seed', default=1 )
    args = parser.parse_args()
    print( 'Starting simulation with args: {0}'.format( vars( args ) ) )
    
    readDevices(args.devs_file)
    world = mosaik.World( sim_config=SIM_CONFIG, mosaik_config=MOSAIK_CONFIG, debug=False )
    create_scenario( world, args )
    
    world.run( until=END_TIME )


def  create_scenario( world, args ):
    #---
    #--- Simulators configuration
    #---

    pflowsim    = world.start('PFlowSim',
                              topofile = DSS_EXE_PATH + TOPO_RPATH_FILE,
                              nwlfile  = DSS_EXE_PATH + NWL_RPATH_FILE,
                              ilpqfile = DSS_EXE_PATH + ILPQ_RPATH_FILE,
                              step_size = 100,
                              loadgen_interval = 80,
                              verbose = 0)    

    pktnetsim = world.start( 'PktNetSim',
        model_name      = 'TransporterModel',
        adjmat_file     = ADJMAT_RPATH_FILE,
        coords_file     = COORDS_RPATH_FILE,
        devs_file       = DEVS_RPATH_FILE,
        linkRate        = "512Kbps",
        linkDelay       = "15ms",
        linkErrorRate   = "0.0001",
        start_time      = 0,
        stop_time       = END_TIME,
        random_seed     = args.random_seed,
        verbose         = 0,
        tcpOrUdp        = "tcp", # transport layer protocols: tcp/udp
        # network architecture: P2P/CSMA/P2Pv6/CSMAv6 (supported backbone architectures)
        # When P2Pv6 or CSMAv6 is selected, secondary network is automatically fitted with
        # LR-WPAN and 6LoWPAN (make the distance between two nodes is set accordingly)
        network         = "P2P"
    )
  
    controlsim  = world.start('ControlSim', verbose = 0)
    
    collector   = world.start('Collector',
                              eid_prefix='Collector_',
                              verbose = 0,
                              out_list = False,
                              h5_save = True,
                              h5_panelname = 'Collector',
                              h5_storename='CollectorStore.hd5')

 
    #---
    #--- Simulators Instances configuration
    #---

    # Declaring instance lists
    sensors = []
    controllers = []
    actuators = []
    transporters = []
    for key in devParams.keys():
        #--- Sensor instances
        device          = devParams[key]['device']
        client          = devParams[key]['src']
        server          = devParams[key]['dst']
        control_loop    = devParams[key]['cidx']
        namespace       = devParams[key]['didx']
        if (device == 'Sensor'):
            sensor_instance = device + '_' + client + '-' + server \
                                + '.' + control_loop + '.' + namespace
            created_sensor = False
            for sensor in sensors:
                if (sensor_instance == sensor.eid):
                    created_sensor = True
            if not created_sensor:
                sensors.append(pflowsim.Sensor(
                                cktTerminal = devParams[key]['cktTerminal'],
                                cktPhase = devParams[key]['cktPhase'],
                                eid =  sensor_instance,
                                step_size = devParams[key]['period'],
                                cktElement = devParams[key]['cktElement'], 
                                error = devParams[key]['error'],
                                verbose = 0))
      
        #--- Controller and Actuator instances for tap control
        elif (device == 'Actuator'):
            # Ignore namespace as one control loop has only one controller/actuator
            controller_instance = 'Control_' + client + '-' + server \
                                + '.' + control_loop
            created_control = False
            for controller in controllers:
                if (controller_instance == controller.eid):
                    created_control = True
            if not created_control:
                controllers.append(
                    controlsim.RangeControl(
                        eid      = controller_instance,
                        vset    = 2178,
                        bw      = 13.6125,
                        tdelay  = 60,
                        control_delay = devParams[key]['period']))
            created_actuator = False
            actuator_instance = 'Actuator_' + server \
                                + '.' + control_loop
            for actuator in actuators:
                if (actuator_instance == actuator.eid):
                    created_actuator = True
            if not created_actuator:
                actuators.append(pflowsim.Actuator(
                                    cktTerminal = devParams[key]['cktTerminal'],
                                    cktPhase = devParams[key]['cktPhase'],
                                    eid = actuator_instance,
                                    step_size = devParams[key]['period'],
                                    cktElement = devParams[key]['cktElement'], 
                                    error = devParams[key]['error'],
                                    verbose=0))

        #--- Transporter instances (Pktnet)
        created_transporter = False
        if (device == 'Actuator'):
            transporter_instance = 'Transp_' + client + '-' + server \
                                    + '.' + control_loop
        else:
            transporter_instance = 'Transp_' + client + '-' + server \
                                    + '.' + control_loop + '.' + namespace
        for transporter in transporters:
            if (transporter_instance == transporter.eid):
                created_transporter = True            
        if not created_transporter:
            transporters.append(pktnetsim.Transporter(
                                src=client,
                                dst=server,
                                eid=transporter_instance))

    #--- Monitor instances
    monitor = collector.Monitor()

    #--- Prober instances
    probers = []

    # probers.append(pflowsim.Prober(idt = "611-V3",   step_size = global_step_size, verbose = 0))
    # probers.append(pflowsim.Prober(idt = "650-T3",   step_size = global_step_size, verbose = 0))      
    # probers.append(pflowsim.Prober(idt = "611-Load", step_size = global_step_size, verbose = 0))
    # probers.append(pflowsim.Prober(idt = "650-VPu3", step_size = global_step_size, verbose = 0))

    # probers.append(pflowsim.Prober(idt = "33101-V1",   step_size = global_step_size, verbose = 0))
    # probers.append(pflowsim.Prober(idt = "33101-Load", step_size = global_step_size, verbose = 0))
    # probers.append(pflowsim.Prober(idt = "33080-V1",   step_size = global_step_size, verbose = 0))
    # probers.append(pflowsim.Prober(idt = "33080-Load", step_size = global_step_size, verbose = 0))
    

    #---
    #--- Simulators interconnections
    #---
    
    for key in devParams.keys():
        device          = devParams[key]['device']
        client          = devParams[key]['src']
        server          = devParams[key]['dst']
        control_loop    = devParams[key]['cidx']
        namespace       = devParams[key]['didx']

        #--- Sensor to PktNet(Transporter)
        if (device == 'Sensor'):
            sensor_instance      = device + '_' + client + '-' + server \
                                    + '.' + control_loop + '.' + namespace
            transporter_instance = 'Transp_' + client + '-' + server \
                                    + '.' + control_loop + '.' + namespace
            for sensor in sensors:
                if (sensor_instance == sensor.eid):
                    for transporter in transporters:
                        if (transporter_instance == transporter.eid):
                            world.connect(sensor, transporter, 'v', 't')
                            print('Connect', sensor.eid, 'to', transporter.eid)                        
        
        elif (device == 'Actuator'):
            controller_instance  = 'Control_' + client + '-' + server \
                                    + '.' + control_loop
            actuator_instance = 'Actuator_' + server + '.' + control_loop
            transporter_instance = 'Transp_' + client + '-' + server \
                                    + '.' + control_loop

            #--- Controller to PktNet
            for controller in controllers:
                if (controller_instance == controller.eid):
                    for transporter in transporters:
                        if (transporter_instance == transporter.eid):
                            world.connect(controller, transporter, 'v', 't',
                                weak=True, initial_data={'v': None, 't': None})
                            print('Connect', controller.eid, 'to', transporter.eid)
        
            #--- PktNet(Transporter) to Actuator           
            for actuator in actuators:
                if (actuator_instance == actuator.eid):
                    for transporter in transporters:
                        if (transporter_instance == transporter.eid):
                            world.connect(transporter, actuator, 'v', 't',
                                weak=True, initial_data={'v': None, 't': None})
                            print('Connect', transporter.eid, 'to', actuator.eid)

            #--- PktNet(Transporter) to Controller
            #--- Find the transporter that needs to connect to this controller
            for controller in controllers:
                if (controller_instance == controller.eid):
                    for transporter in transporters:
                        # Find server and control loop of transporter
                        t_server = transporter.eid
                        t_control_loop = transporter.eid
                        t_server = t_server.split('_', 1)[1]
                        t_server = t_server.split('-', 1)[1]
                        t_server = t_server.split('.', 1)[0]
                        t_control_loop = t_control_loop.split('.')[1]
                        # print(transporter.eid, " Server: ", t_server, " Control Loop: ", t_control_loop)
                        if (t_server == client and t_control_loop == control_loop):
                            world.connect(transporter, controller, 'v', 't')
                            print('Connect', transporter.eid, 'to', controller.eid)
 
    #--- Sensor to Controller
#     for client, server, role in appconLinks:
#         if (role == 'sensing'):
#             for sensor in sensors:
#                 sensor_instance = 'Sensor_' + str(client)
#                 if (sensor_instance == sensor.eid):
#                     for controller in controllers:
#                         controller_instance = 'Control_' + str(server)
#                         if (controller_instance == controller.eid):
#                             world.connect(sensor, controller, 'v', 't')
#                             print('Connect', sensor.eid, 'to', controller.eid)
   

    #--- Controller to Actuator
#     for client, server, role in appconLinks:
#         if (role == 'acting'):
#             for controller in controllers:
#                 controller_instance = 'Control_' + str(client)
#                 if (controller_instance == controller.eid):
#                     for actuator in actuators:
#                         actuator_instance = 'Actuator_' + str(server)
#                         if (actuator_instance == actuator.eid):                        
#                             print('Connect', controller.eid, 'to', actuator.eid)                           
#                             world.connect(controller, actuator, 'v', 't', 
#                                 time_shifted=True, initial_data={'v': None, 't': None})


    #---
    #--- Simulators to Monitor
    #---

    #--- Sensor to Monitor
    mosaik.util.connect_many_to_one(world, sensors, monitor, 'v', 't')
    for sensor in sensors:
        print('Connect', sensor.eid, 'to', monitor.sid)

    #--- PktNet(Transporter) to Monitor
#     mosaik.util.connect_many_to_one(world, transporters, monitor, 'v', 't')
#     for transporter in transporters:    
#         print('Connect', transporter.eid, 'to', monitor.sid)

    #--- Controller to Monitor
    mosaik.util.connect_many_to_one(world, controllers, monitor, 'v', 't')
    for controller in controllers:
        print('Connect', controller.eid, 'to', monitor.sid)

    #--- Actuator to Monitor
    mosaik.util.connect_many_to_one(world, actuators, monitor, 'v', 't')
    for actuator in actuators:
        print('Connect', actuator.eid, 'to', monitor.sid)
        
    #--- Prober to Monitor
    mosaik.util.connect_many_to_one(world, probers, monitor, 'v', 't')
    for prober in probers:
        print('Connect', prober.eid, 'to', monitor.sid)    
        

if __name__ == '__main__':
    sim_start_time = datetime.now()

    # Run the simulation.
    main()

    delta_sim_time = datetime.now() - sim_start_time
    print( 'simulation took {} seconds'.format( delta_sim_time.total_seconds() ) )
