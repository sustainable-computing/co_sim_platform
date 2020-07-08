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
 *
 */


//--- Includes ---//
#include <cstdio>
#include <cassert>
#include <string>
#include "ns3/lr-wpan-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-apps-module.h"
#include "ns3/wifi-module.h"
#include "ns3/sixlowpan-module.h"
#include "ns3/smartgrid-default-simulator-impl.h"
#include "NS3Netsim.h"
#include "ns3-helper.h"

using namespace std;
using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("SmartgridNs3Main");
std::string fileNameReceived = "packets_received.pkt";

/**
 * \brief Parses the packet received by the an appliction/socket and adds it to the list of packets that will be sent to the upper layer.
 *
 * \param socket
 */
void
ExtractInformationFromPacketAndSendToUpperLayer (Ptr<Socket> socket)
{
  Address from;
  Ptr<Packet> packet = socket->RecvFrom (from);
  packet->RemoveAllPacketTags ();
  packet->RemoveAllByteTags ();

  Ptr<Node> recvnode = socket->GetNode();
  uint8_t *buffer = new uint8_t[packet->GetSize()];
  packet->CopyData(buffer,packet->GetSize());
  string recMessage = string((char*)buffer);
  recMessage = recMessage.substr (0,packet->GetSize());

  // TODO: Change this so that we get ipv6 and ipv4 addresses depending on the socket passed in
//  Ipv4Address srcIpv4Address = InetSocketAddress::ConvertFrom (from).GetIpv4();
//  uint32_t srcNodeId = mapIpv4NodeId[srcIpv4Address];

  //--- print received msg
  NS_LOG_DEBUG(
      "Pkt Rcv at "    << Simulator::Now ().GetMilliSeconds ()
                       << " by nodeName: " << Names::FindName(socket->GetNode ())
                       << " dstNodeId: "   << socket->GetNode()->GetId()
//                       << " srcNodeId: "   << srcNodeId
                       << " Size: "        << packet->GetSize()
                       << " Payload: "     << recMessage
                       << endl;
  );

  //--- get val and val_time
  std::size_t current;
  current = recMessage.find("&");
  string val = recMessage.substr(0, current);
  string val_time = recMessage.substr(current+1);

  //--- insert data on dataXchgOutput / give to upper layer
//  DataXCHG dataRcv = { Names::FindName(NodeList::GetNode(srcNodeId)),
//                       Names::FindName(socket->GetNode ()),
//                       val,
//                       stoll(val_time)
//  };
//  dataXchgOutput.push_back(dataRcv);

  ofstream filePacketsSent;
  filePacketsSent.open("packets_rec.pkt", std::ios_base::app);
  filePacketsSent << "time: " << Simulator::Now ().GetMilliSeconds ()
	  << " by nodeName: " << Names::FindName(socket->GetNode ())
	  << " dstNodeId: "   << socket->GetNode()->GetId()
//	  << " srcNodeId: "   << srcNodeId
	  << " Payload: "     << recMessage << std::endl;
  filePacketsSent.close();
}

NS3Netsim::NS3Netsim():
    linkCount(0), sinkPort(0),  startTime(0), verbose (0)
{
  //--- setup simulation type
  GlobalValue::Bind ("SimulatorImplementationType",
                     StringValue ("ns3::SmartgridDefaultSimulatorImpl"));
//  LogComponentEnable ("Ping6Application", LOG_LEVEL_ALL);
//  LogComponentEnable("ArpL3Protocol", LOG_LEVEL_ALL);
//  LogComponentEnable("ArpCache", LOG_LEVEL_ALL);
//  LogComponentEnable("Simulator", LOG_LEVEL_ALL);
//  LogComponentEnable("LrWpanCsmaCa", LOG_LEVEL_ALL);
//  LogComponentEnable("LrWpanNetDevice", LOG_LEVEL_ALL);
//  LogComponentEnable("LrWpanMac", LOG_LEVEL_ALL);
//  LogComponentEnable("SmartgridDefaultSimulatorImpl", LOG_LEVEL_ALL);
//  LogComponentEnable("SmartgridNs3Main", LOG_LEVEL_ALL);
//  LogComponentEnable ("MultiClientTcpServer", LOG_LEVEL_ALL);
//  LogComponentEnable ("TcpClient", LOG_LEVEL_ALL);
//  LogComponentEnable ("Socket", LOG_LEVEL_ALL);
//  LogComponentEnable ("SocketFactory", LOG_LEVEL_ALL);
//  LogComponentEnable ("TcpSocket", LOG_LEVEL_ALL);
//  LogComponentEnable ("TcpSocketBase", LOG_LEVEL_ALL);
//  LogComponentEnable ("SixLowPanNetDevice", LOG_LEVEL_ALL);
//  LogComponentEnable ("TcpL4Protocol", LOG_LEVEL_ALL);
//  LogComponentEnable ("IpL4Protocol", LOG_LEVEL_ALL);
//  LogComponentEnable ("EventImpl", LOG_LEVEL_ALL);
//  LogComponentEnable ("Node", LOG_LEVEL_ALL);
//  LogComponentEnable ("Application", LOG_LEVEL_ALL);
//  LogComponentEnable ("Packet", LOG_LEVEL_ALL);
//  LogComponentEnable ("Address", LOG_LEVEL_ALL);
}


