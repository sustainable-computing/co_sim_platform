#!/bin/bash

#---
# Script to run SimDSE application
#---

BASE_DIR="../.."

VIRTENV=$BASE_DIR/virtualenv/cosimul
SGEXEC=$BASE_DIR/co_sim_platform/SimDSE

#--- set python environment
source $VIRTENV/bin/activate
export PYTHONPATH=$PYTHONPATH:$BASE_DIR:$BASE_DIR/co_sim_platform/OpenDSS

#--- run mosaik script
python $SGEXEC/simulator_masterFull.py
#--- for python debug run using PDB
# python -m pdb $SGEXEC/simulator_masterFull.py

#--- run post analysis script
python $SGEXEC/analysisFull.py

#--- deactivate virtual environment
deactivate

