#---
# Script for test of NS3MosaikSim
#---

BASE_DIR="/home/evandro/DOCSHARE/Professional/CoSimulPrj/develop/cosimul"

PATH=$BASE_DIR/NS3Mosaik
LD_LIBRARY_PATH=$BASE_DIR/ns-allinone-3.30.1/ns-3.30.1/build/lib
NS_LOG="SmartgridDefaultSimulatorImpl=all"

LD_LIBRARY_PATH=$LD_LIBRARY_PATH NS_LOG=$NS_LOG $PATH/NS3MosaikSim 127.0.0.1:5050
