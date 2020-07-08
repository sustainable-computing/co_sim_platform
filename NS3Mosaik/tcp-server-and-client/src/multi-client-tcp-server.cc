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
 * Modelled after packet-sink.cc
 */

#include "ns3/address.h"
#include "ns3/address-utils.h"
#include "ns3/socket-factory.h"
#include "multi-client-tcp-server.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("MultiClientTcpServer");
NS_OBJECT_ENSURE_REGISTERED (MultiClientTcpServer);

TypeId
MultiClientTcpServer::GetTypeId (void)
{
  static TypeId tid = TypeId("ns3::MultiClientTcpServer")
      .SetParent<Application> ()
      .SetGroupName("Applications")
      .AddConstructor<MultiClientTcpServer> ()
      .AddAttribute("LocalIpv4",
                    "The value on which to Bind the rx socket.",
                    AddressValue (),
                    MakeAddressAccessor (&MultiClientTcpServer::m_localIpv4),
                    MakeAddressChecker())
	  .AddAttribute("LocalIpv6",
					"The value on which to Bind the rx socket.",
					AddressValue (),
					MakeAddressAccessor (&MultiClientTcpServer::m_localIpv6),
					MakeAddressChecker())
      .AddTraceSource("Rx",
                      "A packet has been received",
                      MakeTraceSourceAccessor (&MultiClientTcpServer::m_rxTrace),
                      "ns3::Packet::AddressTracedCallback")
      .AddTraceSource ("RxWithAddresses", "A packet has been received",
                       MakeTraceSourceAccessor (&MultiClientTcpServer::m_rxTraceWithAddresses),
                       "ns3::Packet::TwoAddressTracedCallback")
  ;

  return tid;
}

MultiClientTcpServer::MultiClientTcpServer()
{
  NS_LOG_FUNCTION(this);
  // Set the socket to null
  m_listeningSocketIpv4 = 0;
  m_listeningSocketIpv6 = 0;
  m_packetReceivedCallback = 0;
}

MultiClientTcpServer::~MultiClientTcpServer()
{
  NS_LOG_FUNCTION (this);
}

Ptr<Socket>
MultiClientTcpServer::GetListeningSocketIpv4 (void) const
{
  NS_LOG_FUNCTION (this);
  return m_listeningSocketIpv4;
}

Ptr<Socket>
MultiClientTcpServer::GetListeningSocketIpv6 (void) const
{
  NS_LOG_FUNCTION (this);
  return m_listeningSocketIpv6;
}

std::list<Ptr<Socket> >
MultiClientTcpServer::GetAcceptedSockets(void) const
{
  NS_LOG_FUNCTION (this);
  return m_acceptedSocketList;
}

void
MultiClientTcpServer::DoDispose (void)
{
  NS_LOG_FUNCTION (this);
  // Clear the listening socket
  m_listeningSocketIpv4 = 0;
  m_listeningSocketIpv6 = 0;
  // Clear the accepted socket
  m_acceptedSocketList.clear ();

  // chain up
  Application::DoDispose ();
}

void
MultiClientTcpServer::SetPacketReceivedCallBack(void (*callback)(Ptr<Socket> socket))
{
  m_packetReceivedCallback = callback;
}

// Application Methods
void
MultiClientTcpServer::StartApplication()
{
  NS_LOG_FUNCTION(this);
  // Create ipv4 listening socket if it does not exist
  if (m_listeningSocketIpv4 == 0) {
	m_listeningSocketIpv4 = CreateListeningSocket(m_localIpv4);
  }

  // Create ipv6 listening socket if it does not exist
  if (m_listeningSocketIpv6 == 0) {
	m_listeningSocketIpv6 = CreateListeningSocket(m_localIpv6);
  }
}

Ptr<Socket>
MultiClientTcpServer::CreateListeningSocket(const Address bindTo)
{
  NS_LOG_FUNCTION(this);
  // Create the socket
  TypeId tid = TypeId::LookupByName ("ns3::TcpSocketFactory");
  Ptr<Socket> socket = Socket::CreateSocket(GetNode(), tid);
  // Bind the socket
  if (socket->Bind(bindTo) == -1)
  {
    NS_FATAL_ERROR ("Failed to bind socket");
  }

  // Tell the socket to start listening
  socket->Listen();
  socket->ShutdownSend ();

  // Set the callback funcs for connection request and connection accept
  socket->SetAcceptCallback(
	  MakeCallback (&MultiClientTcpServer::HandleRequest, this),
	  MakeCallback (&MultiClientTcpServer::HandleAccept, this)
  );
  // Set the callback funcs for connection close for the listening socket
  socket->SetCloseCallbacks(
	  MakeCallback (&MultiClientTcpServer::HandlePeerClose, this),
	  MakeCallback (&MultiClientTcpServer::HandlePeerError, this)
  );
  // Set the call back for packet reception for the listening socket
  socket->SetRecvCallback(
	  MakeCallback(&MultiClientTcpServer::HandleRead, this)
  );

  return socket;
}

void
MultiClientTcpServer::StopApplication()
{
  NS_LOG_FUNCTION (this);
  // Iterate thorough and close all sockets that are still active.
  while(!m_acceptedSocketList.empty ()) //these are accepted sockets, close them
  {
    Ptr<Socket> acceptedSocket = m_acceptedSocketList.front ();
    m_acceptedSocketList.pop_front ();
    acceptedSocket->Close ();
  }

  // Close the listening sockets
  if (m_listeningSocketIpv4 != 0)
  {
    CloseListeningSocket(m_listeningSocketIpv4);
  }
  if (m_listeningSocketIpv6 != 0)
  {
	CloseListeningSocket(m_listeningSocketIpv6);
  }
}

void
MultiClientTcpServer::CloseListeningSocket(Ptr<Socket> socket)
{
  NS_LOG_FUNCTION(this);
  socket->Close ();
  socket->SetAcceptCallback (
  	MakeNullCallback<bool, Ptr<Socket>, const Address& > (),
  	MakeNullCallback<void, Ptr<Socket>, const Address & > ());
  socket->SetCloseCallbacks (
  	MakeNullCallback<void, Ptr<Socket> > (),
  	MakeNullCallback<void, Ptr<Socket> > ());
  socket->SetRecvCallback (MakeNullCallback<void, Ptr<Socket> > ());
}

bool MultiClientTcpServer::HandleRequest(Ptr<Socket> socket, const Address& from)
{
  NS_LOG_FUNCTION (this << socket);
  return true;
}

void
MultiClientTcpServer::HandlePeerClose (Ptr<Socket> socket)
{
  NS_LOG_FUNCTION (this << socket);
}

void
MultiClientTcpServer::HandlePeerError (Ptr<Socket> socket)
{
  NS_LOG_FUNCTION (this << socket);
}

void
MultiClientTcpServer::HandleAccept (Ptr<Socket> socket, const Address& from)
{
  NS_LOG_FUNCTION (this << socket << from);
  socket->SetRecvCallback (MakeCallback (&MultiClientTcpServer::HandleRead, this));
  socket->SetCloseCallbacks(
      MakeCallback (&MultiClientTcpServer::HandlePeerClose, this),
      MakeCallback (&MultiClientTcpServer::HandlePeerError, this)
  );
  m_acceptedSocketList.push_back (socket);
}

void
MultiClientTcpServer::HandleRead(Ptr<Socket> socket) {
  NS_LOG_FUNCTION (this);
  // Call the callback in the simulator to let it know that a message has been received
  if (m_packetReceivedCallback != NULL)
    {
      m_packetReceivedCallback(socket);
    }
}
