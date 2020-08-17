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
from config.reader.ConfigErrors import NetworkConnectionNumberOfNodesNotCorrect, \
    NetworkConnectionHasNodesWithConnectionToSelf, InvalidNetworkConnectionType
from config.reader.NetworkConnection import NetworkConnection
from config.reader.NetworkConnectionTypes import NetworkConnectionP2P, NetworkConnectionTypeBase, NetworkConnectionWiFi


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

    def test_eq_is_equal_network_connection(self):
        """
        Test network connections that are equal with the == operator.
        :return:
        """
        nc1 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        nc2 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        self.assertTrue(nc1 == nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        nc2 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        self.assertTrue(nc1 == nc2)

    def test_eq_not_equal_network_connection(self):
        """
        Test network connections that are not equal with the == operator.
        :return:
        """
        nc1 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        nc2 = NetworkConnection(["3", "2"], NetworkConnectionP2P())
        self.assertFalse(nc1 == nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        nc2 = NetworkConnection(["1", "3"], NetworkConnectionP2P())
        self.assertFalse(nc1 == nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        nc2 = NetworkConnection(["3", "2"], NetworkConnectionWiFi())
        self.assertFalse(nc1 == nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        nc2 = NetworkConnection(["1", "3"], NetworkConnectionWiFi())
        self.assertFalse(nc1 == nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        nc2 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        self.assertFalse(nc1 == nc2)

    def test_ne_is_equal_network_connection(self):
        """
        Test network connections that are equal with the != operator.
        :return:
        """
        nc1 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        nc2 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        self.assertFalse(nc1 != nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        nc2 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        self.assertFalse(nc1 != nc2)

    def test_ne_not_equal_network_connection(self):
        """
        Test network connections that are not equal with the != operator.
        :return:
        """
        nc1 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        nc2 = NetworkConnection(["3", "2"], NetworkConnectionP2P())
        self.assertTrue(nc1 != nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        nc2 = NetworkConnection(["1", "3"], NetworkConnectionP2P())
        self.assertTrue(nc1 != nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        nc2 = NetworkConnection(["3", "2"], NetworkConnectionWiFi())
        self.assertTrue(nc1 != nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        nc2 = NetworkConnection(["1", "3"], NetworkConnectionWiFi())
        self.assertTrue(nc1 != nc2)

        nc1 = NetworkConnection(["1", "2"], NetworkConnectionWiFi())
        nc2 = NetworkConnection(["1", "2"], NetworkConnectionP2P())
        self.assertTrue(nc1 != nc2)

    def test_eq_is_equal_network_connection_type(self):
        """
        Check the connection type with == when they are both equal
        :return:
        """
        nct1 = NetworkConnectionWiFi()
        nct2 = NetworkConnectionWiFi()
        self.assertTrue(nct1 == nct2)

        nct1 = NetworkConnectionP2P()
        nct2 = NetworkConnectionP2P()
        self.assertTrue(nct1 == nct2)

    def test_eq_not_equal_network_connection_type(self):
        """
        Check the connection type with == when they are not equal
        :return:
        """
        nct1 = NetworkConnectionWiFi()
        nct2 = NetworkConnectionP2P()
        self.assertFalse(nct1 == nct2)

        nct1 = NetworkConnectionP2P()
        nct2 = NetworkConnectionWiFi()
        self.assertFalse(nct1 == nct2)

    def test_ne_is_equal_network_connection_type(self):
        """
        Check the connection type with != when they are both equal
        :return:
        """
        nct1 = NetworkConnectionWiFi()
        nct2 = NetworkConnectionWiFi()
        self.assertFalse(nct1 != nct2)

        nct1 = NetworkConnectionP2P()
        nct2 = NetworkConnectionP2P()
        self.assertFalse(nct1 != nct2)

    def test_ne_not_equal_network_connection_type(self):
        """
        Check the connection type with != when they are not equal
        :return:
        """
        nct1 = NetworkConnectionWiFi()
        nct2 = NetworkConnectionP2P()
        self.assertTrue(nct1 != nct2)

        nct1 = NetworkConnectionP2P()
        nct2 = NetworkConnectionWiFi()
        self.assertTrue(nct1 != nct2)


if __name__ == '__main__':
    unittest.main()
