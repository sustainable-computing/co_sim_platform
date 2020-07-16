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


using namespace std;
using namespace ns3;


vector<vector<bool>>
ReadNodeAdjMatrix (string adjMatFileName)
{
  NS_LOG_INFO ("ReadNodeAdjMatrix");

  ifstream adjMatFile;
  adjMatFile.open (adjMatFileName.c_str (), std::ios::in);
  if (adjMatFile.fail ())
    {
      NS_FATAL_ERROR ("File " << adjMatFileName.c_str () << " not found");
    }
  vector<vector<bool> > array;
  int i = 0;
  int n_nodes = 0;

  while (!adjMatFile.eof ())
    {
      string line;
      getline (adjMatFile, line);
      if (line == "")
        {
          NS_LOG_WARN ("WARNING: Ignoring blank row in the array: " << i);
          break;
        }

      istringstream iss (line);
      bool element;
      vector<bool> row;
      int j = 0;

      while (iss >> element)
        {
          row.push_back (element);
          j++;
        }

      if (i == 0)
        {
          n_nodes = j;
        }

      if (j != n_nodes )
        {
          NS_LOG_ERROR ("ERROR: Number of elements in line " << i << ": " << j << " not equal to number of elements in line 0: " << n_nodes);
          NS_FATAL_ERROR ("ERROR: The number of rows is not equal to the number of columns! in the adjacency matrix");
        }
      else
        {
          array.push_back (row);
        }
      i++;
    }

  if (i != n_nodes)
    {
      NS_LOG_ERROR ("There are " << i << " rows and " << n_nodes << " columns.");
      NS_FATAL_ERROR ("ERROR: The number of rows is not equal to the number of columns! in the adjacency matrix");
    }

  adjMatFile.close ();
  return array;

}

vector<vector<double>>
loadNodeCoords(vector<vector<string>> arrayNamesCoords)
{
  vector<vector<double>> arrayNodeCoords;
  for(auto it = arrayNamesCoords.begin(); it != arrayNamesCoords.end(); it++) {
      vector<double> row;
      row.push_back(   atof( (*it)[1].c_str() )  );
      row.push_back(   atof( (*it)[2].c_str() )  );
      arrayNodeCoords.push_back(row);
    }
  return arrayNodeCoords;
}

void
PrintNodeAdjMatrix (const char* description, vector<vector<bool>> array)
{
  NS_LOG_INFO ("PrintNodeAdjMatrix");
  cout << "**** Print file " << description << "********" << endl;
  for (size_t m = 0; m < array.size (); m++)
    {
      for (size_t n = 0; n < array[m].size (); n++)
        {
          cout << array[m][n] << ' ';
        }
      cout << endl;
    }
  cout << "**** End " << description << " ********" << endl;
}


vector<vector<string>>
ReadCoordinatesFile (string nodeCoordinatesFilename)
{
  NS_LOG_INFO ("ReadCoordinatesFile");
  vector<vector<string> > array;
  ifstream node_coordinates_file;
  ifstream inputFile(nodeCoordinatesFilename);
  int l = 0;

  while (inputFile) {
      l++;
      string s;
      if (!getline(inputFile, s)) break;
      if (s != "") {
          istringstream ss(s);
          vector<string> record;

          while (ss) {
              string line;
              if (!getline(ss, line, ',')) break;
              //--- strip '\r'
              if(!line.empty() && *line.rbegin() == '\r') {
                  line.erase( line.length()-1, 1);
                }
              record.push_back(line);
            }
          array.push_back(record);
        }
    }

  if (!inputFile.eof()) {
      cerr << "Could not read file " << nodeCoordinatesFilename << "\n";
      __throw_invalid_argument("File not found.");
    }

  return array;
}


void
PrintNamesCoordinates (const char* description, vector<vector<string> > array)
{
  NS_LOG_INFO ("PrintNamesCoordinates");
  cout << "**** Start " << description << " ********" << endl;
  for (size_t m = 0; m < array.size (); m++)
    {
      for (size_t n = 0; n < array[m].size (); n++)
        {
          cout << array[m][n] << ' ';
        }
      cout << endl;
    }
  cout << "**** End " << description << " ********" << endl;
}


vector<vector<string>>
ReadAppConnectionsFile (string appConnectionsFilename)
{
  NS_LOG_INFO ("ReadAppConnectionsFile");
  vector<vector<string> > array;
  ifstream node_coordinates_file;
  ifstream inputFile(appConnectionsFilename);
  int l = 0;

  while (inputFile) {
      l++;
      string s;
      if (!getline(inputFile, s)) break;
      if (s != "") {
          istringstream ss(s);
          vector<string> record;

          while (ss) {
              string line;
              if (!getline(ss, line, ',')) break;
              //--- strip '\r'
              if(!line.empty() && *line.rbegin() == '\r') {
                  line.erase( line.length()-1, 1);
                }
              record.push_back(line);
            }
          array.push_back(record);
        }
    }

  if (!inputFile.eof()) {
      cerr << "Could not read file " << appConnectionsFilename << "\n";
      __throw_invalid_argument("File not found.");
    }

  return array;
}


void
PrintIpAddresses(NodeContainer nodes)
{
  NS_LOG_INFO ("PrintIpAddresses");
  cout << "**** Start Print IP Addresses ********" << endl;
  string nodeName;
  Ipv4InterfaceAddress iaddr;
  for (NodeList::Iterator i = NodeList::Begin (); i != NodeList::End (); ++i)
    {
      int ifaces = (*i)->GetObject<Ipv4>()->GetNInterfaces();
      for (int j = 1; j < ifaces; j++) {
          iaddr = (*i)->GetObject<Ipv4>()->GetAddress (j,0);
          nodeName = Names::FindName((*i));

          cout << "Node ID: "   << (*i)->GetId() << " - "
               << "Ifaces: " << (*i)->GetObject<Ipv4>()->GetNInterfaces() << " - "
               << "Name: " <<  nodeName << " - "
               << "IP Addr: "   << iaddr.GetLocal() <<  " - "
               << "IP Mask: " << iaddr.GetMask() << endl;
        }
    }
  cout << "**** End Print IP Addresses ********" << endl;
}


map<Ipv4Address, uint32_t>
CreateMapIpv4NodeId(NodeContainer nodes)
{
  NS_LOG_INFO ("CreateMapIpv4NodeId");

  map<Ipv4Address, uint32_t> mapIpv4NodeId;
  string nodeName;
  uint32_t nodeId;
  Ipv4InterfaceAddress iaddr;
  for (NodeList::Iterator i = NodeList::Begin (); i != NodeList::End (); ++i)
    {
      int ifaces = (*i)->GetObject<Ipv4>()->GetNInterfaces();
      for (int j = 1; j < ifaces; j++) {
          iaddr = (*i)->GetObject<Ipv4>()->GetAddress (j,0);
          nodeId = (*i)->GetId ();
          nodeName = Names::FindName((*i));

          mapIpv4NodeId[iaddr.GetLocal()] = nodeId;

        }
    }

  return mapIpv4NodeId;
}
