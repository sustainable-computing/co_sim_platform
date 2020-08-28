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
	  .AddAttribute("LocalPrimary",
					"The value on which to Bind the rx socket.",
					AddressValue (),
					MakeAddressAccessor (&CustomUdpServer::m_LocalPrimary),
					MakeAddressChecker())
	  .AddAttribute("LocalWifi",
					"The value on which to Bind the rx socket.",
					AddressValue (),
					MakeAddressAccessor (&CustomUdpServer::m_LocalWifi),
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

CustomUdpServer::CustomUdpServer()
{
  NS_LOG_FUNCTION(this);
  // Set the socket to null
  m_socketPrimary = 0;
  m_socketWifi = 0;
  m_createWifiSocket = false;
}

CustomUdpServer::~CustomUdpServer()
{
  NS_LOG_FUNCTION (this);
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
  if (m_socketPrimary == 0)
  {
	m_socketPrimary = CreateSocket(m_LocalPrimary);
  }

  if (m_socketWifi == 0 && m_createWifiSocket == true)
  {
	m_socketWifi = CreateSocket(m_LocalWifi);
  }
}

Ptr<Socket>
CustomUdpServer::CreateSocket(const Address bindTo)
{
  NS_LOG_FUNCTION(this);
  Ptr<Socket> socket;
  // Create a socket
  TypeId tid = TypeId::LookupByName ("ns3::UdpSocketFactory");
  socket = Socket::CreateSocket(GetNode(), tid);
  // Bind teh socket
  if (socket->Bind(bindTo) == -1)
  {
    NS_FATAL_ERROR ("Failed to bind socket");
  }

  // Tell the socket to listen
  socket->Listen();
  socket->ShutdownSend ();
  // No need to worry about multi-cast, not appropriate for TCP

  // Set the call back for packet reception for the listening socket
  socket->SetRecvCallback(
	  MakeCallback(&CustomUdpServer::HandleRead, this)
  );

  return socket;
}

void
CustomUdpServer::StopApplication (void)
{
  // Close the socket
  if (m_socketPrimary != 0)
  {
    CloseSocket(m_socketPrimary);
  }

  if (m_socketWifi != 0)
  {
	CloseSocket(m_socketWifi);
  }
}

void
CustomUdpServer::CloseSocket(Ptr<Socket> socket)
{
  NS_LOG_FUNCTION(this);
  socket->Close ();
  socket->SetRecvCallback (MakeNullCallback<void, Ptr<Socket> > ());
}

void
CustomUdpServer::SetCreateWifiSocket(bool enable)
{
  NS_LOG_FUNCTION(this);
  m_createWifiSocket = enable;
}

bool
CustomUdpServer::GetCreateWifiSocket(void)
{
  NS_LOG_FUNCTION(this);
  return m_createWifiSocket;
}