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
 */


//--- Includes ---//
#include <cstdio>
#include "NS3Netsim.h"
#include "ns3-helper.h"
#include "ns3/smartgrid-default-simulator-impl.h"

using namespace std;
using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("SmartgridNs3Main");
std::string fileNameReceived = "packets_received.pkt";
std::string fileNameSent = "packets_sent.pkt";

void
SendMessage (Ptr<Socket> socket, string message)
{
  Ptr<Packet> sendPacket =
      Create<Packet> ((uint8_t*)message.c_str(),message.size());

  socket->Send (sendPacket);

  //--- print sending info
  NS_LOG_DEBUG(
      "Pkt Snt at "
          << Simulator::Now ().GetMilliSeconds ()
          << " nodeName: "
          << Names::FindName(socket->GetNode ())
          << " nodeId: "
          << socket->GetNode()->GetId()
          << " nodeAddr: "
          << socket->GetNode ()->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()
          << " Size: "
          << sendPacket->GetSize()
          << " MsgSize "
          << message.size()
          << endl;
  );
//  ofstream filePacketsSent;
//  filePacketsSent.open(fileNameSent, std::ios_base::app);
//  filePacketsSent << "time: " << Simulator::Now ().GetMilliSeconds ()
//                  << " nodeId: " << socket->GetNode()->GetId()
//                  << " nodeAddr: " << socket->GetNode ()->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()
//                  << " MsgSize: " << message.size() << std::endl;
//  filePacketsSent.close();
}


void
ReceiveMessage (Ptr<Socket> socket)
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

  Ipv4Address srcIpv4Address = InetSocketAddress::ConvertFrom (from).GetIpv4();
  uint32_t srcNodeId = mapIpv4NodeId[srcIpv4Address];

  //--- print received msg
  NS_LOG_DEBUG(
      "Pkt Rcv at "    << Simulator::Now ().GetMilliSeconds ()
                       << " by nodeName: " << Names::FindName(socket->GetNode ())
                       << " dstNodeId: "   << socket->GetNode()->GetId()
                       << " dstAddr: "     << socket->GetNode ()->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()
                       << " srcNodeId: "   << srcNodeId
                       << " srcAddr: "     << InetSocketAddress::ConvertFrom (from).GetIpv4()
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
  DataXCHG dataRcv = { Names::FindName(NodeList::GetNode(srcNodeId)),
                       Names::FindName(socket->GetNode ()),
                       val,
                       stoll(val_time)
  };
  dataXchgOutput.push_back(dataRcv);
//  ofstream filePacketsReceived;
//  filePacketsReceived.open(fileNameReceived, std::ios_base::app);
//  std::replace( recMessage.begin(), recMessage.end(), '\n', ' ');
//  filePacketsReceived << "time: " << Simulator::Now ().GetMilliSeconds ()
//                      << " dstNodeId: "   << socket->GetNode()->GetId()
//                      << " dstAddr: "     << socket->GetNode ()->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()
//                      << " srcNodeId: "   << srcNodeId
//                      << " srcAddr: "     << InetSocketAddress::ConvertFrom (from).GetIpv4()
//                      << " Payload: "     << recMessage
//                      << " MsgSize: " << recMessage.size() << std::endl;
//  filePacketsReceived.close();
}


