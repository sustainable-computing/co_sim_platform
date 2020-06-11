#!/bin/bash

#---
# Script to run tapcontrol application
#---

BASE_DIR="/mnt/hgfs/cosimul"

VIRTENV=$BASE_DIR/virtualenv/cosimul
SGEXEC=$BASE_DIR/CoSimul_Platform/TapControl


#--- set python environment
source $VIRTENV/bin/activate
export PYTHONPATH=$PYTHONPATH:$BASE_DIR:$BASE_DIR/CoSimul_Platform/OpenDSS

#--- run mosaik script
python $SGEXEC/tapcontrol/simulator_demo.py

#--- run post analysis script
python $SGEXEC/tapcontrol/simulator_analysis.py

#--- deactivate virtual environment
deactivate

