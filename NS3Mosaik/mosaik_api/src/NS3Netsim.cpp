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
#include "NS3Netsim.h"
#include "ns3-helper.h"
#include "ns3/smartgrid-default-simulator-impl.h"
#include <cassert>

using namespace std;
using namespace ns3;

NS_LOG_COMPONENT_DEFINE("SmartgridNs3Main");
std::string fileNameReceived = "packets_received.pkt";

//--- IPv4 or IPv6 active
bool v4;

/**
 * \brief Passes a a preprocessed message of the form "<data>&<time>" to the upper layer.
 *
 * \param message
 * \param sourceNode
 * \param destinationNode
 */
void sendMessageToUpperLayer(string message, Ptr<Node> sourceNode, Ptr<Node> destinationNode)
{
  std::size_t current;
  //--- get val and val_time
  current = message.find("&");
  string val = message.substr(0, current);
  string val_time = message.substr(current+1);
  //--- insert data on dataXchgOutput / give to upper layer
  DataXCHG dataRcv = {Names::FindName(sourceNode),
                      Names::FindName(destinationNode),
                      val,
                      stoll(val_time)};
  dataXchgOutput.push(dataRcv);
}

/**
 * \brief Parses the packet received by the an appliction/socket and adds it to the list of packets that will be sent to the upper layer.
 *
 * \param socket
 */
