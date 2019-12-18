#!/bin/bash

#---
# Script to run tapcontrol application
#---

BASE_DIR=".."

VIRTENV=$BASE_DIR/virtualenv/cosimul
SGEXEC=$BASE_DIR/SimDSE

#--- set python environment
source $VIRTENV/bin/activate
export PYTHONPATH=$PYTHONPATH:$BASE_DIR:$BASE_DIR/OpenDSS

#--- run mosaik script
python $SGEXEC/simulator_masterFull.py

#--- run post analysis script
python $SGEXEC/analysisFull.py

#--- deactivate virtual environment
deactivate

