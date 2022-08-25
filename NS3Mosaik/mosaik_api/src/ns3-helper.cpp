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

#include "ns3-helper.h"
#include "json.hpp"
#define MAX_NODES 2000
using namespace std;
using namespace ns3;
using json = nlohmann::ordered_json;

int parent[MAX_NODES][MAX_NODES];

vector<vector<bool>>
ReadNodeAdjMatrix(string adjMatFileName)
{
  NS_LOG_INFO("ReadNodeAdjMatrix");
  memset(parent, -1, sizeof(parent));

  ifstream adjMatFile;
  adjMatFile.open(adjMatFileName.c_str(), std::ios::in);
  if (adjMatFile.fail())
  {
    NS_FATAL_ERROR("File " << adjMatFileName.c_str() << " not found");
  }
  vector<vector<bool>> array;
  int i = 0;
  int n_nodes = 0;

  while (!adjMatFile.eof())
  {
    string line;
    getline(adjMatFile, line);
    if (line == "")
    {
      NS_LOG_WARN("WARNING: Ignoring blank row in the array: " << i);
      break;
    }

    istringstream iss(line);
    bool element;
    vector<bool> row;
    int j = 0;

    while (iss >> element)
    {
      row.push_back(element);
      j++;
    }

    if (i == 0)
    {
      n_nodes = j;
    }

    if (j != n_nodes)
    {
      NS_LOG_ERROR("ERROR: Number of elements in line " << i << ": " << j << " not equal to number of elements in line 0: " << n_nodes);
      NS_FATAL_ERROR("ERROR: The number of rows is not equal to the number of columns! in the adjacency matrix");
    }
    else
    {
      array.push_back(row);
    }
    i++;
  }

  if (i != n_nodes)
  {
    NS_LOG_ERROR("There are " << i << " rows and " << n_nodes << " columns.");
    NS_FATAL_ERROR("ERROR: The number of rows is not equal to the number of columns! in the adjacency matrix");
  }

  adjMatFile.close();
  return array;
}

vector<vector<bool>>
ReadNodeAdjListJson(string jsonFileName)
{
  NS_LOG_INFO("ReadNodeAdjListJson");
  memset(parent, -1, sizeof(parent));

  ifstream adjListFile;
  adjListFile.open(jsonFileName.c_str(), std::ios::in);
  if (adjListFile.fail())
  {
    NS_FATAL_ERROR("File " << jsonFileName.c_str() << " not found");
  }
  json config;
  adjListFile >> config;

  unsigned int num_nodes = config["nodes"].size();

  vector<vector<bool>> array;
  unordered_map<string, unsigned int> node_to_idx;
  array.resize(num_nodes, vector<bool>(num_nodes));
  // This will map the node to a numerical index
  unsigned idx = 0;
  for (auto &node : config["nodes"].items())
  {
    node_to_idx.emplace(node.key(), idx);
    ++idx;
  }
  // This will create the adjacency matrix
  for (auto &node : config["nodes"].items())
  {
    unsigned int curr_idx = node_to_idx[node.key()];
    for (auto &neighbour : node.value()["connections"])
    {
      array[curr_idx][node_to_idx[neighbour]] = true;
    }
  }

  adjListFile.close();
  return array;
}

vector<vector<double>>
loadNodeCoords(vector<vector<string>> arrayNamesCoords)
{
  vector<vector<double>> arrayNodeCoords;
  for (auto it = arrayNamesCoords.begin(); it != arrayNamesCoords.end(); it++)
  {
    vector<double> row;
    row.push_back(atof((*it)[1].c_str()));
    row.push_back(atof((*it)[2].c_str()));
    arrayNodeCoords.push_back(row);
  }
  return arrayNodeCoords;
}

void PrintNodeAdjMatrix(const char *description, vector<vector<bool>> array)
{
  NS_LOG_INFO("PrintNodeAdjMatrix");
  cout << "**** Print file " << description << "********" << endl;
  for (size_t m = 0; m < array.size(); m++)
  {
    for (size_t n = 0; n < array[m].size(); n++)
    {
      cout << array[m][n] << ' ';
    }
    cout << endl;
  }
  cout << "**** End " << description << " ********" << endl;
}

