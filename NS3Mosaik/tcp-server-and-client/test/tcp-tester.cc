/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Add lines here
 * Copyright (c) 2020 Amrinder S. Grewal
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
 * Author:  Amrinder S. Grewal <asgrewal@ualberta.ca>
 * Date:    2020.05.18
 * Company: University of Alberta/Canada - Computing Science
 *
 * File modelled after star.cc
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/netanim-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/point-to-point-layout-module.h"
#include "ns3/simulator.h"
#include <string>
#include "ns3/Ptr.h"

// Network topology (default)
//
//        n2 n3 n4              .
//         \ | /                .
//          \|/                 .
//     n1--- n0---n5            .
//          /|\                 .
//         / | \                .
//        n8 n7 n6              .
// n0 will always exist and be the server, n1....nk will be the number of clients
// Having 0 clients is a possibility

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("TESTER");


void
ReceiveMessage (Ptr<Socket> socket)
{
  Address from;
  Ptr<Packet> packet = socket->RecvFrom (from);
  if (packet != 0) {
    packet->RemoveAllPacketTags ();
    packet->RemoveAllByteTags ();

    Ptr<Node> recvnode = socket->GetNode();
    uint8_t *buffer = new uint8_t[packet->GetSize()];
    packet->CopyData(buffer,packet->GetSize());
    std::string recMessage = std::string((char*)buffer);
    recMessage = recMessage.substr (0,packet->GetSize());

//  Ipv4Address srcIpv4Address = InetSocketAddress::ConvertFrom(from).GetIpv4();
//  uint32_t srcNodeId = mapIpv4NodeId[srcIpv4Address];

    //--- print received msg
    NS_LOG_DEBUG(
        "Pkt Rcv at "    << Simulator::Now ().GetMilliSeconds ()
                         << " dstAddr: "     << socket->GetNode ()->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()
                         << " srcAddr: "     << InetSocketAddress::ConvertFrom (from).GetIpv4()
                         << " Size: "        << packet->GetSize()
                         << " Payload: "     << recMessage
    );
  }
}


int
main (int argc, char *argv[])
{
  //
  // Default number of nodes in the star.  Overridable by command line argument.
  //
  uint32_t nSpokes = 10;

  CommandLine cmd;
  cmd.AddValue ("nSpokes", "Number of nodes to place in the star", nSpokes);
  cmd.Parse (argc, argv);

  LogComponentEnable ("MultiClientTcpServer", LOG_LEVEL_ALL);
  LogComponentEnable ("TESTER", LOG_LEVEL_DEBUG);
  LogComponentEnable ("TcpClient", LOG_LEVEL_ALL);
//  LogComponentEnable ("TcpL4Protocol", LOG_LEVEL_ALL);

  NS_LOG_INFO ("Build star topology.");
  PointToPointHelper pointToPoint;
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("2ms"));
  PointToPointStarHelper star (nSpokes, pointToPoint);

  NS_LOG_INFO ("Install internet stack on all nodes.");
  InternetStackHelper internet;
  star.InstallStack (internet);

  NS_LOG_INFO ("Assign IP Addresses.");
  star.AssignIpv4Addresses (Ipv4AddressHelper ("10.1.1.0", "255.255.255.0"));

  NS_LOG_INFO ("Create applications.");
  //
  // Create a packet sink on the star "hub" to receive packets.
  //
  uint16_t port = 50000;
  Address hubLocalAddress (InetSocketAddress (Ipv4Address::GetAny (), port));
  MultiClientTcpServerHelper multiClientTcpServerHelper (hubLocalAddress);
  ApplicationContainer hubApp = multiClientTcpServerHelper.Install (star.GetHub ());
  Ptr<MultiClientTcpServer> server = DynamicCast<MultiClientTcpServer> (hubApp.Get(0));
  server->SetPacketReceivedCallBack(&ReceiveMessage);

  hubApp.Start (Seconds (0.0));
  hubApp.Stop (Seconds (9.0));

  //
  // Create client applications to send TCP to the hub, one on each spoke node.
  //
  TcpClientHelper helper = TcpClientHelper(Address());
  ApplicationContainer spokeApps;
  for (uint32_t i = 0; i < star.SpokeCount (); ++i)
    {
      AddressValue remoteAddress (InetSocketAddress (star.GetHubIpv4Address(i), port));
      helper.SetAttribute("Remote", remoteAddress);
      helper.Install (star.GetSpokeNode (i));
      Ptr<TcpClient> client = DynamicCast<TcpClient> (star.GetSpokeNode(i)->GetApplication(0));

      for (int j = 0; j < 10000; j++) {
          Simulator::Schedule(
              MilliSeconds(1000),
              &TcpClient::ScheduleTransmit,
              client,
              std::to_string(i + 0.5),
              std::to_string(i + 2000)
          );
      }
      spokeApps.Add (ApplicationContainer(client));
    }
  spokeApps.Start (Seconds (0.0));
  spokeApps.Stop (Seconds (10.0));

  NS_LOG_INFO ("Enable static global routing.");
  //
  // Turn on global static routing so we can actually be routed across the star.
  //
  Ipv4GlobalRoutingHelper::PopulateRoutingTables ();

  NS_LOG_INFO ("Enable pcap tracing.");
  //
  // Do pcap tracing on all point-to-point devices on all nodes.
  //
  pointToPoint.EnablePcapAll ("star");

  NS_LOG_INFO ("Run Simulation.");
  Simulator::Run ();
  Simulator::Destroy ();
  NS_LOG_INFO ("Done.");

  return 0;
}