NS3Netsim::~NS3Netsim() {
  Simulator::Destroy ();
  NS_LOG_INFO ("Done.");
}


void
NS3Netsim::init (string f_adjmat,
                 string f_coords,
                 string f_appcon,
                 string s_linkRate,
                 string s_linkDelay,
                 string s_linkErrorRate,
                 double start_time,
                 int verb,
                 string s_tcpOrUdp)
{
  // Point to point helper for point to point connections
  PointToPointHelper pointToPoint;
  // LrWpanHelper for 802.15.4 wireless communcation
  LrWpanHelper lrWpanHelper;
  // Internet stack helper to help with installation of internet
  InternetStackHelper internet;
  // Pointer to Ipv4 Internet helper class
  Ipv4AddressHelper ipv4Address;
  // Pointer to the Ipv6 Internet helper class
  Ipv6AddressHelper ipv6Address;
  // Pointer to mobility (position) helper class
  MobilityHelper mobility;
  // Helper, set up a stack to be used between IPv6 and a generic
  SixLowPanHelper sixlowpan;

  allApplications = ApplicationContainer ();
  //--- verbose level
  verbose = verb;
  // save which protocol should be used
  tcpOrUdp = s_tcpOrUdp;
  std::cout << "Network Mode: " << tcpOrUdp << std::endl;

  NS_LOG_FUNCTION(this);

  // --- generate different seed each time
  srand ( (unsigned)time ( NULL ) );

  //--- set link properties
  LinkRate  = s_linkRate;
  LinkDelay = s_linkDelay;
  LinkErrorRate = s_linkErrorRate;
  linkCount = 0;

  //--- set address properties for ipv4
  ipv4Address.SetBase ("10.0.0.0", "255.255.255.252");
  //--- set the address properties for ipv6
  ipv6Address.SetBase (Ipv6Address ("2001:2::"), Ipv6Prefix (64));

  //--- set application destination port
  sinkPort = 3030;

  //--- simulation parameters
  startTime  = start_time;

  //--- set configuration file names
  nodeAdjMatrixFilename   = f_adjmat;
  nodeCoordinatesFilename = f_coords;
  appConnectionsFilename  = f_appcon;

  //--- load adjacency matrix
  NS_LOG_INFO ("Load node adjacency matrix");
  nodeAdjMatrix = ReadNodeAdjMatrix (nodeAdjMatrixFilename);
  if (verbose > 8) {
      PrintNodeAdjMatrix (nodeAdjMatrixFilename.c_str (), nodeAdjMatrix);
    }

  //--- load node coordinates and names
  NS_LOG_INFO ("Load node names and coordinates");
  arrayNamesCoords = ReadCoordinatesFile (nodeCoordinatesFilename);
  arrayNodeCoords = loadNodeCoords(arrayNamesCoords);
  if (verbose > 1) {
      PrintNamesCoordinates (nodeCoordinatesFilename.c_str (), arrayNamesCoords);
    }

  //--- check node coordinates dimension and adjacency matrix dimension
  if (nodeAdjMatrix.size () != arrayNamesCoords.size())
    {
      NS_FATAL_ERROR ("The number of lines in coordinate file is: " << arrayNamesCoords.size()
                                                                    << " not equal to the number of nodes in adjacency matrix size " << nodeAdjMatrix.size ());
    }

  //--- create nodes container and give names
  NS_LOG_INFO ("Create node container.");
  nodes.Create (arrayNamesCoords.size());
  for (size_t m = 0; m < arrayNamesCoords.size (); m++)
    {
      Names::Add (arrayNamesCoords[m][0], nodes.Get (m));
      Ptr<Node> newNode = Names::Find<Node>(arrayNamesCoords[m][0]);
    }

  // --- Allocate node positions
  NS_LOG_INFO ("Allocate Positions to Nodes.");
  nodePositionAlloc = CreateObject<ListPositionAllocator> ();
  for (size_t m = 0; m < arrayNodeCoords.size (); m++)
    {
      nodePositionAlloc->Add (Vector (arrayNodeCoords[m][0], arrayNodeCoords[m][1], 0));
      Ptr<Node> n0 = nodes.Get (m);
      Ptr<ConstantPositionMobilityModel> nLoc =  n0->GetObject<ConstantPositionMobilityModel> ();
      if (nLoc == 0)
        {
          nLoc = CreateObject<ConstantPositionMobilityModel> ();
          n0->AggregateObject (nLoc);
        }
      Vector nVec (arrayNodeCoords[m][0], arrayNodeCoords[m][1], 0);
      NS_LOG_INFO ("Node[" << m << "]: " << "(" << arrayNodeCoords[m][0] << "," << arrayNodeCoords[m][1] << ")");
      nLoc->SetPosition (nVec);
    }
  mobility.SetPositionAllocator (nodePositionAlloc);
  mobility.Install (nodes);

  //--- sort array
  sort(nodeServerList.begin(), nodeServerList.end());
  //--- unique elements
  iList = unique(nodeServerList.begin(), nodeServerList.end());
  //--- resize list
  nodeServerList.resize(distance(nodeServerList.begin(), iList));

  // Set the internet stack on every node
  internet.Install (NodeContainer::GetGlobal ());

  //--- create network topology
  NS_LOG_INFO ("Create p2p and lr-wpan links Between Nodes, then set internet stack and addresses");
  pointToPoint.SetDeviceAttribute  ("DataRate", StringValue (LinkRate));
  pointToPoint.SetChannelAttribute ("Delay",    StringValue (LinkDelay));
  for (size_t i = 0; i < nodeAdjMatrix.size (); i++)
  {
	for (size_t j = i; j < nodeAdjMatrix[i].size (); j++)
	{
	  if (nodeAdjMatrix[i][j] == 1)
	  {
		// Create a point to point link
		linkCount++;
		NodeContainer n_links = NodeContainer (nodes.Get (i), nodes.Get (j));

		uint32_t iId = nodes.Get(i)->GetId();
		uint32_t jId = nodes.Get(j)->GetId();

		NS_LOG_INFO ("matrix element [" << i << "][" << j << "] is " << nodeAdjMatrix[i][j]);
		NetDeviceContainer n_devs = pointToPoint.Install (n_links);
		p2pDevices.push_back(n_devs);
		ipv4Address.Assign (n_devs);
		ipv4Address.NewNetwork ();
	  }
	  else
	  {
		NS_LOG_INFO ("matrix element [" << i << "][" << j << "] is 0");
	  }
	}
  }

  // Getting PAN network from files
  panNetworks = CreateMapForLRWPAN("");

  // Create the LR-WPAN connections specified in the files with 6LoWPAN
  // Iterate through the keys found in the network, the keys act as the center of the PAN
  for (auto center = panNetworks.begin(); center != panNetworks.end(); center++) {
    // Stores the nodes in the PAN
	NodeContainer panNodes;
	// Add the center to the list
//	panNodes.Add(Names::Find<Node>((*center).first));
	for (auto spokes = (*center).second.begin(); spokes != (*center).second.end(); spokes++) {
	  // Add the spokes to the list
	  panNodes.Add(Names::Find<Node>(*spokes));
	}

	WifiHelper wifi;
	NetDeviceContainer staDevs;
	NetDeviceContainer apDevs;
	WifiMacHelper wifiMac;
	YansWifiPhyHelper wifiPhy = YansWifiPhyHelper::Default ();
	YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default ();
	wifiPhy.SetChannel (wifiChannel.Create ());
	Ssid ssid = Ssid ((*center).first);
	wifi.SetRemoteStationManager ("ns3::ArfWifiManager");

	wifiMac.SetType ("ns3::StaWifiMac",
					 "ActiveProbing", BooleanValue (true),
					 "Ssid", SsidValue (ssid));
	staDevs = wifi.Install (wifiPhy, wifiMac, panNodes);
	// setup ap.
	wifiMac.SetType ("ns3::ApWifiMac",
					 "Ssid", SsidValue (ssid));
	apDevs = wifi.Install (wifiPhy, wifiMac, Names::Find<Node>((*center).first));

	wifiPhy.EnablePcap ("AccessPoint", apDevs);
	wifiPhy.EnablePcap ("Station", staDevs);

	ipv6Address.Assign (staDevs);
	ipv6Address.Assign (apDevs);
	ipv6Address.NewNetwork();

//	// Install the LR-WPAN devices
//	NetDeviceContainer lrwpanDevices = lrWpanHelper.Install(panNodes);
//	// Fake PAN association and short address assignment.
//	lrWpanHelper.AssociateToPan (lrwpanDevices, stoi((*center).first));
//	// Add Sixlowpan devices
//	NetDeviceContainer sixlowpanDevices = sixlowpan.Install (lrwpanDevices);
//	// Add the ipv6 addresses
//	ipv6Address.Assign (sixlowpanDevices);
//	ipv6Address.NewNetwork();
  }

//  if (verbose > 1) {
//	cout << "Printing LR-WPAN network connections read from file" << endl;
//	for (auto it = panNetworks.begin(); it != panNetworks.end(); it++) {
//	  cout << (*it).first << ";";
//	  for (auto it2 = (*it).second.begin(); it2 != (*it).second.end(); it2++) {
//		cout << *it2 << ",";
//		create((*it).first, *it2);
//	  }
//	  cout << endl;
//	}
//  }

  //--- set link error rate
  Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
  em->SetAttribute ("ErrorRate", DoubleValue (stod(LinkErrorRate)));
  for (auto dev = p2pDevices.begin(); dev != p2pDevices.end(); ++dev)
  {
	(*dev).Get(1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));
	if (verbose > 1) {
	  std::cout << "int(0) =  "   << (*dev).Get(0)->GetAddress()
				<< "  int(1) =  " << (*dev).Get(1)->GetAddress()
				<< " ID = " << (*dev).Get(1)->GetNode()->GetId()
				<< std::endl;
	}
  }

  if (verbose > 1) {
	PrintIpAddresses(nodes);
  }

  //--- create map Ipv4 address to NodeId
  mapIpv4NodeId = CreateMapIpv4NodeId(nodes);

  // --- Global routing protocol for IP version 4 stacks
  NS_LOG_INFO ("Initialize Global Routing.");
  Ipv4GlobalRoutingHelper::PopulateRoutingTables ();

  //--- Output topology summary
  NS_LOG_INFO ("Number of links in the adjacency matrix is: " << linkCount);
  NS_LOG_INFO ("Number of all nodes is: " << nodes.GetN ());

  //--- set regular trace file
  AsciiTraceHelper ascii;
