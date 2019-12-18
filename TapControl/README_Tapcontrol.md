# Tap Control Application

## Table of Contents

| File           | Content                                                                                                            |
|----------------|:-------------------------------------------------------------------------------------------------------------------|
| tapcontrol_run.sh | Script to run tapcontrol simulation |
| TapControl/simulator_collector.py                                   | Collector for simulation data exchange |
| TapControl/simulator_controltap.py                                  | Control model simulator including tap controller logic |
| TapControl/simulator_demo.py                                        | Main simulation integration script used by Mosaik |
| TapControl/simulator_pflow.py                                       | Mosaik integration to include OpenDSS simulator |
| TapControl/simulator_scope.py                                       | Post simulation scope analyzer |
| TapControl/data/IEEE13Node-adjacency_matrix.txt                     | NS3 topology configuration file |
| TapControl/data/IEEE13Node_AppConnections_Tap.csv                   | NS3 transport instances configuration file |
| TapControl/data/IEEE13Node_BusXY.csv                                | OpenDSS bus coordinates configuration file |
| TapControl/data/IEEE13Nodeckt_Actives_Tap.csv                       | PFlowSim instances (sensor/actuator/prober) configuration file |
| TapControl/data/IEEE13Nodeckt.dss                                   | OpenDSS main configuration file |
| TapControl/data/IEEE13Nodeckt_InelasticLoadPQ.csv                   | Initial ineslastic load for power grid model (node, P, Q) |
| TapControl/data/IEEE13Nodeckt_NodeWithLoad.csv                      | List of nodes and number of loads (node, #loads) |
| TapControl/data/IEEE13Node_coordinates.txt                          | NS3 node coordinates (x, y) |
| TapControl/data/IEEELineCodes.dss                                   | OpenDSS line codes for main OpenDSS config file |



## Running the tests

* Do not forget to change "BASE_DIR" in scripts

> cd *PATH-TO-PROJECT-ROOT*/TapControl

> ./tapcontrol_run.sh

* A new generated picture should be create as 'Monitor.png'


### Configuration Files

* These are the programs/scripts that use configuration files.
* Note that IEEE13Node_AppConnections_Tap.csv is used by two programs/scripts.

```
simulator_demo.py
	IEEE13Node_AppConnections_Tap.csv

simulator_pflow.py
	IEEE13Nodeckt.dss
	IEEE13Nodeckt_NodeWithLoad.csv  
	IEEE13Nodeckt_InelasticLoadPQ.csv  	
	IEEE13Nodeckt_Actives_Tap.csv  

OpenDSS
	IEEE13Nodeckt.dss
	IEEELineCodes.dss
	IEEE13Node_BusXY.csv

NS3
	IEEE13Node-adjacency_matrix.txt
	IEEE13Node_coordinates.txt
	IEEE13Node_AppConnections_Tap.csv

LoadGen.py
	IEEE13Nodeckt_NodeWithLoad.csv  
```

**IEEE13Node_AppConnections_Tap.csv**

It is composed of three fields:
"source, destination, function", example: "611,632,sensing"
- Used by simulator_demo.py to create instances of sensor, controller and actuator
  and connect simulator instances
- ns3 simulator uses the file to create transport layer instances


**IEEE13Nodeckt_Actives_Tap.csv**

It is composed of five fields:
"instance, function, cktElement, cktTerminal, cktPhase"
example: "Sensor_611,getV,Line.684611,RCVBUS,PHASE_3"
- Used by simulator_pflowsim to know for each simulator instance, which function
is used to obtain/insert OpenDSS information, and the parameters used in the function.
- The parameters are directly related to OpenDSS configuration names, except the last,
which uses the configuration defined in CktDef.py


**IEEE13Nodeckt_NodeWithLoad.csv**

Composed of two fields:
"circuit_node, number_of_loads"
- It uses the name defined in OpenDSS and express how many loads will be connected in
a specific phase. It is later used in LoadGen.py to generate an equivalent
amount of load for the node.


**IEEE13Nodeckt_InelasticLoadPQ.csv**

Composed of three fields:
"circuit_node, P, Q", example: "634.1, 160, 110"
- Defined the inelastic load for each circuit_node


**IEEE13Nodeckt.dss**

- OpenDSS main configuration file, which calls the additional configuration:
IEEELineCodes.dss and IEEE13Node_BusXY.csv


**IEEE13Node-adjacency_matrix.txt**

- Communication network adjacency matrix to define network topology.
The sequence of elements is the same defined in IEEE13Nodeckt_NodeWithLoad.csv


**IEEE13Node_coordinates.txt**
- Communication network node spatial position. The sequence of elements
is the same defined in IEEE13Nodeckt_NodeWithLoad.csv


### Changing Configuration
1. *Add a new sensor*
	* add connection in IEEE13Node_AppConnections_Tap.csv
	* add information about which element to be accessed and which function
	  will be called to extract the information in IEEE13Nodeckt_Actives_Tap.csv


2. *Change tap configuration*
	* Tap configuration is presented in file OpenDSS file IEEE13Nodeckt.dss


3. *Change controller configuration*
	* The controller parameters are configurated in simulator_demo.py when
	the controller instance is created:
	controllers.append(controlsim.RangeControl(idt=client, vset=2178, bw=13.6125, tdelay=40))

**Observation:**
- in the current version there are limitations of how many transport
  instances is possible to allocate in a single node


## Credits
As a part of the University of Alberta Future Energy Systems (FES), this
research was made possible in part thanks to funding from the Canada First
Research Excellence Fund (CFREF).


## References
1. http://smartgrid.epri.com/SimulationTool.aspx
2. https://www.nsnam.org/
3. https://mosaik.offis.de/
4. https://www.python.org

> Last Modification: 2019-11-18
