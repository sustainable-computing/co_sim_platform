/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
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
 * Date:    2020.06.09
 * Company: University of Alberta/Canada - Computing Science
 *
 * Modelled after udp-echo-client.cc
 */

#include "custom-udp-client.h"
#include "ns3/log.h"
#include "ns3/ipv4-address.h"
#include "ns3/nstime.h"
#include "ns3/inet-socket-address.h"
#include "ns3/inet6-socket-address.h"
#include "ns3/socket.h"
#include "ns3/simulator.h"
#include "ns3/socket-factory.h"
#include "ns3/packet.h"
#include "ns3/uinteger.h"
#include "ns3/trace-source-accessor.h"
#include "ns3/ipv4.h"
#include "ns3/log.h"
#include <fstream>

using namespace ns3;
using namespace std;

NS_LOG_COMPONENT_DEFINE ("CustomUdpClient");
NS_OBJECT_ENSURE_REGISTERED (CustomUdpClient);

TypeId
CustomUdpClient::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::CustomUdpClient")
      .SetParent<Application> ()
      .SetGroupName("Applications")
      .AddConstructor<CustomUdpClient> ()
      .AddAttribute ("Remote", "The address of the destination",
                     AddressValue (),
                     MakeAddressAccessor (&CustomUdpClient::m_peerAddress),
                     MakeAddressChecker ())
      .AddAttribute ("Local",
                     "The Address on which to bind the socket. If not set, it is generated automatically.",
                     AddressValue (),
                     MakeAddressAccessor (&CustomUdpClient::m_local),
                     MakeAddressChecker ())
      .AddTraceSource ("Tx", "A new packet is created and is sent",
                       MakeTraceSourceAccessor (&CustomUdpClient::m_txTrace),
                       "ns3::Packet::TracedCallback")
      .AddTraceSource ("Rx", "A packet has been received",
                       MakeTraceSourceAccessor (&CustomUdpClient::m_rxTrace),
                       "ns3::Packet::TracedCallback")
      .AddTraceSource ("TxWithAddresses", "A new packet is created and is sent",
                       MakeTraceSourceAccessor (&CustomUdpClient::m_txTraceWithAddresses),
                       "ns3::Packet::TwoAddressTracedCallback")
      .AddTraceSource ("RxWithAddresses", "A packet has been received",
                       MakeTraceSourceAccessor (&CustomUdpClient::m_rxTraceWithAddresses),
                       "ns3::Packet::TwoAddressTracedCallback")
  ;
  return tid;
}

void
CustomUdpClient::SendMessage (string message)
{
  NS_LOG_FUNCTION(this);
  if (m_socket != 0)
    {
      Ptr <Packet> sendPacket =
          Create<Packet> ((uint8_t *) message.c_str (), message.size ());
      m_socket->Send (sendPacket);

  ofstream filePacketsSent;
  filePacketsSent.open("packets_sent.pkt", std::ios_base::app);
  filePacketsSent << "time: " << Simulator::Now ().GetMilliSeconds ()
                      << " nodeId: " << m_socket->GetNode()->GetId()
                      << " nodeAddr: " << m_socket->GetNode ()->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()

                      << " MsgSize: " << message.size() << std::endl;
  filePacketsSent.close();
    }
}

void
CustomUdpClient::ScheduleTransmit (std::string val, std::string valTime)
{
  // Get the delay in time
  NS_LOG_FUNCTION(this);
  double schDelay = stod(valTime) - Simulator::Now ().GetMilliSeconds ();

  NS_LOG_DEBUG("CustomUdpClient:schedule NS3_Time: " << Simulator::Now ().GetMilliSeconds ()
                                               << " Event_Val_Time: " << valTime << " val " << val << " socket " << m_socket);

  NS_LOG_DEBUG("CustomUdpClient:schedule("
                   << ", value=" << val
                   << ", delay=" << schDelay
                   << ")");

  // Get the message ready
  std::string msgx = val + "&" + valTime;
  Simulator::Schedule(
      MilliSeconds(schDelay),
      &CustomUdpClient::SendMessage,
      this,
      msgx
  );
}

void
CustomUdpClient::StartApplication (void)
{
  NS_LOG_FUNCTION(this);

  // Make a socket if empty
  if (m_socket == 0)
    {
      TypeId tid = TypeId::LookupByName ("ns3::UdpSocketFactory");
      m_socket = Socket::CreateSocket (GetNode (), tid);
      if (Ipv4Address::IsMatchingType(m_peerAddress) == true)
        {
          if (m_socket->Bind () == -1)
            {
              NS_FATAL_ERROR ("Failed to bind socket");
            }
          m_socket->Connect (InetSocketAddress (Ipv4Address::ConvertFrom(m_peerAddress), m_peerPort));
        }
      else if (Ipv6Address::IsMatchingType(m_peerAddress) == true)
        {
          if (m_socket->Bind6 () == -1)
            {
              NS_FATAL_ERROR ("Failed to bind socket");
            }
          m_socket->Connect (Inet6SocketAddress (Ipv6Address::ConvertFrom(m_peerAddress), m_peerPort));
        }
      else if (InetSocketAddress::IsMatchingType (m_peerAddress) == true)
        {
          if (m_socket->Bind () == -1)
            {
              NS_FATAL_ERROR ("Failed to bind socket");
            }
          m_socket->Connect (m_peerAddress);
        }
      else if (Inet6SocketAddress::IsMatchingType (m_peerAddress) == true)
        {
          if (m_socket->Bind6 () == -1)
            {
              NS_FATAL_ERROR ("Failed to bind socket");
            }
          m_socket->Connect (m_peerAddress);
        }
      else
        {
          NS_LOG_DEBUG(this);
          NS_ASSERT_MSG (false, "Incompatible address type: " << m_peerAddress);
        }
    }
}

void
CustomUdpClient::StopApplication (void)
{
  NS_LOG_FUNCTION(this);

  // Close the socket if it was open
  if (m_socket != 0)
    {
      m_socket->Close ();
      m_socket = 0;
    }
}