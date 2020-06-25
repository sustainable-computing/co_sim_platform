# Smartgrid Cosimulation Platform
## Table of Contents

| Directory       | Content                                                              |
|:----------------|:---------------------------------------------------------------------|
| *NS3Mosaik*     | NS3Mosaik interface and NS3 communication model code                 |
| *ns-allinone*   | NS3 simulator                                                        |
| *OpenDSS*       | Python classes interfacing OpenDSS simulator                         |
| *SimDSE*        | Distributed state estimator application                              |
| *SmartgridSimulator* | NS3 simulation core class modification                           |
| *TapControl*    | Voltage control application                                          |

## File Description
### NS3-Mosaik API
| File           | Content                                                                |
|----------------|:-------------------------------------------------------------------------------------------------------------------|
| NS3Mosaik/Makefile       | NS3 script and middleware compilation         |
| NS3Mosaik/NS3MosaikSim   | binary of NS3Mosaik middleware                |
| NS3Mosaik/NS3MosaikSim_test.sh | script to test NS3Mosaik middleware after compilation |
| NS3Mosaik/mosaik_api/include/MosaikSim.h                                 | Includes for NS3-Mosaik middleware |
| NS3Mosaik/mosaik_api/include/NS3Netsim.h                                 | Includes for NS3 script for communication model |
| NS3Mosaik/mosaik_api/include/ns3-helper.h                                | Includes for Auxiliary function for MS3Mosaik middleware |
| NS3Mosaik/mosaik_api/src/main.cpp                                        | Main program to start NS3 script and middleware C++ classes |
| NS3Mosaik/mosaik_api/src/MosaikSim.cpp                                   | NS3-Mosaik middleware |
| NS3Mosaik/mosaik_api/src/ns3-helper.cpp                                  | Auxiliary function for MS3Mosaik middleware |
| NS3Mosaik/mosaik_api/src/NS3Netsim.cpp                                   | NS3 script for communication model |

### OpenDSS wrapper class and accessories
| File           | Content                                                                                                            |
|----------------|:-------------------------------------------------------------------------------------------------------------------|
| OpenDSS/CktDef.py            | Auxiliary OpenDSS defintions |
| OpenDSS/LoadGenerator.py     | Load Generator class |
| OpenDSS/SimDSS.py            | Python wrapper class for OpenDSS simulator |
| OpenDSS/examples             | Directory with some examples of OpenDSS wrapper class |
| OpenDSS/tests                | Directory with some tests scripts |

### Distributed State Estimation Application
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

### NS3 core files
| File           | Content                                                                                                            |
|----------------|:-------------------------------------------------------------------------------------------------------------------|
| SmartgridSimulator/smartgrid-default-simulator-impl.cc   | NS3 smartgrid simulator class C++ code |
| SmartgridSimulator/smartgrid-default-simulator-impl.h    | NS3 smartgrid simulator class includes |

### NS3 Application Files
| File           | Content                                                                                                            |
|----------------|:-------------------------------------------------------------------------------------------------------------------|
| tcp-server-and-client/multi-client-tcp-server.cc   | NS3 TCP server with multiple clients C++ code |
| tcp-server-and-client/multi-client-tcp-server.h   | NS3 TCP server with multiple clients includes |
| tcp-server-and-client/multi-client-tcp-server-helper.cc   | NS3 Helper for TCP server with multiple clients C++ code |
| tcp-server-and-client/multi-client-tcp-server-helper.h   | NS3 Helper for TCP server with multiple clients includes |
| tcp-server-and-client/tcp-client.cc   | NS3 TCP client C++ code |
| tcp-server-and-client/tcp-client.h   | NS3 TCP client C++ includes |
| tcp-server-and-client/tcp-client-helper.cc   | NS3 Helper for TCP client C++ code |
| tcp-server-and-client/tcp-client-helper.h   | NS3 Helper for TCP client C++ includes |
| udp-server-client/custom-udp-server.cc   | NS3 UDP server application C++ code |
| udp-server-client/custom-udp-server.h   | NS3 UDP server application includes |
| udp-server-client/custom-udp-server-helper.cc   | NS3 Helper for UDP server application C++ code |
| udp-server-client/custom-udp-server-helper.h   | NS3 Helper for UDP server application includes |
| udp-server-client/custom-udp-client.cc   | NS3 UDP client C++ code |
| udp-server-client/custom-udp-client.h   | NS3 UDP client C++ includes |
| udp-server-client/custom-udp-client-helper.cc   | NS3 Helper for UDP client C++ code |
| udp-server-client/custom-udp-client-helper.h   | NS3 Helper for UDP client C++ includes |

### Tap Control Application
| File           | Content                                                                                                            |
|----------------|:-------------------------------------------------------------------------------------------------------------------|
| /simulator_analysis.py                                    | Post simulation graph generation |
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

## Getting Started
* This project was develop in a Linux platform, and this installation procedure is based on this platform.
* Even though it is not anticipated major problems to install on Windows or Mac, adaptations in the process are required.
* Python version **3.6.8** was used during the development.
* The use of Python *virtualenv* is optional, but recommended. Running scripts use virtualenv.

### Prepare area
1. Create project directory
  > mkdir cosimul

  > cd cosimul

2. Clone repository
  > git clone https://github.com/sustainable-computing/CoSimul_Platform

### NS3

