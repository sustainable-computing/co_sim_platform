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
python $SGEXEC/simulator_master.py
#--- for python debug run using PDB
# python -m pdb $SGEXEC/simulator_master.py

#--- run post analysis script
python $SGEXEC/analysis.py
#--- for python debug run using PDB
# python -m pdb $SGEXEC/analysis.py

#--- deactivate virtual environment
deactivate