vector<vector<string>>
ReadCoordinatesFile(string nodeCoordinatesFilename)
{
  NS_LOG_INFO("ReadCoordinatesFile");
  vector<vector<string>> array;
  ifstream node_coordinates_file;
  ifstream inputFile(nodeCoordinatesFilename);
  int l = 0;

  while (inputFile)
  {
    l++;
    string s;
    if (!getline(inputFile, s))
      break;
    if (s != "")
    {
      istringstream ss(s);
      vector<string> record;

      while (ss)
      {
        string line;
        if (!getline(ss, line, ','))
          break;
        //--- strip '\r'
        if (!line.empty() && *line.rbegin() == '\r')
        {
          line.erase(line.length() - 1, 1);
        }
        record.push_back(line);
      }
      array.push_back(record);
    }
  }

  if (!inputFile.eof())
  {
    cerr << "Could not read file " << nodeCoordinatesFilename << "\n";
    __throw_invalid_argument("File not found.");
  }

  return array;
}

vector<vector<string>>
ReadCoordinatesJSONFile(string jsonFileName)
{
  NS_LOG_INFO("ReadCoordinatesJSONFile");

  ifstream coordJSONFile;
  coordJSONFile.open(jsonFileName.c_str(), std::ios::in);
  if (coordJSONFile.fail())
  {
    NS_FATAL_ERROR("File " << jsonFileName.c_str() << " not found");
  }
  json config;
  coordJSONFile >> config;

  unsigned int num_nodes = config["nodes"].size();

  vector<vector<string>> array;

  for (auto& node : config["nodes"].items())
  {
    // node_id (name), x, y
    vector<string> record;
    // name goes first
    record.push_back(node.key());
    // coordinates goes second
    record.push_back(to_string(node.value()["x"]));
    record.push_back(to_string(node.value()["y"]));

    // Insert the record into the array list
    array.push_back(record);
  }

  return array;
}

void PrintNamesCoordinates(const char *description, vector<vector<string>> array)
{
  NS_LOG_INFO("PrintNamesCoordinates");
  cout << "**** Start " << description << " ********" << endl;
  for (size_t m = 0; m < array.size(); m++)
  {
    for (size_t n = 0; n < array[m].size(); n++)
    {
      cout << array[m][n] << ' ';
    }
    cout << endl;
  }
  cout << "**** End " << description << " ********" << endl;
}

vector<vector<string>>
ReadAppConnectionsFile(string appConnectionsFilename)
{
  NS_LOG_INFO("ReadAppConnectionsFile");
  vector<vector<string>> array;
  ifstream node_coordinates_file;
  ifstream inputFile(appConnectionsFilename);
  int l = 0;

  while (inputFile)
  {
    l++;
    string s;
    if (!getline(inputFile, s))
      break;
    if (s != "")
    {
      istringstream ss(s);
      vector<string> record;

      while (ss)
      {
        string line;
        if (!getline(ss, line, ','))
          break;
        //--- strip '\r'
        if (!line.empty() && *line.rbegin() == '\r')
        {
          line.erase(line.length() - 1, 1);
        }
        record.push_back(line);
      }
      array.push_back(record);
    }
  }

  if (!inputFile.eof())
  {
    cerr << "Could not read file " << appConnectionsFilename << "\n";
    __throw_invalid_argument("File not found.");
  }

  return array;
}

