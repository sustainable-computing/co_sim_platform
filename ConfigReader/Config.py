"""
Created on August 30, 2020
File contains the classes that will read and verify the config files.

@file    Config.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.06
@version 0.1
@company University of Alberta - Computing Science
"""
import json

from ConfigErrors import InvalidNetworkType, NodeWithNetworkIdAlreadyExistsInNetwork, \
    NodeWithPowerIdAlreadyExistsInNetwork
from NICs import P2PNIC, WiFiNIC
from Node import Node


class Config:
    """
    Class was created read, verify and store the verified config file.
    """
    # Stores the files passed in
    file = None
    # Stores all the nodes
    nodes = []
    # Store all the ids of the network nodes, used for verification purposes
    __network_node_ids = set()
    # Store all the ids of the power nodes, used for verification purposes
    __power_node_ids = set()
    # Stores the Network connection
    network_connections = []
    # Stores all the ids of the network connections in a set, used for verification purposes
    __network_connections = set()
    # Stores the app connections
    app_connections = []
    # Stores the app connection ids in a set, used for verification purposes
    __app_connections = []

    def __init__(self, file):
        """
        Stores the file pointer passed in. Nothing else is done.
        :param file:
        """
        # Just save the file pointer
        self.file = file

    def __setattr__(self, key, value):
        """
        Overridden, once file changes, wipe all the other members
        :param key:
        :param value:
        :return:
        """
        # Call super to change the value of the members
        super(Config, self).__setattr__(key, value)
        # If the changed key was file, then set all the others to their default value
        if key == "file":
            self.nodes = []
            self.__node_ids = dict()
            self.network_connections = []
            self.__network_connections = set()
            self.app_connections = []
            self.__app_connections = []

    def read_config(self):
        """
        Reads the config files and the file.
        :return: 
        """
        # Load the config file
        data = json.load(self.file)
        # Get the primary network out
        primary_network = data["primary_network"]
        nodes_dict = primary_network["nodes"]
        # Load the nodes
        self.__read_nodes_from_primary_network(nodes_dict)

    def __read_nodes_from_primary_network(self, data):
        """
        Reads the nodes from the primary network, parses them, then verifies them.
            - No duplicates
        :return:
        """
        # Go through every node and create a node from it
        for node_dict in data:
            node = self.__read_and_create_node(node_dict)
            # Check that the node creates no duplicates
            if node.network_id in self.__network_node_ids:
                raise NodeWithNetworkIdAlreadyExistsInNetwork(node)
            if node.power_id in self.__power_node_ids:
                raise NodeWithPowerIdAlreadyExistsInNetwork(node)

            # No errors, add to sets and list
            self.__network_node_ids.add(node.network_id)
            self.__power_node_ids.add(node.power_id)
            self.nodes.append(node)

    def __read_and_create_node(self, node_dict):
        """
        Reads a dict, creates a node and returns it.
        :param node_dict:
        :return:
        """
        # Just get the values that can be easily fetched
        power_id = node_dict["power_network_id"]
        network_id = node_dict["id"]
        location = node_dict["location"]

        nics = []
        # Convert the NIC strings to NICs
        for nic_type in node_dict["nic_card_types"]:
            nic = None
            if nic_type["type"] == "p2p":
                nic = P2PNIC()
            elif nic_type["type"] == "wifi":
                nic = WiFiNIC(nic_type["access_point"])
            else:
                raise InvalidNetworkType
            # Add the nic to end
            nics.append(nic)

        # Create a node and return it
        return Node(power_id, network_id, location, nics)