void ExtractInformationFromPacketAndSendToUpperLayer(Ptr<Socket> socket)
{
  Address from;
  Ptr<Packet> packet = socket->RecvFrom(from);
  uint32_t srcNodeId;
  if (v4)
  {
    Ipv4Address srcIpv4Address = InetSocketAddress::ConvertFrom(from).GetIpv4();
    srcNodeId = mapIpv4NodeId[srcIpv4Address];
  }
  else
  {
    Ipv6Address srcIpv6Address = Inet6SocketAddress::ConvertFrom(from).GetIpv6();
    srcNodeId = mapIpv6NodeId[srcIpv6Address];
  }
  Ptr<Node> srcNode = NodeList::GetNode(srcNodeId);

  packet->RemoveAllPacketTags();
  packet->RemoveAllByteTags();

  uint32_t packetSize = packet->GetSize();
  uint8_t *buffer = new uint8_t[packetSize];
  packet->CopyData(buffer, packetSize);
  string recMessage = string((char *)buffer);
  recMessage = recMessage.substr(0, packetSize);

  PacketMetadata::ItemIterator i = packet->BeginItem();
  //A packet can contain fragments, complete payloads or a combination of both.
  while (i.HasNext())
  {
    PacketMetadata::Item item = i.Next();
    if (item.isFragment)
    {
      if (item.type == PacketMetadata::Item::PAYLOAD)
      {
        //We check if the sender node has an entry in the fragment buffers hash table
        if (fragmentBuffers.find(srcNodeId) == fragmentBuffers.end())
        {
          //If there is no entry, insert an entry with an empty string
          fragmentBuffers[srcNodeId] = "";
        }
        //This packet is a fragment in its entirety, it can correspond to one of the middle or end fragments of
        //a fragmented package
        //Example packet structure: (Fragment)
        if (item.currentSize == packetSize)
        {
          //concatenate the contents of this fragment to the contents of the previously received fragments
          fragmentBuffers[srcNodeId] = fragmentBuffers[srcNodeId] + recMessage;
          //TODO: Flush the buffer on receiving a package that just contains a fragment?
        }
        //This packet contains a complete payload as well as a payload fragment(s)
        else if (item.currentSize < packetSize)
        {
          //If fragment starts at 0 bits, it means that it is the begining of a fragmented package
          //it is reasonable to assume that the corresponding data will be at the end of the packet
          //after the complete payload
          //Example packet structure: (Fragment)(Payload)(Fragment) or (Fragment)(Payload)
          if (item.currentTrimedFromStart == 0)
          {
            string fragmentMessage = recMessage.substr(recMessage.size() - item.currentSize, item.currentSize);
            fragmentBuffers[srcNodeId] = fragmentBuffers[srcNodeId] + fragmentMessage;
            //Remove the fragment from the received message string so that we can process that fragment
            recMessage = recMessage.substr(0, recMessage.size() - item.currentSize);
          }
          //If fragment starts at n bits of a fragmented package and the length of the fragment is less
          //than the total length of the package, we assume that this is the final fragment  of the fragment package
          //which may be followed by a complete payload, which will be handled in the next iteration.
          //Since it is the final fragment, it will be located at the start of the package.
          //Example packet structure: (Payload)(Fragment) or (Fragment)(Payload)(Fragment)
          else if (item.currentTrimedFromStart > 0)
          {
            string fragmentMessage = recMessage.substr(0, item.currentSize);
            fragmentBuffers[srcNodeId] = fragmentBuffers[srcNodeId] + fragmentMessage;
            //Remove the fragment from the received message string
            recMessage = recMessage.substr(item.currentSize);
          }
        }
      }
    }
    else
    {
      //If item is not a fragment and instead it is an unfragmented payload,
      //it is time to flush the fragment buffer corresponding to this source node
      unordered_map<uint32_t, std::string>::iterator fragmentBufferIterator = fragmentBuffers.find(srcNodeId);
      if (fragmentBufferIterator != fragmentBuffers.end())
      {
        string assembledFragments = fragmentBufferIterator->second;
        sendMessageToUpperLayer(assembledFragments, srcNode, socket->GetNode());
        fragmentBuffers.erase(fragmentBufferIterator);
        
        if (v4)
          NS_LOG_DEBUG("Fragmented Pkt Rcv at " << Simulator::Now().GetMilliSeconds()
                                     << " by nodeName: " << Names::FindName(socket->GetNode())
                                     << " dstNodeId: " << socket->GetNode()->GetId()
                                     << " dstAddr: " << socket->GetNode()->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal()
                                     << " srcNodeId: " << srcNodeId
                                     << " srcAddr: " << InetSocketAddress::ConvertFrom(from).GetIpv4()
                                     << " Size: " << packet->GetSize()
                                     << " Payload: " << assembledFragments
                                     << endl;);
        else
          NS_LOG_DEBUG("Fragmented Pkt Rcv at " << Simulator::Now().GetMilliSeconds()
                                     << " by nodeName: " << Names::FindName(socket->GetNode())
                                     << " dstNodeId: " << socket->GetNode()->GetId()
                                     << " dstAddr: " << socket->GetNode()->GetObject<Ipv6>()->GetAddress(1, 0).GetAddress()
                                     << " srcNodeId: " << srcNodeId
                                     << " srcAddr: " << Inet6SocketAddress::ConvertFrom(from).GetIpv6()
                                     << " Size: " << packet->GetSize()
                                     << " Payload: " << assembledFragments
                                     << endl;);
      }

      //After flushing the fragments stored in the fragment buffer for this particular source node
      //send the message received in the unfragmented payload
      string partMessage = recMessage.substr(0, item.currentSize);
      sendMessageToUpperLayer(partMessage, srcNode, socket->GetNode());
      recMessage = recMessage.substr(item.currentSize);

      if (v4)
        NS_LOG_DEBUG("Unfragmented Pkt Rcv at " << Simulator::Now().GetMilliSeconds()
                                     << " by nodeName: " << Names::FindName(socket->GetNode())
                                     << " dstNodeId: " << socket->GetNode()->GetId()
                                     << " dstAddr: " << socket->GetNode()->GetObject<Ipv4>()->GetAddress(1, 0).GetLocal()
                                     << " srcNodeId: " << srcNodeId
                                     << " srcAddr: " << InetSocketAddress::ConvertFrom(from).GetIpv4()
                                     << " Size: " << packet->GetSize()
                                     << " Payload: " << recMessage
                                     << endl;);
      else
        NS_LOG_DEBUG("Unfragmented Pkt Rcv at " << Simulator::Now().GetMilliSeconds()
                                     << " by nodeName: " << Names::FindName(socket->GetNode())
                                     << " dstNodeId: " << socket->GetNode()->GetId()
                                     << " dstAddr: " << socket->GetNode()->GetObject<Ipv6>()->GetAddress(1, 0).GetAddress()
                                     << " srcNodeId: " << srcNodeId
                                     << " srcAddr: " << Inet6SocketAddress::ConvertFrom(from).GetIpv6()
                                     << " Size: " << packet->GetSize()
                                     << " Payload: " << recMessage
                                     << endl;);
    }
  }
}

