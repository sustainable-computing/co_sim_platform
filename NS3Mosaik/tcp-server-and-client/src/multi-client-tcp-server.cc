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
#include "ns3/log.h"
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
      .AddAttribute("Local",
                    "The value on which to Bind the rx socket.",
                    AddressValue (),
                    MakeAddressAccessor (&MultiClientTcpServer::m_local),
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
  m_listeningSocket = 0;
  m_packetReceivedCallback = 0;
}

MultiClientTcpServer::~MultiClientTcpServer()
{
  NS_LOG_FUNCTION (this);
}

Ptr<Socket>
MultiClientTcpServer::GetListeningSocket (void) const
{
  NS_LOG_FUNCTION (this);
  return m_listeningSocket;
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
  m_listeningSocket = 0;
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
  // Create the socket if it does not already exist
  if (m_listeningSocket == 0) {
      TypeId tid = TypeId::LookupByName ("ns3::TcpSocketFactory");
      m_listeningSocket = Socket::CreateSocket(GetNode(), tid);
      if (m_listeningSocket->Bind(m_local) == -1)
        {
          NS_FATAL_ERROR ("Failed to bind socket");
        }

      m_listeningSocket->Listen();
      m_listeningSocket->ShutdownSend ();
      // No need to worry about multi-cast, not appropriate for TCP
    }

  // Set the callback funcs for connection request and connection accept
  m_listeningSocket->SetAcceptCallback(
      MakeCallback (&MultiClientTcpServer::HandleRequest, this),
      MakeCallback (&MultiClientTcpServer::HandleAccept, this)
  );

  // Set the callback funcs for connection close for the listening socket
  m_listeningSocket->SetCloseCallbacks(
      MakeCallback (&MultiClientTcpServer::HandlePeerClose, this),
      MakeCallback (&MultiClientTcpServer::HandlePeerError, this)
  );

  // Set the call back for packet reception for the listening socket
  m_listeningSocket->SetRecvCallback(
      MakeCallback(&MultiClientTcpServer::HandleRead, this)
  );
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

  // Close the listening socket
  if (m_listeningSocket != 0)
    {
      m_listeningSocket->Close ();
      m_listeningSocket->SetRecvCallback (MakeNullCallback<void, Ptr<Socket> > ());
    }
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