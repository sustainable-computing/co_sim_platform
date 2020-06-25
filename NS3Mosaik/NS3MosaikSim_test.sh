#---
# Script for test of NS3MosaikSim
#---

LD_LIBRARY_PATH=../ns-allinone-3.30.1/ns-3.30.1/build/lib
NS_LOG="SmartgridDefaultSimulatorImpl=all"

LD_LIBRARY_PATH=$LD_LIBRARY_PATH NS_LOG=$NS_LOG NS3MosaikSim 127.0.0.1:5050
