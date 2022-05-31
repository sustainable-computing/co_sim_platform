/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2019 Evandro de Souza
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author:  Evandro de Souza <evandro@ualberta.ca>
 * Date:    2019.06.03
 * Company: University of Alberta/Canada - Computing Science
 *
 * Author:  Amrinder S. Grewal <asgrewal@ualberta.ca>
 * Date:    2020.05.09
 * Company: University of Alberta/Canada - Computing Science
 */


#ifndef NS3NETSIM_H_
#define NS3NETSIM_H_

#include <iostream>
#include <iomanip>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/csma-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/log.h"
#include "ns3/sixlowpan-module.h"
#include "ns3/lr-wpan-module.h"
#include <ns3/propagation-loss-model.h>
#include <ns3/propagation-delay-model.h>
#include <ns3/single-model-spectrum-channel.h>
#include <ns3/constant-position-mobility-model.h>
#include "ns3/applications-module.h"

#include "ns3/smartgrid-default-simulator-impl.h"

#include "ns3/tcp-helper.h"
#include "ns3/custom-udp-helper.h"
#include <unordered_map>

using namespace std;
using namespace ns3;

/**
 * \brief Data exchange structure
 */
struct DataXCHG {
    string id;
    string src;
    string dst;
    string val;
    int64_t time;
};

static vector<DataXCHG> dataXchgInput;  ///< Input data exchange vector
static queue<DataXCHG> dataXchgOutput; ///< Output data exchange vector
static map<Ipv4Address, uint32_t> mapIpv4NodeId; ///< Map from client Ipv4 to Node Id
static map<Ipv6Address, uint32_t> mapIpv6NodeId; ///< Map from client Ipv6 to Node Id
static unordered_map<uint32_t , string> fragmentBuffers;

class NS3Netsim {
 public:

  /**
   * \brief Constructor NS3 scripts
   *
   * \param none
   * \returns none
   *
   */
  NS3Netsim();

  /**
   * \brief Destructor NS3 scripts
   *
   * \param none
   * \returns none
   *
   */
  virtual ~NS3Netsim();

  /**
   * \brief Initialize main NS3 parameters
   *
   * \param f_adjmat: adjacency matrix filename
   * \param f_coords: coordinates filename
   * \param f_devs: devices filename
   * \param s_linkRate: link transmission rate
   * \param s_linkDelay: link delay
   * \param s_linkErrorRate: link error rate on receiver
   * \param start_time: when the NS3 simulator should start (not used now)
   * \param stop_time: when the NS3 simulator should end
   * \param verb: level of verbose mode
   *
   * \returns None
   *
   */
  void init (string f_adjmat, string f_coords, string f_devs, string s_linkRate,
             string s_linkDelay, string s_linkErrorRate, string start_time,
             string stop_time, string verb, string s_tcpOrUdp, string s_net);

  /**
   * \brief Create Transport connection between two nodes
   *
   * \param client: source node
   * \param server: destination node
   *
   * \returns None
   *
   */
  void create (string client, string server);

  /**
   * \brief Receive data from Mosaik-NS3 middleware and schedule an event
   *
   * \param src: source node name
   * \param dst: destination node name
   * \param val: value to be transmitted through the network
   * \param val_time: time of this event given by the predecessor simulator
   *
   * \returns None
   *
   */
  void schedule (string id, string src, string dst, string val, string val_time);

  /**
   * \brief Pass the transmitted information upward to the MOSAIK-NS3 middleware
   *
   * \param id: the local transporter simulator identifier
   * (for multiplexing and demultiplexing purposes)
   * \param src: source node name
   * \param dst: destination node name
   * \param val_V: value to be transmitted through the network
   * \param val_T: time of this event when it arrives at the destination
   *
   * \returns int: return 0, if the buffer was empty, or 1 if one record was extract from the buffer
   *
   */
  int  get_data (string &id, string &src, string &dst, string &val_V, string &val_T);

  /**
   * \brief Execute NS3 simulation until the time established in the parameter
   *
   * \param time: current time according to Mosaik simulation
   *
   * \param nextStop: time until which NS3 can execute its simulation part
   *
   * \returns The forced step required or "null"
   *
   */
  std::string runUntil (uint64_t time, string nextStop);