//  pointToPoint.EnableAsciiAll (ascii.CreateFileStream ("pointToPointNS3.tr"));
//  lrWpanHelper.EnableAsciiAll (ascii.CreateFileStream ("lrWpanHelperNS3.tr"));
//  pointToPoint.EnablePcapAll("pcapNS3Netsim.pcap");
//  pointToPoint.EnablePcap("dse", 0, 0, true);
//  lrWpanHelper.EnablePcapAll("lrWpanHelperNS3.pcap");
//  lrWpanHelper.EnablePcap("dse", 0, 0, true);
}


void
NS3Netsim::create (string client, string server)
{
  NS_LOG_FUNCTION(this);
  bool found = false;

  //---
  //--- update list of application connections
  //---
  vector<string> record;
  record.push_back(client);
  record.push_back(server);
  //--- Search for already existing connection
  for (auto rec = arrayAppConnections.begin(); rec != arrayAppConnections.end(); ++rec) {
      string clt = (*rec).front();
      string srv = (*rec).back();
      //--- connection already exist, break
      if ((clt.compare(client) == 0) && (srv.compare(server) == 0)) {
          NS_LOG_DEBUG("NS3Netsim::create Connection already exist: " << client << " --> " << server << endl);
          found = true;
          break;
        }
    }
  //--- new connection, create entries
  if(found == false) {
	arrayAppConnections.push_back(record);

	// create server socket
	NS_LOG_INFO("Create server.");
	Ptr<Node> srvNode = Names::Find<Node>(server);

	Ptr<Node> dstNode = Names::Find<Node>(server);

	// Check protocol
	//--- verify if server already exist
	std::vector<std::string>::iterator it = std::find(nodeServerList.begin(), nodeServerList.end(), server);
	//--- if not found
	if (it == nodeServerList.end()) {
	  // Create the server application
	  setUpServer(InetSocketAddress(Ipv4Address::GetAny(), sinkPort), Inet6SocketAddress(Ipv6Address::GetAny (), sinkPort), tcpOrUdp, server);
	  NS_LOG_DEBUG("NS3Netsim::create Server: " << *iList << endl);
	} else {        //--- end of server part
	  NS_LOG_DEBUG("NS3Netsim::create Server already on the list: " << server << endl);
	}
	// create client socket
	NS_LOG_INFO("Create client.");
	// Check if  this is part of one of the LR-WPAN networks
	// If part of LR-WPAN, use ipv6, otherwise use ipv4
	if (panNetworks.count(server) != 0 && panNetworks[server].count(client) != 0) {
	  Ipv6InterfaceAddress sink_iaddr = dstNode->GetObject<Ipv6>()->GetAddress(1,0);
	  Inet6SocketAddress remote = Inet6SocketAddress(sink_iaddr.GetAddress(), sinkPort);
	  setUpClient(AddressValue(remote), tcpOrUdp, server, client);
	} else {
	  Ipv4InterfaceAddress sink_iaddr = dstNode->GetObject<Ipv4>()->GetAddress(1,0);
	  InetSocketAddress remote = InetSocketAddress(sink_iaddr.GetLocal(), sinkPort);
	  setUpClient(AddressValue(remote), tcpOrUdp, server, client);
	}
  }
}