#### Prerequisites
* [g++] 7.4.0
* [jsoncpp] libjsoncpp-dev 1.7.4-3 (Ubuntu version)
* [python-setuptools] 39.0.1-2
* [python3-setuptools] 39.0.1-2
* [mercurial] 4.5.3
* [ns-3] 3.30.1

#### Installation

  > sudo apt install libjsoncpp-dev

  > sudo apt install g++

 > sudo apt install python-setuptools

 > sudo apt install python3-setuptools

 > sudo apt install mercurial

 > cd CoSimul_Platform

 > wget https://www.nsnam.org/releases/ns-allinone-3.30.1.tar.bz2

 > tar xjf ns-allinone-3.30.1.tar.bz2


* Go to the ns-3 source code and insert smartgrid simulator class and applications classes.
* It must be placed in the correct location in ns-3 source source tree.
* ns-3 configuration files must be changed too to new class be compiled.

> cd ns-allinone-3.30.1/ns-3.30.1/src/core/model
>
> cp ../../../../../SmartGridSimulator/smartgrid-default-simulator-impl.* .
>
> cd ../../applications/model
>
> cp ../../../../../tcp-server-and-client/include/\*.* .
>
> cp ../../../../../tcp-server-and-client/src/\*.* .
>
> cp ../../../../../udp-server-client/include/\*.* .
>
> cp ../../../../../udp-server-client/src/\*.* .


* Change *wscript* to include smartgrid simulator class in ns-3 compilation
* In ns-allinone-3.30.1/ns-3.30.1/src/core/model/wscript, add to core.source:
	'model/smartgrid-default-simulator-impl.cc'
* In ns-allinone-3.30.1/ns-3.30.1/src/core/model/wscript, add to headers.source:
	'model/smartgrid-default-simulator-impl.h'

* In ns-allinone-3.30.1/ns-3.30.1/src/applications/model/wscript, add to module.source:

    'model/tcp-client-helper.cc',
    
    'model/tcp-client.cc',
    
    'model/multi-client-tcp-server-helper.cc',
    
    'model/multi-client-tcp-server.cc',
    
    'model/custom-udp-client-helper.cc',
    
    'model/custom-udp-client.cc',
    
    'model/custom-udp-server-helper.cc',
    
    'model/custom-udp-server.cc',
    
* In ns-allinone-3.30.1/ns-3.30.1/src/applications/model/wscript, add to headers.source:

    'model/tcp-client-helper.h',
    
    'model/tcp-client.h',
    
    'model/multi-client-tcp-server-helper.h',
    
    'model/multi-client-tcp-server.h',
    
    'model/custom-udp-client-helper.h',
    
    'model/custom-udp-client.h',
    
    'model/custom-udp-server-helper.h',
    
    'model/custom-udp-server.h',

* Return to ns-3 top directory to compile the package, named ns-allinone-3.30.1/ns-3.30.1
* Change ns-3 configuration to optimized version.
* It may take a while to compile
> ./waf clean

> ./waf configure --build-profile=optimized

> ./waf


* Compile NS3MosaikSim and test NS3MosaikSim
> cd *PATH-TO-PROJECT-ROOT*/NS3Mosaik

> make

> ./NS3MosaikSim_test.sh

```
IEEE13Model:main argv[1]: 127.0.0.1:5050
Starting MosaikSim class with varargin: 127.0.0.1:5050
MosaikSim::openSocket
terminate called after throwing an instance of 'std::runtime_error'
  what():  MosaikSim::openSocket TCP connection failed
./NS3MosaikSim_test.sh: line 17: 22647 Aborted	(core dump) ...
```


### Python / Mosaik / OpenDSS
#### Create virtualenv and install packages
> cd <PATH-TO-PROJECT-ROOT>

> mkdir virtualenv

> virtualenv -p /usr/bin/python3 virtualenv/cosimul

> source virtualenv/cosimul/bin/activate

> pip install mosaik

> pip install OpenDSSDirect.py[extras]

> pip install tables


### List installed packages

> pip list

```
Package          Version
---------------- -------
cffi             1.13.1
cycler           0.10.0
decorator        4.4.0  
docopt           0.6.2  
dss-python       0.10.1
future           0.18.1
kiwisolver       1.1.0  
matplotlib       3.1.1  
mosaik           2.5.1  
mosaik-api       2.4    
networkx         2.4    
numpy            1.17.3
OpenDSSDirect.py 0.3.7  
pandas           0.25.2
pip              19.3.1
pkg-resources    0.0.0  
pycparser        2.19   
pyparsing        2.4.2  
python-dateutil  2.8.0  
pytz             2019.3
setuptools       41.4.0
simpy            3.0.11
simpy.io         0.2.3  
six              1.12.0
tables           3.6.0
wheel            0.33.6
```

> deactivate


## Credits
As a part of the University of Alberta Future Energy Systems (FES), this
research was made possible in part thanks to funding from the Canada First
Research Excellence Fund (CFREF).

### How to cite our paper?
```
Evandro de Souza, Omid Ardakanian, Ioanis Nikolaidis, "A Co-simulation Platform for Evaluating Cyber Security and Control Applications in the Smart Grid", Proceedings of the IEEE International Conference on Communications (ICC), 2020.
```


## References
1. http://smartgrid.epri.com/SimulationTool.aspx
2. https://www.nsnam.org/
3. https://mosaik.offis.de/
4. https://www.python.org


> Last Modification: 2019-12-18
