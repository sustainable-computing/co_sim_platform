/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2019 Evandro de Souza
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
 * Author:  Evandro de Souza <evandro@ualberta.ca>
 * Date:    2019.05.12
 * Company: University of Alberta/Canada - Computing Science
 *
 */


#ifndef SMARTGRID_NS3_HELPER_H_
#define SMARTGRID_NS3_HELPER_H_

#include <vector>
#include <iostream>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/node-container.h"
#include "ns3/point-to-point-helper.h"
#include "ns3/applications-module.h"
#include "ns3/internet-module.h"

using namespace std;
using namespace ns3;

/**
 * Read node adjacency matrix and load into a boolean vector
 *
 * \param adjMatFileName Filename of the adjacency matrix
 * \returns Boolean array with indication of node connection
 */
vector< vector<bool> > ReadNodeAdjMatrix (string adjMatFileName);


/**
 * Print the node adjacency matrix
 *
 * \param description Filename of the input file
 * \param array Boolean array with indication of node connection
 *
 */
void PrintNodeAdjMatrix (const char* description, vector<vector<bool> > array);


/**
 * Read node names and coordinates
 *
 * \param nodeCoordinatesFilename Filename of the coordinates file
 * \returns String array with nodes names and coordinates
 *
 */
vector<vector<string> > ReadCoordinatesFile (string nodeCoordinatesFilename);


/**
 * Print the node names and coordinates
 *
 * \param description Filename of the input file
 * \param array String array with indication of node coordinates
 *
 */
void PrintNamesCoordinates (const char* description, vector<vector<string> > array);


/**
 * Read node application connections
 *
 * \param appConnectionsFilename Filename of the application connections
 * \returns String array with nodes names of application connections
 *
 */
vector<vector<string> > ReadAppConnectionsFile (string nodeCoordinatesFilename);


/**
 * Print the IP addresses
 *
 * \param nodes NodeContainer with nodes
 *
 */
void PrintIpAddresses(NodeContainer nodes);


/**
 * Create map to associate Ipv4 address and Node Id
 *
 * \param nodes NodeContainer with nodes
 *
 */
map<Ipv4Address, uint32_t> CreateMapIpv4NodeId(NodeContainer nodes);


#endif /* SMARTGRID_NS3_HELPER_H_ */