NS3Netsim::NS3Netsim() : linkCount(0), sinkPort(0), startTime(0), verbose(0)
{
  //--- setup simulation type
  GlobalValue::Bind("SimulatorImplementationType",
                    StringValue("ns3::SmartgridDefaultSimulatorImpl"));
  // LogComponentEnable("Simulator", LOG_LEVEL_ALL);
  // LogComponentEnable("SmartgridDefaultSimulatorImpl", LOG_LEVEL_ALL);
  // LogComponentEnable("SmartgridNs3Main", LOG_LEVEL_ALL);
  // LogComponentEnable("MultiClientTcpServer", LOG_LEVEL_ALL);
  // LogComponentEnable("TcpClient", LOG_LEVEL_ALL);
  // LogComponentEnable("Socket", LOG_LEVEL_ALL);
  // LogComponentEnable("SocketFactory", LOG_LEVEL_ALL);
  // LogComponentEnable("TcpSocket", LOG_LEVEL_ALL);
  // LogComponentEnable("TcpSocketBase", LOG_LEVEL_ALL);
  // LogComponentEnable("TcpL4Protocol", LOG_LEVEL_ALL);
  // LogComponentEnable("IpL4Protocol", LOG_LEVEL_ALL);
  // LogComponentEnable ("Ipv4L3Protocol", LOG_LEVEL_ALL);
  // LogComponentEnable("EventImpl", LOG_LEVEL_ALL);
  // LogComponentEnable("Node", LOG_LEVEL_ALL);
  // LogComponentEnable("Application", LOG_LEVEL_ALL);
  // LogComponentEnable ("Ipv4StaticRouting", LOG_LEVEL_ALL);
  // LogComponentEnable ("Ipv4Interface", LOG_LEVEL_ALL);
  // LogComponentEnable ("Ipv6L3Protocol", LOG_LEVEL_ALL);
  // LogComponentEnable ("Icmpv6L4Protocol", LOG_LEVEL_ALL);
  // LogComponentEnable ("Ipv6StaticRouting", LOG_LEVEL_ALL);
  // LogComponentEnable ("Ipv6Interface", LOG_LEVEL_ALL);

  // Config::SetDefault("ns3::TcpSocket::TcpNoDelay", BooleanValue(true));
  //--- To set the nodes as routers for IPv6, where they are hosts by default
  Config::SetDefault("ns3::Ipv6::IpForward", BooleanValue(true));
}

NS3Netsim::~NS3Netsim()
{
  Simulator::Destroy();
  NS_LOG_INFO("Done.");
}

