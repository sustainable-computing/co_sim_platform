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
 * Modelled after packet-sink.h
 */

#ifndef _MULTI_CLIENT_TCP_SERVER_H_
#define _MULTI_CLIENT_TCP_SERVER_H_

#include "ns3/core-module.h"
#include "ns3/socket.h"
#include "ns3/application.h"
#include "ns3/address.h"
#include "ns3/ptr.h"

using namespace ns3;
/**
 * \brief Application server that allows multiple simultaneous TCP connection.
 *
 * A single TCP socket is used to listen to incoming connections, then a new
 * socket is created after a connection has been accepted to continue
 * communicating with a client whose connection has already been accepted.
 *
 * This application was created to work with CoSimul_Platform to allow
 * reception of TCP packets from multiple sensors.
 *
 * Modelled after packet-sink.h
 */
class MultiClientTcpServer: public Application
{
 public:
  /**
   * \brief Get the type ID.
   * \return the object TypeID
   */
  static TypeId GetTypeId (void);

  MultiClientTcpServer ();
  virtual ~MultiClientTcpServer ();

  /**
   * \return pointer to the listening socket with ipv4 address
   */
  Ptr<Socket> GetListeningSocketIpv4 (void) const;

  /**
 	* \return pointer to the listening socket with ipv4 address
 	*/
  Ptr<Socket> GetListeningSocketIpv6 (void) const;

  /**
   * \return list of pointer to accepted sockets
   */
  std::list<Ptr<Socket> > GetAcceptedSockets(void) const;

  /**
   * \brief set the callback function that is called when a packet is received
   * \param callback the function to which the callback is set.
   */
  void SetPacketReceivedCallBack(void (*callback)(Ptr<Socket> socket));

  Address         m_localIpv4;         //!< Local address to bind to for ipv4 socket
  Address		  m_localIpv6;			//!< Local address to bind to for the ipv6 socket
 protected:
  virtual void DoDispose (void);

 private:
  // inherited from Application base class.
  virtual void StartApplication (void);    // Called at time specified by Start
  virtual void StopApplication (void);     // Called at time specified by Stop

  /**
   * \brief Created to set up the listening socket with all the callbacks set.
   * \param address of type Address, the address which will bind to the socket
   * \return Ptr<Socket>, the socket with the address bound
   */
   Ptr<Socket> CreateListeningSocket(const Address bindTo);

   /**
    * \breif Closes the listening sockets.
    * \param The socket to close
    */
   void CloseListeningSocket(Ptr<Socket> socket);

  /**
   * \brief Handle a connection request received by the application.
   * \param socket the incoming connection socket
   * \param from the address the connection is from
   */
  bool HandleRequest(Ptr<Socket> socket, const Address& from);

  /**
   * \brief Handle an incoming connection that has been accepted
   * \param socket the incoming connection socket
   * \param from the address the connection is from
   */
  void HandleAccept(Ptr<Socket> socket, const Address& from);

  /**
   * \brief Handle a packet received by the application
   * \param socket the receiving socket
   */
  void HandleRead(Ptr<Socket> socket);

  /**
   * \brief Handle an connection close
   * \param socket the connected socket
   */
  void HandlePeerClose (Ptr<Socket> socket);

  /**
   * \brief Handle an connection error
   * \param socket the connected socket
   */
  void HandlePeerError (Ptr<Socket> socket);

  // When a connection is accepted in TCP, a new socket is returned
  // So we need to store a listening socket for this class
  Ptr<Socket>     m_listeningSocketIpv4; //!< Listening socket for ipv4
  Ptr<Socket>     m_listeningSocketIpv6; //!< Listening socket for ipv6
  // And a list of sockets that have been accepted
  std::list<Ptr<Socket> > m_acceptedSocketList; //!< the accepted sockets


  /// Traced Callback: received packets, source address.
  TracedCallback<Ptr<const Packet>, const Address &> m_rxTrace;

  /// Callback for tracing the packet Rx events, includes source and destination addresses
  TracedCallback<Ptr<const Packet>, const Address &, const Address &> m_rxTraceWithAddresses;

  /// The function that will be called when a packet is received
  void (*m_packetReceivedCallback)(Ptr<Socket> socket);
};

#endif //_MULTI_CLIENT_TCP_SERVER_H_