void PrintIpAddresses(NodeContainer nodes, string network)
{
  NS_LOG_INFO("PrintIpAddresses");
  cout << "**** Start Print IP Addresses ********" << endl;
  string nodeName;
  Ipv4InterfaceAddress v4iaddr;
  Ipv6InterfaceAddress v6iaddr;
  bool v4 = false;
  if (network == "P2P" || network == "CSMA")  v4 = true;
  for (NodeList::Iterator i = NodeList::Begin(); i != NodeList::End(); ++i)
  {
    int ifaces;
    if (v4) ifaces = (*i)->GetObject<Ipv4>()->GetNInterfaces();
    else  ifaces = (*i)->GetObject<Ipv6>()->GetNInterfaces();

    for (int j = 1; j < ifaces; j++)
    {
      if (v4) v4iaddr = (*i)->GetObject<Ipv4>()->GetAddress(j, 0);
      else v6iaddr = (*i)->GetObject<Ipv6>()->GetAddress(j, 1);
      nodeName = Names::FindName((*i));

      if (v4) cout << "Node ID: " << (*i)->GetId() << " - "
                   << "Ifaces: " << (*i)->GetObject<Ipv4>()->GetNInterfaces() << " - "
                   << "Name: " << nodeName << " - "
                   << "IP Addr: " << v4iaddr.GetLocal() << " - "
                   << "IP Mask: " << v4iaddr.GetMask() << endl;
      else    cout << "Node ID: " << (*i)->GetId() << " - "
                   << "Ifaces: " << (*i)->GetObject<Ipv6>()->GetNInterfaces() << " - "
                   << "Name: " << nodeName << " - "
                   << "IP Addr: " << v6iaddr.GetAddress() << " - "
                   << "IP Mask: " << v6iaddr.GetPrefix() << endl;
    }
  }
  cout << "**** End Print IP Addresses ********" << endl;
}

map<Ipv4Address, uint32_t>
CreateMapIpv4NodeId(NodeContainer nodes)
{
  NS_LOG_INFO("CreateMapIpv4NodeId");

  map<Ipv4Address, uint32_t> mapIpv4NodeId;
  string nodeName;
  uint32_t nodeId;
  Ipv4InterfaceAddress iaddr;
  for (NodeList::Iterator i = NodeList::Begin(); i != NodeList::End(); ++i)
  {
    int ifaces = (*i)->GetObject<Ipv4>()->GetNInterfaces();
    for (int j = 1; j < ifaces; j++)
    {
      iaddr = (*i)->GetObject<Ipv4>()->GetAddress(j, 0);
      nodeId = (*i)->GetId();
      nodeName = Names::FindName((*i));

      mapIpv4NodeId[iaddr.GetLocal()] = nodeId;
    }
  }

  return mapIpv4NodeId;
}

map<Ipv6Address, uint32_t>
CreateMapIpv6NodeId(NodeContainer nodes)
{
  NS_LOG_INFO("CreateMapIpv6NodeId");

  map<Ipv6Address, uint32_t> mapIpv6NodeId;
  string nodeName;
  uint32_t nodeId;
  Ipv6InterfaceAddress iaddr;
  for (NodeList::Iterator i = NodeList::Begin(); i != NodeList::End(); ++i)
  {
    int ifaces = (*i)->GetObject<Ipv6>()->GetNInterfaces();
    for (int j = 1; j < ifaces; j++)
    {
      iaddr = (*i)->GetObject<Ipv6>()->GetAddress(j, 1);
      nodeId = (*i)->GetId();
      nodeName = Names::FindName((*i));

      mapIpv6NodeId[iaddr.GetAddress()] = nodeId;
    }
  }

  return mapIpv6NodeId;
}

string FindNextHop(string clt, string srv, vector<vector<bool>> array)
{
  Ptr <Node> srcNode = Names::Find<Node>(clt);
  Ptr <Node> desNode = Names::Find<Node>(srv);

  size_t src = srcNode->GetId();
  size_t des = desNode->GetId();

  if(parent[des][src] != -1)
  {
    Ptr <Node> nextHopeNode = NodeList::GetNode(parent[des][src]);
    return Names::FindName(nextHopeNode);
  }
  size_t nextHop;
  queue <size_t> bfsQ;

  // Searching in the opposite direction so that parents are
  // actually next hops when des is the destination
  bfsQ.push(des);
  parent[des][des] = des;
  while(!bfsQ.empty())
  {
    nextHop = bfsQ.front();
    bfsQ.pop();
    for (size_t m = 0; m < array[nextHop].size(); m++)
    {
      if(!array[nextHop][m]) continue;
      if(parent[des][m] != -1)  continue;
      bfsQ.push(m);
      parent[des][m] = nextHop;
    }
  }
  if(parent[des][src] == -1)  cerr << "The source and destination are not connected!";

  Ptr <Node> nextHopeNode = NodeList::GetNode(parent[des][src]);
  return Names::FindName(nextHopeNode);  
}