void NS3Netsim::init(string f_adjmat,
                     string f_coords,
                     string f_appcon,
                     string f_json,
                     string s_linkRate,
                     string s_linkDelay,
                     string s_linkErrorRate,
                     string start_time,
                     string stop_time,
                     string verb,
                     string s_tcpOrUdp,
                     string s_net)
{
  allApplications = ApplicationContainer();
  //--- verbose level
  verbose = stoi(verb);
  // save which protocol should be used
  tcpOrUdp = s_tcpOrUdp;
  std::cout << "Network Mode: " << tcpOrUdp << std::endl;
  // save which architecture should be used
  netArch = s_net;
  std::cout << "Network Architecture: " << netArch << std::endl;
  if (netArch == "P2P" || netArch == "CSMA")  v4 = true;
  else  v4 = false;

  NS_LOG_FUNCTION(this);

  // --- generate different seed each time
  long int seed = 1;
  srand((unsigned)time(&seed));

  //--- set link properties
  LinkRate = s_linkRate;
  LinkDelay = s_linkDelay;
  LinkErrorRate = s_linkErrorRate;
  linkCount = 0;

  //--- set devices properties
  if (v4) ipv4Address.SetBase("10.0.0.0", "255.255.255.252");
  else  ipv6Address.SetBase(Ipv6Address("2001:1::"), Ipv6Prefix(64));

  //--- set application destination port
  sinkPort = 3030;

  //--- simulation parameters
  startTime = stod(start_time);
  stopTime = stod(stop_time);

  //--- set configuration file names
  nodeAdjMatrixFilename = f_adjmat;
  nodeCoordinatesFilename = f_coords;
  appConnectionsFilename = f_appcon;
  string nodeJSONFilename = f_json;

  //--- load adjacency matrix
  NS_LOG_INFO("Load node adjacency matrix");
  // nodeAdjMatrix = ReadNodeAdjListJson(nodeJSONFilename);
  nodeAdjMatrix = ReadNodeAdjMatrix(nodeAdjMatrixFilename);
  if (verbose > 8)
  {
    PrintNodeAdjMatrix(nodeJSONFilename.c_str(), nodeAdjMatrix);
  }

  //--- load node coordinates and names
  NS_LOG_INFO("Load node names and coordinates");
  // arrayNamesCoords = ReadCoordinatesJSONFile(nodeJSONFilename);
  arrayNamesCoords = ReadCoordinatesFile(nodeCoordinatesFilename);
  arrayNodeCoords = loadNodeCoords(arrayNamesCoords);
  if (verbose > 1)
  {
    PrintNamesCoordinates(nodeJSONFilename.c_str(), arrayNamesCoords);
  }

  //--- check node coordinates dimension and adjacency matrix dimension
  if (nodeAdjMatrix.size() != arrayNamesCoords.size())
  {
    NS_FATAL_ERROR("The number of lines in coordinate file is: " << arrayNamesCoords.size()
                                                                 << " not equal to the number of nodes in adjacency matrix size " << nodeAdjMatrix.size());
  }

  //--- create nodes container and give names
  NS_LOG_INFO("Create node container.");
  nodes.Create(arrayNamesCoords.size());
  for (size_t m = 0; m < arrayNamesCoords.size(); m++)
  {
    Names::Add(arrayNamesCoords[m][0], nodes.Get(m));
    Ptr<Node> newNode = Names::Find<Node>(arrayNamesCoords[m][0]);
  }

  //--- create network topology
  NS_LOG_INFO("Create Links Between Nodes.");
  if (netArch == "P2P" || netArch == "P2Pv6")
  {
    pointToPoint.SetDeviceAttribute("DataRate", StringValue(LinkRate));
    pointToPoint.SetChannelAttribute("Delay", StringValue(LinkDelay));
  }
  else if (netArch == "CSMA" || netArch == "CSMAv6")
  {
    csma.SetChannelAttribute  ("DataRate", StringValue (LinkRate));
    csma.SetChannelAttribute ("Delay",    StringValue (LinkDelay));
  }
  for (size_t i = 0; i < nodeAdjMatrix.size(); i++)
  {
    for (size_t j = i; j < nodeAdjMatrix[i].size(); j++)
    {
      if (nodeAdjMatrix[i][j] == 1)
      {
        linkCount++;
        NodeContainer n_links = NodeContainer(nodes.Get(i), nodes.Get(j));
        NetDeviceContainer n_devs;
        if (netArch == "P2P" || netArch == "P2Pv6")
          n_devs = pointToPoint.Install(n_links);
        else if (netArch == "CSMA" || netArch == "CSMAv6") 
          n_devs = csma.Install (n_links);
        Devices.push_back(n_devs);
        /// Store devices to be fetched using node names
        DeviceMap[make_pair(arrayNamesCoords[i][0], arrayNamesCoords[j][0])] = n_devs;
        NS_LOG_INFO("matrix element [" << i << "][" << j << "] is 1");
      }
      else
      {
        NS_LOG_INFO("matrix element [" << i << "][" << j << "] is 0");
      }
    }
  }
  NS_LOG_INFO("");

  //--- set link error rate
  Ptr<RateErrorModel> em = CreateObject<RateErrorModel>();
  em->SetAttribute("ErrorRate", DoubleValue(stod(LinkErrorRate)));
  for (auto dev = Devices.begin(); dev != Devices.end(); ++dev)
  {
    (*dev).Get(1)->SetAttribute("ReceiveErrorModel", PointerValue(em));
    if (verbose > 1)
    {
      std::cout << "int(0) =  " << (*dev).Get(0)->GetAddress()
                << "  int(1) =  " << (*dev).Get(1)->GetAddress()
                << " ID = " << (*dev).Get(1)->GetNode()->GetId()
                << std::endl;
    }
  }

  //--- set Internet stack and IP address to the p2p/csma devices
  NS_LOG_INFO("Set internet stack and addresses.");
  internet.Install(NodeContainer::GetGlobal());
  for (auto dev = Devices.begin(); dev != Devices.end(); ++dev)
  {
    if(v4)
    {
      ipv4Address.Assign(*dev);
      ipv4Address.NewNetwork();
    }
    else
    {
      Ipv6InterfaceContainer i6 = ipv6Address.Assign(*dev);
      ipv6Address.NewNetwork();
    }
  }
  if (verbose > 1)
  {
    PrintIpAddresses(nodes, netArch);
  }

  //--- create map Ipv4/Ipv6 address to NodeId
  if (v4) mapIpv4NodeId = CreateMapIpv4NodeId(nodes);
  else  mapIpv6NodeId = CreateMapIpv6NodeId(nodes);

  // --- Global routing protocol for IP version 4 stacks
  // NS_LOG_INFO("Initialize Global Routing.");
  // Ipv4GlobalRoutingHelper::PopulateRoutingTables();

  //--- Output topology summary
  NS_LOG_INFO("Number of links in the adjacency matrix is: " << linkCount);
  NS_LOG_INFO("Number of all nodes is: " << nodes.GetN());

  // --- Allocate node positions
  NS_LOG_INFO("Allocate Positions to Nodes.");
  nodePositionAlloc = CreateObject<ListPositionAllocator>();
  for (size_t m = 0; m < arrayNodeCoords.size(); m++)
  {
    nodePositionAlloc->Add(Vector(arrayNodeCoords[m][0], arrayNodeCoords[m][1], 0));
    Ptr<Node> n0 = nodes.Get(m);
    Ptr<ConstantPositionMobilityModel> nLoc = n0->GetObject<ConstantPositionMobilityModel>();
    if (nLoc == 0)
    {
      nLoc = CreateObject<ConstantPositionMobilityModel>();
      n0->AggregateObject(nLoc);
    }
    Vector nVec(arrayNodeCoords[m][0], arrayNodeCoords[m][1], 0);
    NS_LOG_INFO("Node[" << m << "]: "
                        << "(" << arrayNodeCoords[m][0] << "," << arrayNodeCoords[m][1] << ")");
    nLoc->SetPosition(nVec);
  }
  mobility.SetPositionAllocator(nodePositionAlloc);
  mobility.Install(nodes);

  //--- sort array
  sort(nodeServerList.begin(), nodeServerList.end());
  //--- unique elements
  iList = unique(nodeServerList.begin(), nodeServerList.end());
  //--- resize list
  nodeServerList.resize(distance(nodeServerList.begin(), iList));

  //--- set regular trace file
  AsciiTraceHelper ascii;
  if (netArch == "P2P" || netArch == "P2Pv6")
    pointToPoint.EnableAsciiAll(ascii.CreateFileStream("traceNS3Netsim.tr"));
  else if (netArch == "CSMA" || netArch == "CSMAv6")
    csma.EnableAsciiAll(ascii.CreateFileStream ("traceNS3Netsim.tr"));
  // pointToPoint.EnablePcapAll("pcapNS3Netsim.pcap");
  //pointToPoint.EnablePcap("dse", 0, 0, true);
}