void
NS3Netsim::setUpServer(InetSocketAddress addressIpv4, Inet6SocketAddress addressIpv6, string protocol, string server)
{
  NS_LOG_FUNCTION(this);
  // Where the returned application will be stored
  ApplicationContainer serverAppContainer;
  // Switch on the protocol passed in
  if (protocol == "tcp") {
      // Set the address with which the application should be created
      multiClientTcpServerHelper.SetAttribute("LocalIpv4", AddressValue(addressIpv4));
      multiClientTcpServerHelper.SetAttribute("LocalIpv6", AddressValue(addressIpv6));
      serverAppContainer = multiClientTcpServerHelper.Install(server);
      // Set the call back to extract information from a packet and sent it to the upper layer
      Ptr<MultiClientTcpServer> serverAppAsCorrectType = DynamicCast<MultiClientTcpServer> (serverAppContainer.Get(0));
      // Set the function that should be called when the server receives a packet
      serverAppAsCorrectType->SetPacketReceivedCallBack(ExtractInformationFromPacketAndSendToUpperLayer);
  } else if (protocol == "udp") {
      // Set the address with which the application should be created
      customUdpServerHelper.SetAttribute("LocalIpv4", AddressValue(addressIpv4));
      customUdpServerHelper.SetAttribute("LocalIpv6", AddressValue(addressIpv6));
      // Create a tcp container
      serverAppContainer = customUdpServerHelper.Install(server);
      // Set the call back to extract information from a packet and sent it to the upper layer
      Ptr<CustomUdpServer> serverAppAsCorrectType = DynamicCast<CustomUdpServer> (serverAppContainer.Get(0));
      // Set the function that should be called when the server receives a packet
      serverAppAsCorrectType->SetPacketReceivedCallBack(ExtractInformationFromPacketAndSendToUpperLayer);
  } else {
      // If unknown protocol, stop and throw error
      NS_FATAL_ERROR("Invalid protocol passed in");
  }

  // Save the app
  allApplications.Add(serverAppContainer.Get(0));
  // Start the application at the start of the simulation
  serverAppContainer.Start(NanoSeconds(0.0));
  //--- update server node list
  nodeServerList.push_back(server);
  //--- sort array
  sort(nodeServerList.begin(), nodeServerList.end());
}

