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

#ifndef _CUSTOM_UDP_SERVER_H_
#define _CUSTOM_UDP_SERVER_H_

#include "ns3/core-module.h"
#include "ns3/socket.h"
#include "ns3/application.h"
#include "ns3/address.h"
#include "ns3/ptr.h"

using namespace ns3;
using namespace std;

/**
 * \brief Modified version of the udp-server in ns3. The read callback function has been modified to suit the needs
 * of the co-simulator.
 */
class CustomUdpServer: public Application {
public:
  /**
   * \brief Configures the server
   */
  static TypeId GetTypeId (void);
  /**
   * \brief set the callback function that is called when a packet is received
   * \param callback the function to which the callback is set.
   */
  void SetPacketReceivedCallBack(void (*callback)(Ptr<Socket> socket));
private:
  virtual void StartApplication (void);
  virtual void StopApplication (void);

  /**
   * \Brief, create a udp socket and bind it to the address
   * \param bindTo, the address to which the udp packet should be bound to
   * \return socket, the created udp socket
   */
  Ptr<Socket> CreateSocket(const Address bindTo);

  /**
   * Close a udp socket.
   * \param socket, the udp socket to close
   */
  void CloseSocket(Ptr<Socket> socket);
  /**
   * The over-written read callback function that calls ExtractInformationFromPacketAndSendToUpperLayer to send
   * a message that a new packet has been received.
   */
  virtual void HandleRead (Ptr<Socket> socket);
  /// The function that will be called when a packet is received
  void (*m_packetReceivedCallback)(Ptr<Socket> socket);
  Ptr<Socket>           m_socketIpv4; //!< Socket that will be used to send the messages for ipv4
  Ptr<Socket>           m_socketIpv6; //!< Socket that will be used to send the messages for ipv6
  Address               m_localIpv4;         //!< Local address to bind to for ipv4 socket
  Address               m_localIpv6;         //!< Local address to bind to for ipv4 socket

  TracedCallback<Ptr<const Packet> > m_rxTrace;
  TracedCallback<Ptr<const Packet>, const Address &, const Address &> m_rxTraceWithAddresses;
};

#endif //_CUSTOM_UDP_SERVER_H_