void NS3Netsim::create(string client, string server)
{
  NS_LOG_FUNCTION(this);
  bool found = false, v4 = false;
  if (netArch == "P2P" || netArch == "CSMA")  v4 = true;

  //---
  //--- update list of application connections
  //---
  vector<string> record;
  record.push_back(client);
  record.push_back(server);
  //--- Search for already existing connection
  for (auto rec = arrayAppConnections.begin(); rec != arrayAppConnections.end(); ++rec)
  {
    string clt = (*rec).front();
    string srv = (*rec).back();
    //--- connection already exist, break
    if ((clt.compare(client) == 0) && (srv.compare(server) == 0))
    {
      NS_LOG_DEBUG("NS3Netsim::create Connection already exist: " << client << " --> " << server << endl);
      found = true;
      break;
    }
  }

  //--- new connection, create entries
  if (found == false)
  {
    arrayAppConnections.push_back(record);

    // create server socket
    NS_LOG_INFO("Create server.");
    Ptr<Node> srvNode = Names::Find<Node>(server);

    // Check protocol

    //--- verify if server already exist
    std::vector<std::string>::iterator it = std::find(nodeServerList.begin(), nodeServerList.end(), server);
    //--- if not found
    if (it == nodeServerList.end())
    {
      // Create the server application
      if (v4)
      {
        AddressValue address = AddressValue(InetSocketAddress(Ipv4Address::GetAny(), sinkPort));
        setUpServer(address, tcpOrUdp, server);
      }
      else
      {
        AddressValue address = AddressValue(Inet6SocketAddress(Ipv6Address::GetAny(), sinkPort));
        setUpServer(address, tcpOrUdp, server);
      }
      NS_LOG_DEBUG("NS3Netsim::create Server: " << *iList << endl);
    }
    else
    { //--- end of server part
      NS_LOG_DEBUG("NS3Netsim::create Server already on the list: " << server << endl);
    }

    // create client socket
    NS_LOG_INFO("Create client.");
    Ptr<Node> dstNode = Names::Find<Node>(server);
    if (v4)
    {
      Ipv4InterfaceAddress sink_iaddr = dstNode->GetObject<Ipv4>()->GetAddress(1, 0);
      InetSocketAddress remote = InetSocketAddress(sink_iaddr.GetLocal(), sinkPort);
      setUpClient(AddressValue(remote), tcpOrUdp, server, client);
    }
    else
    {
      Ipv6InterfaceAddress sink_v6iaddr = dstNode->GetObject<Ipv6>()->GetAddress(1, 1);
      Inet6SocketAddress remote = Inet6SocketAddress(sink_v6iaddr.GetAddress(), sinkPort);
      setUpClient(AddressValue(remote), tcpOrUdp, server, client);
    }
  }

  // --- Static routing for IP version 4
  NS_LOG_INFO("Initialize Static Routing.");
  if(v4)
  {
    Ipv4StaticRoutingHelper ipv4StaticRouter;
    Ptr<Ipv4StaticRouting> staticRouting;
    string clt = client;
    string srv = server;
    string nextHop;
    Ptr <Node> desNode = Names::Find<Node>(server);
    Ptr <Ipv4> desIpv4 = desNode->GetObject<Ipv4> ();
    Ipv4Address destAddress = desIpv4->GetAddress(1, 0).GetLocal();
    Ptr <Node> srcNode = Names::Find<Node>(client);
    Ptr <Ipv4> srcIpv4 = srcNode->GetObject<Ipv4> ();
    Ipv4Address srcAddress = srcIpv4->GetAddress(1, 0).GetLocal();
    //--- create static routes from clients to servers and vice versa
    if (verbose > 2)  cout << "Connecting " << clt << " to " << srv << endl;
    while(nextHop != srv)
    {
      nextHop = FindNextHop(clt, srv, nodeAdjMatrix);
      if (verbose > 3)  cout << "Next hop for " << clt << " is: " << nextHop << endl;

      Ptr<Node> nextHopNode = Names::Find<Node>(nextHop);
      Ptr<Node> cltNode = Names::Find<Node>(clt);
      Ptr<Ipv4> nextHopIpv4 = nextHopNode->GetObject<Ipv4> ();
      Ptr<Ipv4> cltIpv4 = cltNode->GetObject<Ipv4> ();

      uint32_t hostIfIndex, hopIfIndex;
      // The interfaces are in reverse order
      if(DeviceMap.find(make_pair(clt, nextHop)) == DeviceMap.end())
      {
        NetDeviceContainer link_dev = DeviceMap[make_pair(nextHop, clt)];
        hostIfIndex = link_dev.Get(1)->GetIfIndex() + 1;
        hopIfIndex = link_dev.Get(0)->GetIfIndex() + 1;
      }
      else // The interfaces are in correct order
      {
        NetDeviceContainer link_dev = DeviceMap[make_pair(clt, nextHop)];
        hostIfIndex = link_dev.Get(0)->GetIfIndex() + 1;
        hopIfIndex = link_dev.Get(1)->GetIfIndex() + 1;
      }
      Ipv4Address nextHopAddress = nextHopIpv4->GetAddress(hopIfIndex, 0).GetLocal();
      staticRouting = ipv4StaticRouter.GetStaticRouting (cltIpv4);
      staticRouting->AddHostRouteTo(destAddress, nextHopAddress, hostIfIndex);
      Ipv4Address cltAddress = cltIpv4->GetAddress(hostIfIndex, 0).GetLocal();
      staticRouting = ipv4StaticRouter.GetStaticRouting (nextHopIpv4);
      staticRouting->AddHostRouteTo(srcAddress, cltAddress, hopIfIndex);
      if (verbose > 3)
      {
        cout << "Next Hop Address: " << nextHopAddress << endl;
        PrintRoutingTable(cltNode, v4);
      }
      clt = nextHop;
    }
  }
  else
  {
    Ipv6StaticRoutingHelper ipv6StaticRouter;
    Ptr<Ipv6StaticRouting> staticRouting;
    string clt = client;
    string srv = server;
    string nextHop;
    Ptr <Node> desNode = Names::Find<Node>(server);
    Ptr <Ipv6> desIpv6 = desNode->GetObject<Ipv6> ();
    Ipv6Address destAddress = desIpv6->GetAddress(1, 1).GetAddress();
    Ptr <Node> srcNode = Names::Find<Node>(client);
    Ptr <Ipv6> srcIpv6 = srcNode->GetObject<Ipv6> ();
    Ipv6Address srcAddress = srcIpv6->GetAddress(1, 1).GetAddress();
    //--- create static routes from clients to servers and vice versa
    if (verbose > 2)  cout << "Connecting " << clt << " to " << srv << endl;
    while(nextHop != srv)
    {
      nextHop = FindNextHop(clt, srv, nodeAdjMatrix);
      if (verbose > 3)  cout << "Next hop for " << clt << " is: " << nextHop << endl;

      Ptr<Node> nextHopNode = Names::Find<Node>(nextHop);
      Ptr<Node> cltNode = Names::Find<Node>(clt);
      Ptr<Ipv6> nextHopIpv6 = nextHopNode->GetObject<Ipv6> ();
      Ptr<Ipv6> cltIpv6 = cltNode->GetObject<Ipv6> ();

      uint32_t hostIfIndex, hopIfIndex;
      // The interfaces are in reverse order
      if(DeviceMap.find(make_pair(clt, nextHop)) == DeviceMap.end())
      {
        NetDeviceContainer link_dev = DeviceMap[make_pair(nextHop, clt)];
        hostIfIndex = link_dev.Get(1)->GetIfIndex() + 1;
        hopIfIndex = link_dev.Get(0)->GetIfIndex() + 1;
      }
      else // The interfaces are in correct order
      {
        NetDeviceContainer link_dev = DeviceMap[make_pair(clt, nextHop)];
        hostIfIndex = link_dev.Get(0)->GetIfIndex() + 1;
        hopIfIndex = link_dev.Get(1)->GetIfIndex() + 1;
      }
      Ipv6Address nextHopAddress = nextHopIpv6->GetAddress(hopIfIndex, 1).GetAddress();
      staticRouting = ipv6StaticRouter.GetStaticRouting (cltIpv6);
      staticRouting->AddHostRouteTo(destAddress, nextHopAddress, hostIfIndex);
      Ipv6Address cltAddress = cltIpv6->GetAddress(hostIfIndex, 1).GetAddress();
      staticRouting = ipv6StaticRouter.GetStaticRouting (nextHopIpv6);
      staticRouting->AddHostRouteTo(srcAddress, cltAddress, hopIfIndex);
      if (verbose > 3)
      {
        cout << "Next Hop Address: " << nextHopAddress << endl;
        PrintRoutingTable(cltNode, v4);
      }
      clt = nextHop;
    }
  }
}

