#!/bin/bash

echo "Updating apt"
sudo apt-get update --fix-missing

echo "Installing requirements"
sudo apt install libjsoncpp-dev -y
sudo apt install g++ -y
sudo apt install python-setuptools -y
sudo apt install python3-setuptools -y
sudo apt install mercurial -y
sudo apt install python3-virtualenv -y
sudo apt install python3-pip -y
sudo apt install make -y

echo "Downloading NS-3"
if test -f ns-allinone-3.33.tar.bz2
then
	echo "File ns-allinone-3.33.tar.bz2 already exists!"
else	wget https://www.nsnam.org/releases/ns-allinone-3.33.tar.bz2
fi

echo "Extracting NS-3"
tar xjf ns-allinone-3.33.tar.bz2

echo "Copying additionals files into NS-3"
cp SmartGridSimulator/smartgrid-default-simulator-impl.* ns-allinone-3.33/ns-3.33/src/core/model/
cp tcp-server-and-client/include/* ns-allinone-3.33/ns-3.33/src/applications/model/
cp tcp-server-and-client/src/* ns-allinone-3.33/ns-3.33/src/applications/model/
cp udp-server-client/include/* ns-allinone-3.33/ns-3.33/src/applications/model/
cp udp-server-client/src/* ns-allinone-3.33/ns-3.33/src/applications/model/

echo "Copying modified wscripts into NS-3"
cp wscripts/wscript_applications ns-allinone-3.33/ns-3.33/src/applications/wscript
cp wscripts/wscript_core ns-allinone-3.33/ns-3.33/src/core/wscript

echo "Building NS-3"
cd ns-allinone-3.33/ns-3.33

./waf configure --build-profile=optimized
# ./waf configure --build-profile=debug
./waf

echo "Building NS3Mosaik"
cd ../../NS3Mosaik
make

echo "Creating virtual env"
cd ../../
mkdir virtualenv
virtualenv -p /usr/bin/python3 virtualenv/cosimul
source virtualenv/cosimul/bin/activate
pip install mosaik
pip install tables
pip install scipy
pip install matplotlib
pip install pandas
pip install co_sim_platform/opendssdirect3.7
