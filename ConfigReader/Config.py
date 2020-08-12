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
    NodeWithPowerIdAlreadyExistsInNetwork, NodeInNetworkConnectionDoesNotExist, NetworkConnectionAlreadyExists, \
    InvalidNetworkConnectionType, NoAccessPointFoundInNetworkConnection, NoNonAccessPointFoundInNetworkConnection, \
    NodeInNetworkConnectionDoesHaveCorrectNIC, NodeInAppConnectionDoesNotExist, InvalidAppConnectionType
from NetworkConnection import NetworkConnection
from AppConnections import AppConnections
from AppConnectionsTypes import ControlAppConnectionPathType, ActuatorAppConnectionPathType
from NetworkConnectionTypes import NetworkConnectionP2P, NetworkConnectionWiFi
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
    __network_connection_ids = set()
    # Stores the app connections
    app_connections = []

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
        primary_network_dict = data["primary_network"]

        # Load the nodes
        nodes_dict = primary_network_dict["nodes"]
        self.__read_nodes_from_network(nodes_dict)

        # Loads the network connections in the primary network
        network_layout_dict = primary_network_dict["network_layout"]
        self.__read_network_connections(network_layout_dict)

        # Loads the app connections
        app_connections_dict = primary_network_dict["app_connections"]
        self.__read_app_connections(app_connections_dict)

    def __read_nodes_from_network(self, data):
        """
        Reads the nodes from the primary network, parses them, then verifies them.
            - No duplicates
        :return:
        """
        # Go through every node and create a node from it
        for node_dict in data:
            node = self.__read_and_create_node(node_dict)
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
                raise InvalidNetworkType(nic_type)
            # Add the nic to end
            nics.append(nic)

        node = Node(power_id, network_id, location, nics)
        # Check that the node creates no duplicates
        if network_id in self.__network_node_ids:
            raise NodeWithNetworkIdAlreadyExistsInNetwork(node)
        if power_id in self.__power_node_ids:
            raise NodeWithPowerIdAlreadyExistsInNetwork(node)

        return node

    def __read_network_connections(self, network_layout_dict):
        """
        Reads the network connections between nodes, parses them and then verifies them.
            - No duplicates
            - Both nodes exist
            - Both nodes have correct type of NIC
        :return:
        """
        # Go through each connection
        for network_conn_dict in network_layout_dict:
            network_connection = self.__read_and_create_network_connections(network_conn_dict)
            self.network_connections.append(network_connection)
            self.__network_connection_ids.add(tuple(sorted([network_connection.nodes[0], network_connection.nodes[1]])))

    def __read_app_connections(self, app_connections_dict):
        """
        Reads the app connections between nodes, parses them and verifies them.
            - Both nodes exist in the app connection
        :param app_connections_dict:
        :return:
        """
        # Go through each app connection
        for app_conn_dict in app_connections_dict:
            app_conn = self.__read_application_connections(app_conn_dict)
            self.app_connections.append(app_conn)

    def __read_and_create_network_connections(self, network_conn_dict):
        """
        Reads a network connection, the nodes and the type, converts it to a NetworkConnection class, and verifies the
        type connection.
        :param self:
        :param network_conn_dict:
        :return:
        """
        # Get the nodes
        node_one = network_conn_dict["nodes"][0]
        node_two = network_conn_dict["nodes"][1]

        # Check the nodes exist
        if node_one not in self.__network_node_ids:
            raise NodeInNetworkConnectionDoesNotExist(node_one)
        if node_two not in self.__network_node_ids:
            raise NodeInNetworkConnectionDoesNotExist(node_two)

        node_one_found = self.__get_node_with_network_id(node_one)
        node_two_found = self.__get_node_with_network_id(node_two)

        # Now check if the connection already exists
        if tuple(sorted([node_one, node_two])) in self.__network_connection_ids:
            raise NetworkConnectionAlreadyExists(node_one_found, node_two_found)

        # Now check if the network connection type is valid
        if network_conn_dict["type"] == "p2p":
            conn_type = NetworkConnectionP2P()
            if not node_one_found.has_p2p_card():
                raise NodeInNetworkConnectionDoesHaveCorrectNIC(node_one_found)

            if not node_two_found.has_p2p_card():
                raise NodeInNetworkConnectionDoesHaveCorrectNIC(node_two_found)
            # No additional validation required
        elif network_conn_dict["type"] == "wifi":
            if not node_one_found.has_wifi_card():
                raise NodeInNetworkConnectionDoesHaveCorrectNIC(node_one_found)

            if not node_two_found.has_wifi_card():
                raise NodeInNetworkConnectionDoesHaveCorrectNIC(node_two_found)

            conn_type = NetworkConnectionWiFi()
            found_access_point = False
            found_non_access_point = False
            # In this case, we need to verify that at least one of the wifi nodes is an access point and the other is
            # not

            if not node_one_found.is_wifi_access_point() or not node_two_found.is_wifi_access_point():
                found_non_access_point = True

            if node_one_found.is_wifi_access_point() or node_two_found.is_wifi_access_point():
                found_access_point = True

            # Now check if access point and non-access point node in the network connection has been found
            if not found_non_access_point:
                raise NoNonAccessPointFoundInNetworkConnection(str(node_one_found), str(node_two_found))

            if not found_access_point:
                raise NoAccessPointFoundInNetworkConnection(str(node_one_found), str(node_two_found))
        else:
            raise InvalidNetworkConnectionType(network_conn_dict["type"])

        # Create a conn and return it
        return NetworkConnection([node_one, node_two], conn_type)

    def __read_application_connections(self, app_conn_dict):
        """
        Reads the application connections, validates the connections by making sure the nodes exist. It does not however
        validate the network connection to determine reachability.
        :return:
        """
        # Get the nodes
        sender = app_conn_dict["sender"]
        receiver = app_conn_dict["receiver"]

        # Check the nodes exist
        if sender not in self.__network_node_ids:
            raise NodeInAppConnectionDoesNotExist(sender)
        if receiver not in self.__network_node_ids:
            raise NodeInAppConnectionDoesNotExist(receiver)

        # Get the nodes if they exist, or it'll never get to this point
        sender_found = self.__get_node_with_network_id(sender)
        receiver_found = self.__get_node_with_network_id(receiver)

        # Check if the connection path type is valid
        path_type = None
        if app_conn_dict["path_type"] == "control":
            path_type = ControlAppConnectionPathType()
        elif app_conn_dict["path_type"] == "actuator":
            path_type = ActuatorAppConnectionPathType()
        else:
            raise InvalidAppConnectionType

        # Return an app connection type
        return AppConnections(sender_found.network_id, receiver_found.network_id, path_type)

    def __get_node_with_network_id(self, network_id):
        """
        Returns the node with the passed in network id if found, else return None
        :param network_id:
        :return:
        """
        for node in self.nodes:
            if node.network_id == network_id:
                return node

        return None
