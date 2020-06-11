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

#include "ns3/socket.h"
#include "ns3/application.h"
#include "ns3/address.h"
#include "ns3/ptr.h"
#include "ns3/traced-callback.h"

#ifndef _CUSTOM_UDP_CLIENT_H_
#define _CUSTOM_UDP_CLIENT_H_

using namespace ns3;
using namespace std;

/**
 * \brief Modified version of the udp-client in ns3. Contains a function that lets us schedule packets to be sent in
 * NS3Netsim.
 */

class CustomUdpClient: public Application {
public:
  /**
   * \brief Configures the client
   */
  static TypeId GetTypeId (void);

  /**
    * \brief Schedule the next packet transmission
    * \param dst where the message will be sent
    * \param val the message that will be send
    * \param valTime delay the transmission by this amount of time
    */
  void ScheduleTransmit (std::string val, std::string valTime);
private:
  virtual void StartApplication (void);
  virtual void StopApplication (void);
  /**
    * The over-written send callback function, to prevent crashes.
    */
  void SendMessage (string message);

  Ptr<Socket>           m_socket; //!< Socket that will be used to send the messages
  Address               m_peerAddress; //!< Remote peer address
  uint16_t              m_peerPort; //!< Remote peer port
  EventId               m_sendEvent; //!< Event to send the next packet
  Address               m_local;

  /// Callbacks for tracing the packet Tx events
  TracedCallback<Ptr<const Packet> > m_txTrace;

  /// Callbacks for tracing the packet Rx events
  TracedCallback<Ptr<const Packet> > m_rxTrace;

  /// Callbacks for tracing the packet Tx events, includes source and destination addresses
  TracedCallback<Ptr<const Packet>, const Address &, const Address &> m_txTraceWithAddresses;

  /// Callbacks for tracing the packet Rx events, includes source and destination addresses
  TracedCallback<Ptr<const Packet>, const Address &, const Address &> m_rxTraceWithAddresses;
};

#endif //_CUSTOM_UDP_CLIENT_H_
