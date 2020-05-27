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
 * Date:    2020.05.13
 * Company: University of Alberta/Canada - Computing Science
 *
 * Modelled after udp-echo-client.cc
 */


#include <iostream>
#include "ns3/log.h"
#include "ns3/ipv4-address.h"
#include "ns3/ipv6-address.h"
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
#include "tcp-client.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("TcpClient");
NS_OBJECT_ENSURE_REGISTERED (TcpClient);

TypeId
TcpClient::GetTypeId(void)
{
  static TypeId tid = TypeId ("ns3::TcpClient")
    .SetParent<Application> ()
    .SetGroupName("Applications")
    .AddConstructor<TcpClient> ()
    .AddAttribute ("Remote", "The address of the destination",
                     AddressValue (),
                     MakeAddressAccessor (&TcpClient::m_peerAddress),
                     MakeAddressChecker ())
      .AddAttribute ("Local",
                     "The Address on which to bind the socket. If not set, it is generated automatically.",
                     AddressValue (),
                     MakeAddressAccessor (&TcpClient::m_local),
                     MakeAddressChecker ())
      .AddTraceSource ("Tx", "A new packet is created and is sent",
                       MakeTraceSourceAccessor (&TcpClient::m_txTrace),
                       "ns3::Packet::TracedCallback")
      .AddTraceSource ("Rx", "A packet has been received",
                       MakeTraceSourceAccessor (&TcpClient::m_rxTrace),
                       "ns3::Packet::TracedCallback")
      .AddTraceSource ("TxWithAddresses", "A new packet is created and is sent",
                       MakeTraceSourceAccessor (&TcpClient::m_txTraceWithAddresses),
                       "ns3::Packet::TwoAddressTracedCallback")
      .AddTraceSource ("RxWithAddresses", "A packet has been received",
                       MakeTraceSourceAccessor (&TcpClient::m_rxTraceWithAddresses),
                       "ns3::Packet::TwoAddressTracedCallback")
  ;

  return tid;
}

TcpClient::TcpClient()
{
  NS_LOG_FUNCTION(this);
  m_socket = 0;
  m_sendEvent = EventId ();
}

TcpClient::~TcpClient()
{
  NS_LOG_FUNCTION (this);
}

void
TcpClient::SetRemote(Address ip, uint16_t port)
{
  // Save address and port of remote
  NS_LOG_FUNCTION (this << ip << port);
  m_peerAddress = ip;
  m_peerPort = port;
}

void
TcpClient::SetRemote (Address addr)
{
  // Save address of remote
  NS_LOG_FUNCTION (this << addr);
  m_peerAddress = addr;
}

void
TcpClient::DoDispose (void)
{
  // Dispose of the object
  NS_LOG_FUNCTION (this);
  Application::DoDispose ();
}

void
TcpClient::StartApplication (void)
{
  NS_LOG_FUNCTION(this);

  // Make a socket if empty
  if (m_socket == 0)
    {
      TypeId tid = TypeId::LookupByName ("ns3::TcpSocketFactory");
      m_socket = Socket::CreateSocket (GetNode (), tid);
      // Confirm the peer is compatible with this server
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
          NS_ASSERT_MSG (false, "Incompatible address type: " << m_peerAddress);
        }
    }
}

void
TcpClient::StopApplication()
{
  NS_LOG_FUNCTION(this);

  // Close the socket if it was open
  if (m_socket != 0)
    {
      m_socket->Close();
      m_socket = 0;
    }

    Simulator::Cancel(m_sendEvent);
}

void
TcpClient::ScheduleTransmit(std::string val, std::string valTime) {
  NS_LOG_FUNCTION(this);

  // Get the delay in time
  double schDelay = std::stod(valTime) - Simulator::Now ().GetMilliSeconds ();

  NS_LOG_DEBUG("TcpClient:schedule NS3_Time: " << Simulator::Now ().GetMilliSeconds ()
                                                << " Event_Val_Time: " << valTime);
  NS_LOG_DEBUG("TcpClient:schedule("
                   << "source="   << m_socket->GetNode ()
                   << ", value=" << val
                   << ", delay=" << schDelay
                   << ")");

  // Get the message ready
  std::string msgx = val + "&" + valTime;

  // Schedule the message to be send
  Simulator::ScheduleWithContext (GetNode()->GetId(),
                                  MilliSeconds(schDelay),
                                  &TcpClient::SendMessage,
                                  this,
                                  msgx
  );
}

void
TcpClient::SendMessage (std::string message)
{
  Ptr<Packet> sendPacket =
      Create<Packet> ((uint8_t*)message.c_str(),message.size());

  m_socket->Send (sendPacket);
  Address addr;
  m_socket->GetPeerName (addr);
  InetSocketAddress iaddr = InetSocketAddress::ConvertFrom (addr);

  //--- print sending info
  NS_LOG_DEBUG(
      "Pkt Snt at "
          << Simulator::Now ().GetMilliSeconds ()
          << " nodeName: "
          << m_socket->GetNode ()
          << " nodeId: "
          << m_socket->GetNode()->GetId()
          << " nodeAddr: "
          << m_socket->GetNode ()->GetObject<Ipv4>()->GetAddress(1,0).GetLocal()
          << " destAddr: "
          << iaddr.GetIpv4 ()
          << " Size: "
          << sendPacket->GetSize()
          << " MsgSize "
          << message.size()
  );
}
