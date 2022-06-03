/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2022 Talha Ibn Aziz
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
 * Author:  Talha Ibn Aziz <taziz@ualberta.ca> <talhaibnaziz6343@gmail.com>
 * Date:    2022.03.03
 * Company: University of Alberta/Canada - Computing Science
 * 
 * Modelled after udp-echo-server.cc
 */

#include "ns3/log.h"
#include "ns3/ipv4-address.h"
#include "ns3/ipv6-address.h"
#include "ns3/address-utils.h"
#include "ns3/nstime.h"
#include "ns3/inet-socket-address.h"
#include "ns3/inet6-socket-address.h"
#include "ns3/socket.h"
#include "ns3/tcp-socket.h"
#include "ns3/simulator.h"
#include "ns3/socket-factory.h"
#include "ns3/packet.h"
#include "ns3/uinteger.h"

#include "tcp-server.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("TcpServer");

NS_OBJECT_ENSURE_REGISTERED (TcpServer);

TypeId
TcpServer::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::TcpServer")
    .SetParent<Application> ()
    .SetGroupName("Applications")
    .AddConstructor<TcpServer> ()
    .AddAttribute ("Port", "Port on which we listen for incoming packets.",
                   UintegerValue (9),
                   MakeUintegerAccessor (&TcpServer::m_port),
                   MakeUintegerChecker<uint16_t> ())
    .AddTraceSource ("Rx", "A packet has been received",
                     MakeTraceSourceAccessor (&TcpServer::m_rxTrace),
                     "ns3::Packet::TracedCallback")
    .AddTraceSource ("RxWithAddresses", "A packet has been received",
                     MakeTraceSourceAccessor (&TcpServer::m_rxTraceWithAddresses),
                     "ns3::Packet::TwoAddressTracedCallback")
  ;
  return tid;
}

TcpServer::TcpServer ()
{
  NS_LOG_FUNCTION (this);
}

TcpServer::~TcpServer()
{
  NS_LOG_FUNCTION (this);
  m_socket = 0;
  m_socket6 = 0;
  m_acceptedSocketList.clear();
}

Ptr<Socket>
TcpServer::GetListeningSocket (void) const
{
  NS_LOG_FUNCTION (this);
  if (m_socket != 0) 
    {
      return m_socket;
    }
  else 
    {
      return m_socket6;
    }
}

std::list<Ptr<Socket> >
TcpServer::GetAcceptedSockets(void) const
{
  NS_LOG_FUNCTION (this);
  return m_acceptedSocketList;
}


void
TcpServer::DoDispose (void)
{
  NS_LOG_FUNCTION (this);
  Application::DoDispose ();
}

void 
TcpServer::StartApplication (void)
{
  NS_LOG_FUNCTION (this);

  if (m_socket == 0)
    {
      TypeId tid = TypeId::LookupByName ("ns3::TcpSocketFactory");
      m_socket = Socket::CreateSocket (GetNode (), tid);
      InetSocketAddress local = InetSocketAddress (Ipv4Address::GetAny (), m_port);
      if (m_socket->Bind (local) == -1)
        {
          NS_FATAL_ERROR ("Failed to bind socket");
        }
      m_socket->Listen();
      m_socket->ShutdownSend ();
    }

  if (m_socket6 == 0)
    {
      TypeId tid = TypeId::LookupByName ("ns3::TcpSocketFactory");
      m_socket6 = Socket::CreateSocket (GetNode (), tid);
      Inet6SocketAddress local6 = Inet6SocketAddress (Ipv6Address::GetAny (), m_port);
      if (m_socket6->Bind (local6) == -1)
        {
          NS_FATAL_ERROR ("Failed to bind socket");
        }
      m_socket6->Listen();
      m_socket6->ShutdownSend ();
    }

  // Set the callback funcs for connection request and connection accept
  m_socket->SetAcceptCallback(
      MakeCallback (&TcpServer::HandleRequest, this),
      MakeCallback (&TcpServer::HandleAccept, this)
  );
  m_socket6->SetAcceptCallback(
      MakeCallback (&TcpServer::HandleRequest, this),
      MakeCallback (&TcpServer::HandleAccept, this)
  );

  // Set the callback funcs for connection close for the listening socket
  m_socket->SetCloseCallbacks(
      MakeCallback (&TcpServer::HandlePeerClose, this),
      MakeCallback (&TcpServer::HandlePeerError, this)
  );
  m_socket6->SetCloseCallbacks(
      MakeCallback (&TcpServer::HandlePeerClose, this),
      MakeCallback (&TcpServer::HandlePeerError, this)
  );

  m_socket->SetRecvCallback (MakeCallback (&TcpServer::HandleRead, this));
  m_socket6->SetRecvCallback (MakeCallback (&TcpServer::HandleRead, this));
}

void 
TcpServer::StopApplication ()
{
  NS_LOG_FUNCTION (this);
  // Iterate thorough and close all sockets that are still active.
  while(!m_acceptedSocketList.empty ()) //these are accepted sockets, close them
    {
      Ptr<Socket> acceptedSocket = m_acceptedSocketList.front ();
      m_acceptedSocketList.pop_front ();
      acceptedSocket->Close ();
    }

  if (m_socket != 0) 
    {
      m_socket->Close ();
      m_socket->SetRecvCallback (MakeNullCallback<void, Ptr<Socket> > ());
    }
  if (m_socket6 != 0) 
    {
      m_socket6->Close ();
      m_socket6->SetRecvCallback (MakeNullCallback<void, Ptr<Socket> > ());
    }
}

void 
TcpServer::HandleRead (Ptr<Socket> socket)
{
  NS_LOG_FUNCTION (this);
  // Call the callback in the simulator to let it know that a message has been received
  if (m_packetReceivedCallback != NULL)
    {
      m_packetReceivedCallback(socket);
    }
}

bool TcpServer::HandleRequest(Ptr<Socket> socket, const Address& from)
{
  NS_LOG_FUNCTION (this << socket);
  return true;
}

void
TcpServer::HandlePeerClose (Ptr<Socket> socket)
{
  NS_LOG_FUNCTION (this << socket);
}

void
TcpServer::HandlePeerError (Ptr<Socket> socket)
{
  NS_LOG_FUNCTION (this << socket);
}

void
TcpServer::HandleAccept (Ptr<Socket> socket, const Address& from)
{
  NS_LOG_FUNCTION (this << socket << from);
  socket->SetRecvCallback (MakeCallback (&TcpServer::HandleRead, this));
  socket->SetCloseCallbacks(
      MakeCallback (&TcpServer::HandlePeerClose, this),
      MakeCallback (&TcpServer::HandlePeerError, this)
  );
  m_acceptedSocketList.push_back (socket);
}


void
TcpServer::SetPacketReceivedCallBack(void (*callback)(Ptr<Socket> socket))
{
  m_packetReceivedCallback = callback;
}

} // Namespace ns3
