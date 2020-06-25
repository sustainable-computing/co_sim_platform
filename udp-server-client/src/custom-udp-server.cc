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
 */

#include "custom-udp-server.h"
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

using namespace ns3;
using namespace std;

NS_LOG_COMPONENT_DEFINE ("CustomUdpServer");
NS_OBJECT_ENSURE_REGISTERED (CustomUdpServer);

TypeId
CustomUdpServer::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::CustomUdpServer")
      .SetParent<Application> ()
      .SetGroupName("Applications")
      .AddConstructor<CustomUdpServer> ()
      .AddAttribute("Local",
                    "The value on which to Bind the rx socket.",
                    AddressValue (),
                    MakeAddressAccessor (&CustomUdpServer::m_local),
                    MakeAddressChecker())
      .AddTraceSource ("Rx", "A packet has been received",
                       MakeTraceSourceAccessor (&CustomUdpServer::m_rxTrace),
                       "ns3::Packet::TracedCallback")
      .AddTraceSource ("RxWithAddresses", "A packet has been received",
                       MakeTraceSourceAccessor (&CustomUdpServer::m_rxTraceWithAddresses),
                       "ns3::Packet::TwoAddressTracedCallback")
  ;
  return tid;
}

void
CustomUdpServer::HandleRead(Ptr<Socket> socket) {
  NS_LOG_FUNCTION (this);
  // Call the callback in the simulator to let it know that a message has been received
  if (m_packetReceivedCallback != NULL)
    {
      m_packetReceivedCallback(socket);
    }
}

void
CustomUdpServer::SetPacketReceivedCallBack(void (*callback)(Ptr<Socket> socket))
{
  m_packetReceivedCallback = callback;
}

void
CustomUdpServer::StartApplication (void)
{
  NS_LOG_FUNCTION(this);
  // Create the socket if it does not already exist
  if (m_socket == 0) {
      TypeId tid = TypeId::LookupByName ("ns3::UdpSocketFactory");
      m_socket = Socket::CreateSocket(GetNode(), tid);
      if (m_socket->Bind(m_local) == -1)
        {
          NS_FATAL_ERROR ("Failed to bind socket");
        }

      m_socket->Listen();
      m_socket->ShutdownSend ();
      // No need to worry about multi-cast, not appropriate for TCP
    }

  // Set the call back for packet reception for the listening socket
  m_socket->SetRecvCallback(
      MakeCallback(&CustomUdpServer::HandleRead, this)
  );
}

void
CustomUdpServer::StopApplication (void)
{
  // Close the socket
  if (m_socket != 0)
    {
      m_socket->Close ();
      m_socket->SetRecvCallback (MakeNullCallback<void, Ptr<Socket> > ());
    }
}