NS3Netsim::NS3Netsim():
    linkCount(0), sinkPort(0),  startTime(0), verbose (0)
{
  //--- setup simulation type
  GlobalValue::Bind ("SimulatorImplementationType",
                     StringValue ("ns3::SmartgridDefaultSimulatorImpl"));
  LogComponentEnable("Simulator", LOG_LEVEL_INFO);
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
                 int verb)
{

  // Delete the files with the packets sent and packets received
  remove(fileNameReceived.c_str());
  remove(fileNameSent.c_str());
  //--- verbose level
  verbose = verb;

  if (verbose > 1) {
      std::cout << "NS3Netsim::init" << std::endl;
    }

  // --- generate different seed each time
  srand ( (unsigned)time ( NULL ) );

  //--- set link properties
  LinkRate  = "512Kbps";
  LinkDelay = "15ms";
  LinkErrorRate = "0.00001";
//  LinkErrorRate = "0.00001";
  linkCount = 0;

  //--- set devices properties
  ipv4Address.SetBase ("10.0.0.0", "255.255.255.252");

  //--- set application destination port
  sinkPort = 3030;

  //--- simulation parameters
  startTime  = start_time;

  //--- set configuration file names
  nodeAdjMatrixFilename   = f_adjmat;
  nodeCoordinatesFilename = f_coords;
  appConnectionsFilename  = f_appcon;

  if (verbose > 1) {
      std::cout << "===>>> NS3Netsim::init(\n"
                << "adjmat_file="   << nodeAdjMatrixFilename
                << ",\n coords_file=" << nodeCoordinatesFilename
                << ",\n appcon_file=" << appConnectionsFilename
                << ")" << std::endl;
    }

  //--- load adjacency matrix
  NS_LOG_INFO ("Load node adjacency matrix");
  nodeAdjMatrix = ReadNodeAdjMatrix (nodeAdjMatrixFilename);
  if (verbose > 8) {
      PrintNodeAdjMatrix (nodeAdjMatrixFilename.c_str (), nodeAdjMatrix);
    }

  //--- load node coordinates and names
  NS_LOG_INFO ("Load node names and coordinates");
  arrayNamesCoords = ReadCoordinatesFile (nodeCoordinatesFilename);
  for(auto it = arrayNamesCoords.begin(); it != arrayNamesCoords.end(); it++) {
      vector<double> row;
      row.push_back(   atof( (*it)[1].c_str() )  );
      row.push_back(   atof( (*it)[2].c_str() )  );
      arrayNodeCoords.push_back(row);
    }
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

  //--- create network topology
  NS_LOG_INFO ("Create Links Between Nodes.");
  pointToPoint.SetDeviceAttribute  ("DataRate", StringValue (LinkRate));
  pointToPoint.SetChannelAttribute ("Delay",    StringValue (LinkDelay));
  for (size_t i = 0; i < nodeAdjMatrix.size (); i++)
    {
      for (size_t j = i; j < nodeAdjMatrix[i].size (); j++)
        {
          if (nodeAdjMatrix[i][j] == 1)
            {
              linkCount++;
              NodeContainer n_links = NodeContainer (nodes.Get (i), nodes.Get (j));
              NetDeviceContainer n_devs = pointToPoint.Install (n_links);
              p2pDevices.push_back(n_devs);
              NS_LOG_INFO ("matrix element [" << i << "][" << j << "] is 1");
            }
          else
            {
              NS_LOG_INFO ("matrix element [" << i << "][" << j << "] is 0");
            }
        }
    }



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


  //--- set Internet stack and IP address to the p2p devices
  NS_LOG_INFO ("Set internet stack and addresses.");
  internet.Install (NodeContainer::GetGlobal ());
  for (auto dev = p2pDevices.begin(); dev != p2pDevices.end(); ++dev)
    {
      ipv4Address.Assign (*dev);
      ipv4Address.NewNetwork ();
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


  //--- set regular trace file
  AsciiTraceHelper ascii;
  pointToPoint.EnableAsciiAll (ascii.CreateFileStream ("traceNS3Netsim.tr"));
  //pointToPoint.EnablePcapAll("pcapNS3Netsim.pcap");
  //pointToPoint.EnablePcap("dse", 0, 0, true);


}


void
NS3Netsim::create (string client, string server)
{
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
          if (verbose > 1) {
              cout << "NS3Netsim::create Connection already exist: " << client << " --> " << server << endl;
            }
          found = true;
          break;
        }
    }

  //--- new connection, create entries
  if(found == false) {
      arrayAppConnections.push_back(record);

      //---
      //--- create server socket
      //---
      NS_LOG_INFO ("Create server socket.");
      Ptr<Node> srvNode = Names::Find<Node>(server);

      //--- verify if server already exist
      std::vector<std::string>::iterator it = std::find(nodeServerList.begin(), nodeServerList.end(), server);
      //--- if not found
      if(it == nodeServerList.end()) {
          Ptr<Socket> recvSink = Socket::CreateSocket (srvNode, TypeId::LookupByName ("ns3::UdpSocketFactory"));
          InetSocketAddress local = InetSocketAddress (Ipv4Address::GetAny (), sinkPort);
          recvSink->Bind (local);
          recvSink->SetRecvCallback (MakeCallback (&ReceiveMessage));
          //--- update server node list
          nodeServerList.push_back(server);

          //--- sort array
          sort(nodeServerList.begin(), nodeServerList.end());

          if (verbose > 1){
              for (iList = nodeServerList.begin(); iList != nodeServerList.end(); ++iList)
                {
                  cout << "NS3Netsim::create Server: " << *iList << endl;
                }
            }

        } else { 		//--- end of server part
          if (verbose > 1){
              cout << "NS3Netsim::create Server already on the list: " << server << endl;
            }
        }


      //---
      //--- create client socket
      //---
      NS_LOG_INFO ("Create client sockets.");
      if (verbose > 1){
          cout << "NS3Netsim::create  Create client socket" << endl;
        }

      //--- get src and dst nodes from application connections
      Ptr<Node> srcNode = Names::Find<Node>(client);
      Ptr<Node> dstNode = Names::Find<Node>(server);

      //--- create  udp socket
      Ptr<Socket> source = Socket::CreateSocket (srcNode, TypeId::LookupByName ("ns3::UdpSocketFactory"));
      Ipv4InterfaceAddress sink_iaddr = dstNode->GetObject<Ipv4>()->GetAddress (1,0);
      InetSocketAddress remote = InetSocketAddress (sink_iaddr.GetLocal(), sinkPort);


      source->Connect (remote);

      //--- insert socket mapping Node --> Socket
      mapNodeSocket[srcNode->GetId()] = source;

      //--- log entry
      for (uint32_t appConn = 0; appConn < arrayAppConnections.size (); appConn++)
        {
          NS_LOG_DEBUG(
              arrayAppConnections[appConn][0] << " --> " << arrayAppConnections[appConn][1]
                                              << " srcAddr: " << srcNode->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()
                                              << " dstAddr: " << dstNode->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()
                                              << " remote: " << remote
                                              << " source: " << source
                                              << endl;
          );
        }
    } //--- end found === false

}


void
NS3Netsim::schedule (string src, string dst, string val, string val_time)
{
  if (verbose > 1) {
      std::cout << "NS3Netsim::schedule" << std::endl;
    }

  double schDelay = stod(val_time) - Simulator::Now ().GetMilliSeconds ();

  if (verbose > 1) {
      std::cout << "NS3Netsim::schedule NS3_Time: " << Simulator::Now ().GetMilliSeconds ()
                << " Event_Val_Time: " << val_time << std::endl;
      std::cout << "NS3Netsim::schedule("
                << "source="   << src
                << ", destination=" << dst
                << ", value=" << val
                << ", delay=" << schDelay
                << ")" << std::endl;
    }

  Ptr<Node> srcNode = Names::Find<Node>(src);
  Ptr<Node> dstNode = Names::Find<Node>(dst);

  Ptr<Socket> srcSocket = mapNodeSocket[srcNode->GetId ()];

  //--- send value and its timestamp
  string msgx = val + "&" + val_time;

  Simulator::ScheduleWithContext (srcNode->GetId (),
                                  MilliSeconds(schDelay),
                                  &SendMessage,
                                  srcSocket,
                                  msgx
  );

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