  /**
   * \brief Check if the output buffer is empty
   *
   * \param None
   *
   * \returns boolen: True or False
   *
   */
  bool checkEmptyDataOutput (void);

  /**
   * \brief Get the number of records in the output buffer
   *
   * \param None
   *
   * \returns int: Number of records
   *
   */
  int getSizeDataOutput (void);

  /**
   * \brief Get the number of records in the input buffer
   *
   * \param None
   *
   * \returns int: Number of records
   *
   */
  int getSizeDataInput (void);


  /**
   * \brief Get the current NS3 simulation time in microseconds
   *
   * \param None
   *
   * \returns double: NS3 simulation time
   *
   */
  double getCurrentTime (void);


  //---
  //--- Variables
  //---

private:
  /**
   * Set up a tcp or udp server depending on what has been passed in.
   *
   * \param address The address that will be used to assigned addresses to both the server
   * \param tcpOrUdp a string that is either set to tcp or udp, indicating which kind of server will be created
   * \param server holds the server id
   */
  void setUpServer(AddressValue address, string protocol, string server);

  /**
   * Sets up a tcp or udp client depending on what has been passed in
   *
   * \param address The address that will be used to assigned addresses to the client
   * \param tcpOrUdp a string that is either set to tcp or udp, indicating which kind of client will be created
   * \param server holds the server id
   * \param client holds the client id
   */
  void setUpClient(AddressValue address, string protocol, string server, string client);

  vector< vector<bool>> nodeAdjMatrix; ///< Node adjacency matrix
  string nodeAdjMatrixFilename;        ///< Node adjacency matrix filename
  string nodeCoordinatesFilename;      ///< Node names and coordinates filename

  vector<vector<string>> arrayNamesCoords; ///< Array of strings with node names and coordinates
  vector<vector<double>> arrayNodeCoords;  ///< Array of doubles with node coordinates
  NodeContainer nodes;                     ///< NS3 container with simulation nodes

  PointToPointHelper pointToPoint;       ///< Pointer to pointTopoint helper class
  CsmaHelper csma;                       ///< CSMA helper class
  string LinkRate;                       ///< Uniform link data rate
  string LinkDelay;                      ///< Uniform link delay
  string LinkErrorRate;				   ///< Uniform Link error rate
  uint32_t linkCount;                    ///< Network link count
  vector<NetDeviceContainer> Devices; ///< Vector with all link devices
  map<pair<string,string>, NetDeviceContainer> DeviceMap; ///< Map from node names to devices

  InternetStackHelper internet;  ///< Pointer to Internet helper class
  Ipv4AddressHelper ipv4Address; ///< Pointer to Ipv4 Internet helper class
  Ipv6AddressHelper ipv6Address; ///< Pointer to Ipv6 Internet helper class

  MobilityHelper mobility;                      ///< Pointer to mobility (position) helper class
  Ptr<ListPositionAllocator> nodePositionAlloc; ///< Pointer to node position allocation

  string devicesFilename;              ///< Device connections filename
  vector<vector<string>> arrayAppConnections; ///< Application client-server connections vector

  vector<string> nodeServerList;  ///< Application servers vector
  vector<string>::iterator iList; ///< Application servers vector iterator
  uint16_t sinkPort;              ///< Application port for all server nodes

  TcpServerHelper tcpServerHelper = TcpServerHelper(sinkPort); ///< Application TCP server helper
  TcpClientHelper tcpClientHelper = TcpClientHelper(Address()); ///< Application TCP client helper
  CustomUdpClientHelper customUdpClientHelper = CustomUdpClientHelper(Address()); ///< Application UDP client helper
  CustomUdpServerHelper customUdpServerHelper = CustomUdpServerHelper(sinkPort); ///< Application UDP server helper

  double startTime; ///< Simulation start time
  double stopTime; ///< Simulation stop time
  int verbose;      ///< Verbose level

  map<uint32_t, Ptr<Socket>> mapNodeSocket; ///< Map from client Nodes Id to the socket

  Ptr<SmartgridDefaultSimulatorImpl> sim; ///< Pointer to the smartgrid simulator implementation

  ApplicationContainer allApplications;
  NodeContainer allNodes;

  string tcpOrUdp; ///< Which network protocol should be used
  string netArch;  ///< Which network architecture should be used
};

#endif /* NS3NETSIM_H_ */
