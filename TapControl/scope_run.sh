#!/bin/bash

#---
# Script to run tapcontrol application
#---

BASE_DIR=".."

VIRTENV=$BASE_DIR/virtualenv/cosimul
SGEXEC=$BASE_DIR/TapControl

#--- set python environment
source $VIRTENV/bin/activate
export PYTHONPATH=$PYTHONPATH:$BASE_DIR:$BASE_DIR/OpenDSS

#--- run mosaik script
python $SGEXEC/tapcontrol/simulator_scope.py

#--- deactivate virtual environment
deactivate

