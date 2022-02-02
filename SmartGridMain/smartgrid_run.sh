#!/bin/bash

#---
# Script to run tapcontrol application
#---

BASE_DIR="../.."

VIRTENV=$BASE_DIR/virtualenv/cosimul
SGEXEC=$BASE_DIR/co_sim_platform/SmartGridMain

#--- set python environment
source $VIRTENV/bin/activate
export PYTHONPATH=$PYTHONPATH:$BASE_DIR:$BASE_DIR/co_sim_platform/OpenDSS

#--- run mosaik script
python $SGEXEC/simulator_demo.py
#--- for python debug run using PDB
# python -m pdb $SGEXEC/simulator_demo.py

#--- run post analysis script
python $SGEXEC/simulator_analysis.py

#--- deactivate virtual environment
deactivate

