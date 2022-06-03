# Distributed State Estimator application



## Table of Contents

| File           | Content                                                                                                            |
|----------------|:-------------------------------------------------------------------------------------------------------------------|
| SimDSE/simulator_master.py     | Master simulation script. Configure HV-only scenario |
| SimDSE/simulator_masterFull.py | Master simulation script. Configure HV-LV scenario |
| SimDSE/simulator_pflow.py      | Mosaik integration to include OpenDSS simulator |
| SimDSE/simulator_dse.py        | State estimator script |
| SimDSE/analysis.py             | Graph generator for HV-only scenario |
| SimDSE/analysisFull.py         | Graph generator for HV-LV scenario |
| SimDSE/simdse_run.sh           | Bash script to run scenario |
| SimDSE/config                  | Directory with configuration files |
| SimDSE/data                    | Directory with simulation results and graphs |
| SimDSE/aux                     | Directory with config generation scripts |



## Running the tests

* Do not forget to change "BASE_DIR" in scripts

> cd *PATH-TO-PROJECT-ROOT*/SimDSE

> ./simdse_run.sh (for small size HV network)

* A new generated picture should be create as 'Monitor_Small.png' in *data* directory.


### Configuration Files

* These are the programs/scripts that use configuration files.


```
simulator_master.py
	config/IEEE33_DevicesFull.csv

simulator_pflow.py
	config/master33Full.dss
	config/IEEE33_NodeWithLoadFull.csv  
	config/IEEE33_BusXYFull.csv
	config/IEEE33_DevicesFull.csv

OpenDSS
	config/master33Full.dss
	config/lineData33Full.dss
	config/loadData33Full.dss
	config/transData33Full.dss
	config/IEEE33_BusXYFull.csv

NS3
	config/IEEE33_AdjMatrixFull.txt
	config/IEEE33_BusXYFull.csv
	config/IEEE33_DevicesFull.csv


simulator_dse.py
	config/IEEE33YMatrys.npy
	config/IEEE33_DevicesFull.csv

```

#### Description

**IEEE33_Devices.csv**

Main devices configuration file. It is composed of the following fields:
* _idn:_ unique identifier for the device
* _type:_ type of device according to the categories in Sensor.py (phasor, smartmeter, prober)
* _src:_ communication node which the device is connected
*	_dst:_ communication destination node where to send information
*	_period:_ number of Mosaik ticks between sending information
*	_error:_ used by Sensor.py to include some error in the reading
*	_cktElement:_ OpenDSS circuit element to collect data
*	_cktTerminal:_ OpenDSS circuit terminal of the cktElement to collect data
*	_cktPhase:_ OpenDSS circuit phase of the cktElement to collect data
*	_cktProperty:_ In the case of a Prober, it is necessary to say which property what to collect (V, I). Otherwise, use "None"



**IEEE33_NodeWithLoad.csv**

Composed of two fields:
"circuit_node, number_of_loads"
- It uses the name defined in OpenDSS and express how many loads will be connected in
a specific phase. It is later used in LoadGen.py to generate an equivalent
amount of load for the node.



**master33.dss**

- OpenDSS main configuration file, which calls the additional OpenDSS configuration files.
- It include HV IEEE33 circuit and European Low Voltage Test Feeder


**IEEE33_AdjMatrix.txt**

- Communication network adjacency matrix to define network topology.
- The sequence of elements is the same defined in IEEE33_NodeWithLoad.csv



### Changing Configuration
1. *Add a new device*
	* add connection in IEEE33_Devices.csv
	* It must be an existing element on OpenDSS with same name. Source and destination must also exist.
	* More than one device can be added in a circuit position, but it should have different "idn".
2. *Different simulation*
	*  simdse_runFull.sh calls simulator_masterFull.py with different parameters and number of devices.


## Credits
As a part of the University of Alberta Future Energy Systems (FES), this
research was made possible in part thanks to funding from the Canada First
Research Excellence Fund (CFREF).


## References
1. http://smartgrid.epri.com/SimulationTool.aspx
2. https://www.nsnam.org/
3. https://mosaik.offis.de/
4. https://www.python.org


> Last Modification: 2019-12-18
