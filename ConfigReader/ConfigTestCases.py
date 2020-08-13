"""
Created on August 30, 2020
File contains tests that will test the reading/verification of config files that are being read by Config

@file    ConfigTestCases.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.06
@version 0.1
@company University of Alberta - Computing Science
"""
import unittest
from Config import Config
from Node import Node
from NICs import P2PNIC, WiFiNIC
from NetworkConnection import NetworkConnection
from AppConnections import AppConnections
from AppConnectionsTypes import ControlAppConnectionPathType, ActuatorAppConnectionPathType
from ConfigErrors import NodeWithNetworkIdAlreadyExistsInNetwork, NodeWithPowerIdAlreadyExistsInNetwork, \
    InvalidNetworkType, NetworkConnectionAlreadyExists, NodeInNetworkConnectionDoesHaveCorrectNIC, \
    NoAccessPointFoundInNetworkConnection, NoNonAccessPointFoundInNetworkConnection, \
    NodeInNetworkConnectionDoesNotExist, NodeInAppConnectionDoesNotExist, InvalidAppConnectionType, \
    NodeTooFarAwayFromAccessPoint
from NetworkConnectionTypes import NetworkConnectionP2P, NetworkConnectionWiFi


class ConfigTestCases(unittest.TestCase):
    def test_valid_nodes(self):
        """
        Passes a file which has valid nodes into Config, no error
        :return:
        """
        valid_nodes_list = [
            Node("622", "3", {"x": "100", "y": "120"}, [P2PNIC(), WiFiNIC(True)]),
            Node("612", "4", {"x": "110", "y": "130"}, [P2PNIC()]),
            Node("632", "5", {"x": "120", "y": "140"}, [WiFiNIC()])
        ]
        # Read the file
        file = open("TestFiles/valid_nodes.json")
        config = Config(file)
        config.read_config()
        # Should have read 3 nodes
        self.assertEqual(len(config.nodes), len(valid_nodes_list))

        # Iterate through the nodes to check their properties
        for i in range(0, len(valid_nodes_list)):
            self.assertTrue(valid_nodes_list[i] == config.nodes[i])

        # Everything else should be empty
        self.assertEqual(len(config.network_connections), 0)
        self.assertEqual(len(config.app_connections), 0)
        # Close the file
        file.close()

    def __open_file_and_wait_to_raise(self, file_to_open, exception_type):
        """
        Opens the file passed in, then check if the exception with type is is raised
        :return:
        """
        file = open(file_to_open)
        config = Config(file)

        with self.assertRaises(exception_type):
            config.read_config()

        file.close()

    def __compare_valid_network_connections(self, file_to_open, connections_to_check):
        """
        Open the file, create the connections, then check against connections_to_check
        :param file_to_open:
        :param connections_to_check:
        :return:
        """
        # Read the file
        file = open(file_to_open)
        config = Config(file)
        config.read_config()
        # Check the number of connections is correct
        self.assertEqual(len(connections_to_check), len(config.network_connections))

        # Now iterate and check the network connections
        for i in range(0, len(connections_to_check)):
            self.assertTrue(connections_to_check[i] == config.network_connections[i])

        # Close the file
        file.close()

    def test_duplicate_power_id_nodes(self):
        """
        Passes a file with duplicate power id nodes into Config, should produce an error
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/duplicate_power_id_nodes.json",
                                           NodeWithPowerIdAlreadyExistsInNetwork)

    def test_duplicate_network_id_nodes(self):
        """
        Passes a file with duplicate network id nodes into Config, should produce an error
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/duplicate_network_id_nodes.json",
                                           NodeWithNetworkIdAlreadyExistsInNetwork)

    def test_nic_wrong_type(self):
        """
        Read a file where the NIC type is not valid
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/wrong_type_nic.json",
                                           InvalidNetworkType)

    def test_valid_p2p_network_connections(self):
        """
        Read a file where the network connections are all p2p and are valid.
        :return:
        """
        # Network connections that should be created
        network_conns = [
            NetworkConnection(["11111", "11112"], NetworkConnectionP2P()),
            NetworkConnection(["11112", "11113"], NetworkConnectionP2P()),
            NetworkConnection(["11113", "11115"], NetworkConnectionP2P()),
            NetworkConnection(["11115", "11114"], NetworkConnectionP2P()),
            NetworkConnection(["11114", "11113"], NetworkConnectionP2P()),
        ]

        self.__compare_valid_network_connections("TestFiles/valid_network_connections_p2p.json", network_conns)

    def test_valid_wifi_network_connections(self):
        """
        Read a file where the network connections are all wifi and are valid.
        :return:
        """
        network_conns = [
            NetworkConnection(["21", "22"], NetworkConnectionWiFi()),
            NetworkConnection(["21", "25"], NetworkConnectionWiFi()),
            NetworkConnection(["23", "24"], NetworkConnectionWiFi())
        ]
        self.__compare_valid_network_connections("TestFiles/valid_network_connections_wifi.json", network_conns)

    def test_valid_mixed_network_connections(self):
        """
        Read a file where the network connections are wifi and p2p mixed and are valid.
        :return:
        """
        # Network connections that should be created
        network_conns = [
            NetworkConnection(["1111", "1112"], NetworkConnectionP2P()),
            NetworkConnection(["1112", "1113"], NetworkConnectionP2P()),
            NetworkConnection(["1113", "1115"], NetworkConnectionP2P()),
            NetworkConnection(["1115", "1114"], NetworkConnectionP2P()),
            NetworkConnection(["1114", "1113"], NetworkConnectionP2P()),
            NetworkConnection(["1111", "1115"], NetworkConnectionWiFi()),
        ]
        # Read the file
        self.__compare_valid_network_connections("TestFiles/valid_network_connections_mixed.json", network_conns)

    def test_not_valid_duplicate_p2p(self):
        """
        Read a file where the network connections are all p2p, but are not valid because there are duplicates.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_network_duplicate_p2p.json",
                                           NetworkConnectionAlreadyExists)

    def test_not_valid_duplicate_wifi(self):
        """
        Read a file where the network connections are all wifi, but are not valid because there are duplicates.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_network_duplicate_wifi.json",
                                           NetworkConnectionAlreadyExists)

    def test_not_valid_duplicate_mixed(self):
        """
        Read a file where the network connections are wifi and p2p, but are not valid because there are duplicates.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_network_duplicate_mixed.json",
                                            NetworkConnectionAlreadyExists)

    def test_not_valid_missing_nic_p2p(self):
        """
        Read a file where the network connections p2p, but one of the nodes does not have a p2p nic card.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_network_missing_nic_p2p.json",
                                            NodeInNetworkConnectionDoesHaveCorrectNIC)

    def test_not_valid_missing_nic_wifi(self):
        """
        Read a file where the network connections wifi, but one of the nodes does not have a wifi nic card.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_network_missing_nic_wifi.json",
                                            NodeInNetworkConnectionDoesHaveCorrectNIC)

    def test_not_valid_wifi_no_access_point(self):
        """
        Read a file where the network connections wifi, the connections are valid except there are no access points. So,
        there should be an error.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_network_wifi_no_access_point.json",
                                            NoAccessPointFoundInNetworkConnection)

    def test_not_valid_wifi_only_access_point(self):
        """
        Read a file where the network connections wifi, the connections are valid except there are only access points.
        So, there should be an error.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_network_wifi_no_non_access_point.json",
                                            NoNonAccessPointFoundInNetworkConnection)

    def test_missing_network_id(self):
        """
        Create valid network connections, but the nodes on one of the connections is missing.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_network_missing_node.json",
                                            NodeInNetworkConnectionDoesNotExist)

    def test_node_one_missing(self):
        """
        Check to see if config reader will fail if node one in an app connection is missing. Error should be thrown.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_app_conn_node_one_missing.json",
                                           NodeInAppConnectionDoesNotExist)

    def test_node_two_missing(self):
        """
        Check to see if config reader will fail if node two in an app connection is missing. Error should be thrown.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_app_conn_node_two_missing.json",
                                           NodeInAppConnectionDoesNotExist)

    def test_wrong_connection_types(self):
        """
        Will pass in invalid path type of app connections, errors should be thrown.
        :return:
        """
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_app_conn_wrong_path_type_one.json",
                                           InvalidAppConnectionType)
        self.__open_file_and_wait_to_raise("TestFiles/not_valid_app_conn_wrong_path_type_two.json",
                                           InvalidAppConnectionType)

    def test_valid_app_connection(self):
        """
        Will pass in valid app connections of different types. Should work.
        :return:
        """
        valid_app_conns_list = [
            AppConnections("-111", "-222", ControlAppConnectionPathType()),
            AppConnections("-333", "-444", ActuatorAppConnectionPathType())
        ]
        # Read the file
        file = open("TestFiles/valid_app_conns.json")
        config = Config(file)
        config.read_config()
        # Should have read 3 nodes
        self.assertEqual(len(config.app_connections), len(valid_app_conns_list))

        # Iterate through the nodes to check their properties
        for i in range(0, len(valid_app_conns_list)):
            self.assertTrue(valid_app_conns_list[i] == config.app_connections[i])

        # Close the file
        file.close()

    def test_distance_too_far_p2p(self):
        """
        In this case, the distance should not matter. The layout should be valid.
        :return:
        """
        file = open("TestFiles/valid_network_connections_distance_p2p.json")
        config = Config(file)
        config.read_config()
        file.close()

    def test_distance_too_far_wifi(self):
        """
        In this case, distance should matter, should get an exception.
        :return:
        """
        file = open("TestFiles/invalid_network_connections_distance_wifi.json")
        config = Config(file)

        with self.assertRaises(NodeTooFarAwayFromAccessPoint):
            config.read_config()

        file.close()

    def test_distance_close_enough_wifi(self):
        """
        In this case, distance should matter, but should be valid.
        :return:
        """
        file = open("TestFiles/valid_network_connections_distance_wifi.json")
        config = Config(file)
        config.read_config()
        file.close()

if __name__ == '__main__':
    unittest.main()