void
NS3Netsim::setUpClient(AddressValue addressValue, string protocol, string server, string client)
{
  NS_LOG_FUNCTION(this);
  // Get the server and the client nodes
  Ptr<Node> srcNode = Names::Find<Node>(client);
  Ptr<Node> dstNode = Names::Find<Node>(server);
  // Where the returned application will be stored
  ApplicationContainer clientAppContainer;
  // Switch on the protocol passed in
  if (protocol == "tcp") {
      // Create a tcp client
      tcpClientHelper.SetAttribute("Remote", addressValue);
      clientAppContainer = tcpClientHelper.Install(client);
  } else if (protocol == "udp") {
      // Create a udp client
      customUdpClientHelper.SetAttribute("Remote", addressValue);
      clientAppContainer = customUdpClientHelper.Install(client);
  } else {
      // If unknown protocol, stop and throw error
      NS_FATAL_ERROR("Invalid protocol passed in");
  }

  // Add the application to the container and start the application
  allApplications.Add(clientAppContainer.Get(0));
  clientAppContainer.Start(NanoSeconds(0.0));
}

void
NS3Netsim::schedule (string src, string dst, string val, string val_time)
{
  if (verbose > 1) {
      std::cout << "NS3Netsim::schedule" << std::endl;
    }

  if (verbose > 1) {
      std::cout << "NS3Netsim::schedule NS3_Time: " << Simulator::Now ().GetMilliSeconds ()
                << " Event_Val_Time: " << val_time << std::endl;
      std::cout << "NS3Netsim::schedule("
                << "source="   << src
                << ", destination=" << dst
                << ", value=" << val
                << ", delay=" << val_time
                << ")" << std::endl;
    }

  Ptr<Node> srcNode = Names::Find<Node>(src);
  if (srcNode->GetNApplications() > 0) {
	if (tcpOrUdp == "tcp") {
	  Ptr<TcpClient> clientApp = DynamicCast<TcpClient> (srcNode->GetApplication(0));
	  if (clientApp == 0){
		clientApp = DynamicCast<TcpClient> (srcNode->GetApplication(1));
	  }
	  clientApp->ScheduleTransmit(val, val_time);
	} else if (tcpOrUdp == "udp") {
	  Ptr<CustomUdpClient> clientApp = DynamicCast<CustomUdpClient> (srcNode->GetApplication(0));
	  if (clientApp == 0){
		clientApp = DynamicCast<CustomUdpClient> (srcNode->GetApplication(1));
	  }
	  clientApp->ScheduleTransmit(val, val_time);
	}
  }
}