void PrintRoutingTable (Ptr<Node>& n, bool v4)
{
  if (v4)
  {
    Ptr<Ipv4StaticRouting> routing = 0;
    Ipv4StaticRoutingHelper routingHelper;
    Ptr<Ipv4> ipv4 = n->GetObject<Ipv4> ();
    uint32_t nbRoutes = 0;
    Ipv4RoutingTableEntry route;

    routing = routingHelper.GetStaticRouting (ipv4);

    std::cout << "Routing table of " << Names::FindName(n) << " : " << std::endl;
    std::cout << "Destination\t\t\t\t" << "Gateway\t\t\t\t\t" << "Interface\t" <<  "Destination Network" << std::endl;

    nbRoutes = routing->GetNRoutes ();
    for (uint32_t i = 0; i < nbRoutes; i++)
    {
      route = routing->GetRoute (i);
      std::cout << route.GetDest () << "\t"
                << route.GetGateway () << "\t"
                << route.GetInterface () << "\t"
                << route.GetDestNetwork () << "\t"
                << route.GetDestNetworkMask () << "\t"
                << std::endl;
    }
  }
  else
  {
    Ptr<Ipv6StaticRouting> routing = 0;
    Ipv6StaticRoutingHelper routingHelper;
    Ptr<Ipv6> ipv6 = n->GetObject<Ipv6> ();
    uint32_t nbRoutes = 0;
    Ipv6RoutingTableEntry route;

    routing = routingHelper.GetStaticRouting (ipv6);

    std::cout << "Routing table of " << Names::FindName(n) << " : " << std::endl;
    std::cout << "Destination\t\t\t\t" << "Gateway\t\t\t\t\t" << "Interface\t" <<  "Prefix to use" << std::endl;

    nbRoutes = routing->GetNRoutes ();
    for (uint32_t i = 0; i < nbRoutes; i++)
    {
      route = routing->GetRoute (i);
      std::cout << route.GetDest () << "\t"
                << route.GetGateway () << "\t"
                << route.GetInterface () << "\t"
                << route.GetPrefixToUse () << "\t"
                << std::endl;
    }
  }
}

bool isSecondary(string nodeName)
{
  int s_size = nodeName.size();

  /// Secondary node name has to be a number
  for(int i=0; i<s_size; i++)
    if(!isdigit(nodeName[i])) return false;

  /// There can be at most 999 primary nodes (for now)
  if(s_size < 4) return false;
  return true;
}

uint32_t findIndex(string nodeName, uint32_t interfaceIdx)
{
  int s_size = nodeName.size();
  /**
   * @brief breakdown of interface count of nodes
   * Each node may have 6LoWPAN links or usual P2P/CSMA links
   * duplicates are only generated for 6LoWPAN links
   * 6LoWPAN is only installed at the secondary network
   * 
   * node 1 has no secondary links (2 interfaces) and will not be called
   * nodes 2, 3, and 6 have 3 primary links and 55 secondary links
   * nodes 18, 22, 25 and 33 have 1 primary link and 55 secondary links
   * the remaining primary nodes all have 2 primary and 55 secondary links
   * all secondary nodes have all duplicate links (number does not matter)
   */
  // secondary node
  if (s_size > 3)  return interfaceIdx/2;
  else if (nodeName == "2" || nodeName == "3" || nodeName == "6")
  {
    return ((interfaceIdx-3)/2 + 3);
  }
  else if (nodeName == "18" || nodeName == "22" || nodeName == "25" || nodeName == "33")
  {
    return ((interfaceIdx-1)/2 + 1);
  }
  else
  {
    return ((interfaceIdx-2)/2 + 2);
  }
}