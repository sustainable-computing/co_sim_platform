# Smartgrid Cosimulation Platform
Smartgrid Cosimulation Platform is a project meant to couple together multiple simulators that are simulating different
parts of a smartgrid to allow the study of dynamics in a complex multi-domain system. Currently, 
[NS-3](https://www.nsnam.org/) is being used to simulate network activity between nodes and
[OpenDSS](https://smartgrid.epri.com/SimulationTool.aspx) is being used to simulate power flow. To 
coordinate the different simulators, the [Mosaik co-simulation framework](https://mosaik.offis.de/) is being used.

TapControl is working example that can be used to observe the simulator at work. It uses the IEEE13 to simulate power 
flow and network activity between sensors and actors. Communication between nodes can be performed using TCP or UDP over
point to point links. 

## Requirements
* This project is being developed on linux, it has been tested on the following:
    * Ubuntu 18.04 LTS
    * Ubuntu 20.04 LTS
* The following python versions have been used to develop the co-simulator:
    * 3.6.8
    * 3.8.2
* Hardware Requirements:
    * 8.0 GB or more to build NS-3

The simulator might run on other operating systems and with other python versions, but this has not been tested.

## Installation
1. Create project directory
    
    ``` 
       > mkdir cosimul
       > cd cosimul 
    ```

2. Clone repository
    ``` 
       > git clone https://github.com/sustainable-computing/co_sim_platform
    ```

3. Run Script
    ``` 
       > cd co_sim_platform
       > ./install.sh
    ```

## Components used:
* [Mosaik co-simulation framework](https://mosaik.offis.de/)
* [OpenDSS](https://smartgrid.epri.com/SimulationTool.aspx)
* [NS-3](https://www.nsnam.org/)

## Acknowledgments
As a part of the University of Alberta Future Energy Systems (FES), this
research was made possible in part thanks to funding from the Canada First
Research Excellence Fund (CFREF).

Advisors:
* Dr. Ardakanian
* Dr. Nikolaidis

Developers:

* Evandro de Souza
* Amrinder S. Grewal

### Citing the Co-simulation Platform
```Bibtex
@INPROCEEDINGS{9149212,  
author={E. {de Souza} and O. {Ardakanian} and I. {Nikolaidis}},  
booktitle={ICC 2020 - 2020 IEEE International Conference on Communications (ICC)},   
title={A Co-simulation Platform for Evaluating Cyber Security and Control Applications in the Smart Grid},   
year={2020},
pages={1-7},}
```

Last Modification: 2020-09-08
