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
 * Date:    2020.05.18
 * Company: University of Alberta/Canada - Computing Science
 *
 * Modelled after packet-sink-helper.h
 */

#ifndef _MULTI_CLIENT_TCP_SERVER_HELPER_H_
#define _MULTI_CLIENT_TCP_SERVER_HELPER_H_

#include "ns3/object-factory.h"
#include "ns3/ipv4-address.h"
#include "ns3/node-container.h"
#include "ns3/application-container.h"

using namespace ns3;

/**
 * \brief Helps with installation and configuration of MultiClientTcpServer
 */
class MultiClientTcpServerHelper {
 public:
  /**
   * \brief constructor
   * \param address The address for the client that will be created
   */
  MultiClientTcpServerHelper();

  /**
   * Sets an attribute to the value passed in
   * \param name The name of the attribute
   * \param value The value to which the attribute should be set to
   */
  void SetAttribute (std::string name, const AttributeValue &value);

  /**
   * \brief Installs TcpClient on every node in the NodeContainer
   *
   * \param c The container that contains all the nodes
   *
   * \return An application container with all the applications
   */
  ApplicationContainer Install (NodeContainer c) const;

  /**
   * \brief Installs TcpClient on the given node
   *
   * \param node Where the application is installed
   *
   * \return An application container with the installed application
   */
  ApplicationContainer Install (Ptr<Node> node) const;

  /**
   * \brief Installs TcpClient on a node with nodeName
   *
   * \param nodeName The name of the node
   *
   * \return An application container with the installed application
   */
  ApplicationContainer Install (std::string nodeName) const;
 private:
  Ptr<Application> InstallPriv (Ptr<Node> node) const;
  ObjectFactory           m_factory;
};

#endif //_MULTI_CLIENT_TCP_SERVER_HELPER_H_
