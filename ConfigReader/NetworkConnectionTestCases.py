"""
Created on July 30, 2020
Test cases for testing NetworkConnections

@file    NetworkConnectionTestCases.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.07.30
@version 0.1
@company University of Alberta - Computing Science
"""

import unittest
from ConfigErrors import NetworkConnectionNumberOfNodesNotCorrect, NetworkConnectionHasNodesWithConnectionToSelf, \
    InvalidNetworkConnectionType
from NetworkConnection import NetworkConnection
from NetworkConnectionTypes import NetworkConnectionP2P, NetworkConnectionTypeBase, NetworkConnectionWiFi


class NetworkConnectionTestCases(unittest.TestCase):
    """
    Tests were created to test the NetworkConnection class
    """
    def test_too_many_nodes(self):
        """
        Creates a NetworkConnection with too many nodes, should throw an error
        :return:
        """
        with self.assertRaises(NetworkConnectionNumberOfNodesNotCorrect):
            nc = NetworkConnection(["123", "321", "5432"], NetworkConnectionP2P())

    def test_too_few_nodes(self):
        """
        Create a NetworkConnection with too few nodes, should throw an error
        :return:
        """
        with self.assertRaises(NetworkConnectionNumberOfNodesNotCorrect):
            nc = NetworkConnection(["123", "321", "5432"], NetworkConnectionWiFi())

    def test_network_connection_to_self(self):
        """
        Create a NetworkConnection where a node is connected to itself, should throw an error
        :return:
        """
        with self.assertRaises(NetworkConnectionHasNodesWithConnectionToSelf):
            nc = NetworkConnection(["123", "123"], NetworkConnectionWiFi())

    def test_correct_number_of_nodes(self):
        """
        Creates a NetworkConnection with the correct number of nodes, should not throw an error
        :return:
        """
        nc = NetworkConnection(["123", "312"], NetworkConnectionWiFi())

    def test_correct_network_type_wifi(self):
        """
        Creates a NetworkConnection with an correct type of network ie, wifi
        :return:
        """
        nc = NetworkConnection(["123", "321"], NetworkConnectionWiFi())

    def test_correct_network_type_p2p(self):
        """
        Creates a NetworkConnection with an correct type of network ie, p2p
        :return:
        """
        nc = NetworkConnection(["123", "321"], NetworkConnectionP2P())

    def test_incorrect_network_type(self):
        """
        Creates a NetworkConnection with an incorrect type of network ie, not wifi and not p2p, should throw an error
        :return:
        """
        with self.assertRaises(InvalidNetworkConnectionType):
            nc = NetworkConnection(["123", "321"], NetworkConnectionTypeBase())


if __name__ == '__main__':
    unittest.main()
