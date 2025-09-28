#!/bin/bash

#---
# Script to run Smart-Grid application
#---

BASE_DIR=".."

VIRTENV=$BASE_DIR/virtualenv/cosimul
SGEXEC=$BASE_DIR/SmartGridMain

#--- set python environment
source $VIRTENV/bin/activate
export PYTHONPATH=$PYTHONPATH:$BASE_DIR:$BASE_DIR/OpenDSS

#--- run mosaik script
python $SGEXEC/simulator_demo.py
#--- for python debug run using PDB
# python -m pdb $SGEXEC/simulator_demo.py

#--- run post analysis script
python $SGEXEC/simulator_analysis.py
#--- for python debug run using PDB
# python -m pdb $SGEXEC/simulator_analysis.py

#--- deactivate virtual environment
deactivate

