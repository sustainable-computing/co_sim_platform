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
 * Date:    2022.02.16
 * Company: University of Alberta/Canada - Computing Science
 * 
 * Modelled after udp-echo-helper.cc
 */
#include "tcp-helper.h"
#include "ns3/tcp-server.h"
#include "ns3/tcp-client.h"
#include "ns3/uinteger.h"
#include "ns3/names.h"

namespace ns3 {

TcpServerHelper::TcpServerHelper (uint16_t port)
{
  m_factory.SetTypeId (TcpServer::GetTypeId ());
  SetAttribute ("Port", UintegerValue (port));
}

void 
TcpServerHelper::SetAttribute (
  std::string name, 
  const AttributeValue &value)
{
  m_factory.Set (name, value);
}

ApplicationContainer
TcpServerHelper::Install (Ptr<Node> node) const
{
  return ApplicationContainer (InstallPriv (node));
}

ApplicationContainer
TcpServerHelper::Install (std::string nodeName) const
{
  Ptr<Node> node = Names::Find<Node> (nodeName);
  return ApplicationContainer (InstallPriv (node));
}

ApplicationContainer
TcpServerHelper::Install (NodeContainer c) const
{
  ApplicationContainer apps;
  for (NodeContainer::Iterator i = c.Begin (); i != c.End (); ++i)
    {
      apps.Add (InstallPriv (*i));
    }

  return apps;
}

Ptr<Application>
TcpServerHelper::InstallPriv (Ptr<Node> node) const
{
  Ptr<Application> app = m_factory.Create<TcpServer> ();
  node->AddApplication (app);

  return app;
}

TcpClientHelper::TcpClientHelper (Address address, uint16_t port)
{
  m_factory.SetTypeId (TcpClient::GetTypeId ());
  SetAttribute ("RemoteAddress", AddressValue (address));
  SetAttribute ("RemotePort", UintegerValue (port));
}

TcpClientHelper::TcpClientHelper (Address address)
{
  m_factory.SetTypeId (TcpClient::GetTypeId ());
  SetAttribute ("RemoteAddress", AddressValue (address));
}

void 
TcpClientHelper::SetAttribute (
  std::string name, 
  const AttributeValue &value)
{
  m_factory.Set (name, value);
}

void
TcpClientHelper::SetFill (Ptr<Application> app, std::string fill)
{
  app->GetObject<TcpClient>()->SetFill (fill);
}

void
TcpClientHelper::SetFill (Ptr<Application> app, uint8_t fill, uint32_t dataLength)
{
  app->GetObject<TcpClient>()->SetFill (fill, dataLength);
}

void
TcpClientHelper::SetFill (Ptr<Application> app, uint8_t *fill, uint32_t fillLength, uint32_t dataLength)
{
  app->GetObject<TcpClient>()->SetFill (fill, fillLength, dataLength);
}

ApplicationContainer
TcpClientHelper::Install (Ptr<Node> node) const
{
  return ApplicationContainer (InstallPriv (node));
}

ApplicationContainer
TcpClientHelper::Install (std::string nodeName) const
{
  Ptr<Node> node = Names::Find<Node> (nodeName);
  return ApplicationContainer (InstallPriv (node));
}

ApplicationContainer
TcpClientHelper::Install (NodeContainer c) const
{
  ApplicationContainer apps;
  for (NodeContainer::Iterator i = c.Begin (); i != c.End (); ++i)
    {
      apps.Add (InstallPriv (*i));
    }

  return apps;
}

Ptr<Application>
TcpClientHelper::InstallPriv (Ptr<Node> node) const
{
  Ptr<Application> app = m_factory.Create<TcpClient> ();
  node->AddApplication (app);

  return app;
}

} // namespace ns3
