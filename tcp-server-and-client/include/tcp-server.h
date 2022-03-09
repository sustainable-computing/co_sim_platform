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
 * Modelled after udp-echo-server.h
 */

#ifndef TCP_SERVER_H
#define TCP_SERVER_H

#include "ns3/application.h"
#include "ns3/event-id.h"
#include "ns3/ptr.h"
#include "ns3/address.h"
#include "ns3/traced-callback.h"

namespace ns3 {

class Socket;
class Packet;

/**
 * \ingroup applications 
 * \defgroup udpecho UdpEcho
 */

/**
 * \ingroup udpecho
 * \brief A Udp Echo server
 *
 * Every packet received is sent back.
 */
class TcpServer : public Application 
{
public:
  /**
   * \brief Get the type ID.
   * \return the object TypeId
   */
  static TypeId GetTypeId (void);

  TcpServer ();

  /**
   * \return pointer to the listening socket.
   */
  Ptr<Socket> GetListeningSocket(void) const;

  /**
   * \return list of pointer to accepted sockets
   */
  std::list<Ptr<Socket>> GetAcceptedSockets(void) const;

  /**
   * \brief set the callback function that is called when a packet is received
   * \param callback the function to which the callback is set.
   */
  void SetPacketReceivedCallBack(void (*callback)(Ptr<Socket> socket));
  virtual ~TcpServer ();



protected:
  virtual void DoDispose (void);

private:

  virtual void StartApplication (void);
  virtual void StopApplication (void);

  /**
   * \brief Handle a packet reception.
   *
   * This function is called by lower layers.
   *
   * \param socket the socket the packet was received to.
   */
  void HandleRead (Ptr<Socket> socket);

  /**
   * \brief Handle a connection request received by the application.
   * \param socket the incoming connection socket
   * \param from the address the connection is from
   */
  bool HandleRequest(Ptr<Socket> socket, const Address &from);

  /**
   * \brief Handle an incoming connection that has been accepted
   * \param socket the incoming connection socket
   * \param from the address the connection is from
   */
  void HandleAccept(Ptr<Socket> socket, const Address &from);

  /**
   * \brief Handle an connection close
   * \param socket the connected socket
   */
  void HandlePeerClose(Ptr<Socket> socket);

  /**
   * \brief Handle an connection error
   * \param socket the connected socket
   */
  void HandlePeerError(Ptr<Socket> socket);

  // A list of sockets that have been accepted
  std::list<Ptr<Socket>> m_acceptedSocketList; //!< the accepted sockets

  uint16_t m_port; //!< Port on which we listen for incoming packets.
  Ptr<Socket> m_socket; //!< IPv4 Socket
  Ptr<Socket> m_socket6; //!< IPv6 Socket
  Address m_local; //!< local multicast address
  /// The function that will be called when a packet is received
  void (*m_packetReceivedCallback)(Ptr<Socket> socket);

  /// Callbacks for tracing the packet Rx events
  TracedCallback<Ptr<const Packet> > m_rxTrace;

  /// Callbacks for tracing the packet Rx events, includes source and destination addresses
  TracedCallback<Ptr<const Packet>, const Address &, const Address &> m_rxTraceWithAddresses;
};

} // namespace ns3

#endif /* TCP_SERVER_H */