void
NS3Netsim::runUntil (string nextStop)
{
  if (verbose > 1) {
      std::cout << "NS3Netsim::runUntil(time=" << nextStop  << ")" << std::endl;
    }

  //--- run scheduler until a given time
  sim = DynamicCast<SmartgridDefaultSimulatorImpl>(Simulator::GetImplementation());
  sim->RunUntil(MilliSeconds (stod(nextStop)));

  if (verbose > 3)
    {
      DataXCHG dataSnt;
      for (auto it = dataXchgOutput.begin(); it != dataXchgOutput.end(); ++it)
        {
          cout << "NS3Netsim::runUntil NS3 OUTPUT Buffer Src: " << (*it).src
               << " Dst: " << (*it).dst
               << " Val: " << (*it).val
               << " Time: " << (*it).time
               << endl;
        }
    }

  if (stoi(nextStop) % 100 == 0){
	schedule ("6321", "632", to_string(-stoi(nextStop)), to_string(stoi(nextStop) + 20));
  }

  if (verbose > 1) {
      std::cout << "NS3Netsim::runUntil After_run NS3 time: " <<  Simulator::Now ().GetMilliSeconds () << std::endl;
    }
}


int
NS3Netsim::get_data (string &src, string &dst, string &val_v, string &val_t)
{
  int res;
  DataXCHG dataOut;

  if (verbose > 1) {
      std::cout << "NS3Netsim::get_data" << std::endl;
      std::cout << "NS3Netsim::get_data NS3-OUTPUT-QUEUE-SIZE: " << dataXchgOutput.size() << std::endl;
    }

  if (!dataXchgOutput.empty())
    {
      res = 1;
      dataOut = dataXchgOutput.back();
      dataXchgOutput.pop_back();
      src = dataOut.src;
      dst = dataOut.dst;
      val_v = dataOut.val;
      val_t = to_string(dataOut.time);
    } else {
      res = 0;
    }

  if (verbose > 2) {
      for (auto it = dataXchgOutput.begin(); it != dataXchgOutput.end(); ++it)
        {
          if ((*it).src == src && (*it).dst == dst)
            cout << "NS3Netsim::get_data NS3 OUTPUT Buffer Src: " << (*it).src
                 << " Dst: " << (*it).dst
                 << " Val: " << (*it).val
                 << " Time: " << (*it).time
                 << endl;
        }
    }

  return res;
}


bool
NS3Netsim::checkEmptyDataOutput (void)
{
  return dataXchgOutput.empty();
}


int
NS3Netsim::getSizeDataOutput (void)
{
  return dataXchgOutput.size();
}

int
NS3Netsim::getSizeDataInput (void)
{
  return dataXchgInput.size();
}

double
NS3Netsim::getCurrentTime (void)
{
  return Simulator::Now ().GetMilliSeconds ();
}

