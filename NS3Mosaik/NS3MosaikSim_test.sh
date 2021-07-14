#---
# Script for test of NS3MosaikSim
#---

LD_LIBRARY_PATH=../ns-allinone-3.33/ns-3.33/build/lib
NS_LOG="SmartgridDefaultSimulatorImpl=all"

LD_LIBRARY_PATH=$LD_LIBRARY_PATH NS_LOG=$NS_LOG NS3MosaikSim 127.0.0.1:5050
