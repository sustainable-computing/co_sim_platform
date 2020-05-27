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
 * Date:    2020.05.14
 * Company: University of Alberta/Canada - Computing Science
 *
 * Modelled after udp-echo-client.h
 */

#include "ns3/socket.h"
#include "ns3/application.h"
#include "ns3/address.h"
#include "ns3/event-id.h"
#include "ns3/ptr.h"
#include "ns3/traced-callback.h"

#ifndef _TCP_SENSOR_H_
#define _TCP_SENSOR_H_

using namespace ns3;

/**
 * \brief A TCP client
 *
 * A client that creates a TCP connection with a server and sends packets
 * to it. This application was created to work with MultiClientTCPServer
 * but can be used more generally.
 *
 * Modelled after: udp-echo-client.h
 */
class TcpClient : public Application
{
public:
  /**
   * \brief Get the type ID.
   * \return the object TypeId
   */
  static TypeId GetTypeId (void);

  TcpClient();
  virtual ~TcpClient();

  /**
   * \brief set a remote address and port
   * \param ip remote IP address
   * \param port remote port
   */
   void SetRemote(Address ip, uint16_t port);

  /**
   * \brief set the remote address
   * \param addr remote address
   */
   void SetRemote(Address addr);
  /**
    * \brief Schedule the next packet transmission
    * \param dst where the message will be sent
    * \param val the message that will be send
    * \param valTime delay the transmission by this amount of time
    */
  void ScheduleTransmit(std::string val, std::string valTime);

  /**
    * \brief Callback function scheduled to send the message.
    * \param socket
    * \param message The message that will be sent
    */
  void SendMessage (std::string message);
protected:
  virtual void DoDispose (void);
private:
  // inherited from Application base class.
  virtual void StartApplication (void);    // Called at time specified by Start
  virtual void StopApplication (void);     // Called at time specified by Stop


  Ptr<Socket>           m_socket; //!< Socket that will be used to send the messages
  Address               m_peerAddress; //!< Remote peer address
  uint16_t              m_peerPort; //!< Remote peer port
  EventId               m_sendEvent; //!< Event to send the next packet
  Address               m_local;
  // Stores the messages that will be sent

  /// Callbacks for tracing the packet Tx events
  TracedCallback<Ptr<const Packet> > m_txTrace;

  /// Callbacks for tracing the packet Rx events
  TracedCallback<Ptr<const Packet> > m_rxTrace;

  /// Callbacks for tracing the packet Tx events, includes source and destination addresses
  TracedCallback<Ptr<const Packet>, const Address &, const Address &> m_txTraceWithAddresses;

  /// Callbacks for tracing the packet Rx events, includes source and destination addresses
  TracedCallback<Ptr<const Packet>, const Address &, const Address &> m_rxTraceWithAddresses;
};

#endif //_TCP_SENSOR_H_