void NS3Netsim::setUpServer(AddressValue address, string protocol, string server)
{
  // Where the returned application will be stored
  ApplicationContainer serverAppContainer;
  // Switch on the protocol passed in
  if (protocol == "tcp")
  {
    // Set the address with which the application should be created
    multiClientTcpServerHelper.SetAttribute("Local", address);
    serverAppContainer = multiClientTcpServerHelper.Install(server);
    // Set the call back to extract information from a packet and sent it to the upper layer
    Ptr<MultiClientTcpServer> serverAppAsCorrectType = DynamicCast<MultiClientTcpServer>(serverAppContainer.Get(0));
    // Set the function that should be called when the server receives a packet
    serverAppAsCorrectType->SetPacketReceivedCallBack(ExtractInformationFromPacketAndSendToUpperLayer);
  }
  else if (protocol == "udp")
  {
    // Set the address with which the application should be created
    if (v4) customUdpServerHelper.SetAttribute("Local", AddressValue(InetSocketAddress(Ipv4Address::GetAny(), sinkPort)));
    else  customUdpServerHelper.SetAttribute("Local", AddressValue(Inet6SocketAddress(Ipv6Address::GetAny(), sinkPort)));
    // Create a tcp container
    serverAppContainer = customUdpServerHelper.Install(server);
    // Set the call back to extract information from a packet and sent it to the upper layer
    Ptr<CustomUdpServer> serverAppAsCorrectType = DynamicCast<CustomUdpServer>(serverAppContainer.Get(0));
    // Set the function that should be called when the server receives a packet
    serverAppAsCorrectType->SetPacketReceivedCallBack(ExtractInformationFromPacketAndSendToUpperLayer);
  }
  else
  {
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

void NS3Netsim::setUpClient(AddressValue address, string protocol, string server, string client)
{
  // Get the server and the client nodes
  Ptr<Node> srcNode = Names::Find<Node>(client);
  Ptr<Node> dstNode = Names::Find<Node>(server);
  // Where the returned application will be stored
  ApplicationContainer clientAppContainer;
  // Switch on the protocol passed in
  if (protocol == "tcp")
  {
    // Create a tcp client
    tcpClientHelper.SetAttribute("Remote", address);
    clientAppContainer = tcpClientHelper.Install(client);
  }
  else if (protocol == "udp")
  {
    // Create a udp client
    customUdpClientHelper.SetAttribute("Remote", address);
    clientAppContainer = customUdpClientHelper.Install(client);
  }
  else
  {
    // If unknown protocol, stop and throw error
    NS_FATAL_ERROR("Invalid protocol passed in");
  }

  // Add the application to the container and start the application
  allApplications.Add(clientAppContainer.Get(0));
  clientAppContainer.Start(NanoSeconds(0.0));
}

void NS3Netsim::schedule(string src, string dst, string val, string val_time)
{
  if (verbose > 1)
  {
    std::cout << "NS3Netsim::schedule" << std::endl;
  }

  if (verbose > 1)
  {
    std::cout << "NS3Netsim::schedule NS3_Time: " << Simulator::Now().GetMilliSeconds()
              << " Event_Val_Time: " << val_time << std::endl;
    std::cout << "NS3Netsim::schedule("
              << "source=" << src
              << ", destination=" << dst
              << ", value=" << val
              << ", delay=" << val_time
              << ")" << std::endl;
  }

  if (tcpOrUdp == "tcp")
  {
    Ptr<Node> srcNode = Names::Find<Node>(src);
    Ptr<TcpClient> clientApp = DynamicCast<TcpClient>(srcNode->GetApplication(0));
    if (clientApp == 0)
    {
      clientApp = DynamicCast<TcpClient>(srcNode->GetApplication(1));
    }
    clientApp->ScheduleTransmit(val, val_time);
  }
  else if (tcpOrUdp == "udp")
  {
    Ptr<Node> srcNode = Names::Find<Node>(src);
    Ptr<CustomUdpClient> clientApp = DynamicCast<CustomUdpClient>(srcNode->GetApplication(0));
    if (clientApp == 0)
    {
      clientApp = DynamicCast<CustomUdpClient>(srcNode->GetApplication(1));
    }
    clientApp->ScheduleTransmit(val, val_time);
  }
}

std::string
NS3Netsim::runUntil(uint64_t time, string nextStop)
{
  if (verbose > 1)
  {
    std::cout << "NS3Netsim::runUntil(time=" << time << " + 1)" << std::endl;
    std::cout << "NS3Netsim::Max Advance time = " << nextStop << std::endl;
  }

  //--- run scheduler until a given time
  sim = DynamicCast<SmartgridDefaultSimulatorImpl>(Simulator::GetImplementation());
  uint64_t max_advance = stoul(nextStop);
  //--- "+1" because NS3 executes until a given time (not including)
  if (time < (uint64_t)stopTime-1)
    sim->RunUntil(MilliSeconds(time + 1));
  //--- Do not execute end time events to avoid socket wait problem
  else
    sim->RunUntil(MilliSeconds((uint64_t)stopTime-1));

  if (verbose > 3)
  {
    DataXCHG dataSnt;
    for (auto it = 0; it != dataXchgOutput.size(); ++it)
    {
      dataSnt = dataXchgOutput.front();
      cout << "NS3Netsim::runUntil NS3 OUTPUT Buffer Src: " << dataSnt.src
           << " Dst: " << dataSnt.dst
           << " Val: " << dataSnt.val
           << " Time: " << dataSnt.time
           << endl;
      dataXchgOutput.pop();
      dataXchgOutput.push(dataSnt);
    }
  }

  //--- Get the next new event
  uint64_t next_step = (uint64_t)sim->Next().GetMilliSeconds();
  if (verbose > 1)
  {
    std::cout << "NS3Netsim::runUntil After_run NS3 time: " << Simulator::Now().GetMilliSeconds() << std::endl;
    std::cout << "NS3Netsim::runUntil next event: " << next_step << std::endl;
  }
  //--- Return a step time so that Mosaik has to give "stop" command
  if (next_step == (uint64_t)stopTime-1)
    return std::to_string(next_step+1);
  else if (next_step > (uint64_t)stopTime-1)
  {
    if (time == (uint64_t)stopTime-1)
      return std::to_string((uint64_t)stopTime);
    else
      return std::to_string((uint64_t)stopTime-1);
  }
  return std::to_string(next_step);
}

int NS3Netsim::get_data(string &src, string &dst, string &val_v, string &val_t)
{
  int res;
  DataXCHG dataOut;

  if (verbose > 1)
  {
    std::cout << "NS3Netsim::get_data" << std::endl;
    std::cout << "NS3Netsim::get_data NS3-OUTPUT-QUEUE-SIZE: " << dataXchgOutput.size() << std::endl;
  }

  if (!dataXchgOutput.empty())
  {
    res = 1;
    dataOut = dataXchgOutput.front();
    dataXchgOutput.pop();
    src = dataOut.src;
    dst = dataOut.dst;
    val_v = dataOut.val;
    val_t = to_string(dataOut.time);
  }
  else
  {
    res = 0;
  }

  if (verbose > 2)
  {
    for (auto it = 0; it != dataXchgOutput.size(); ++it)
    {
      DataXCHG dataSnt = dataXchgOutput.front();
      if (dataSnt.src == src && dataSnt.dst == dst)
        cout << "NS3Netsim::get_data NS3 OUTPUT Buffer Src: " << dataSnt.src
             << " Dst: " << dataSnt.dst
             << " Val: " << dataSnt.val
             << " Time: " << dataSnt.time
             << endl;
      dataXchgOutput.pop();
      dataXchgOutput.push(dataSnt);
    }
  }

  return res;
}

bool NS3Netsim::checkEmptyDataOutput(void)
{
  return dataXchgOutput.empty();
}

int NS3Netsim::getSizeDataOutput(void)
{
  return dataXchgOutput.size();
}

int NS3Netsim::getSizeDataInput(void)
{
  return dataXchgInput.size();
}

double
NS3Netsim::getCurrentTime(void)
{
  return Simulator::Now().GetMilliSeconds();
}
