"""
Created on July 30, 2020
File contains the class that will store nodes.

@file    NodeTestCases.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.07.30
@version 0.1
@company University of Alberta - Computing Science
"""
import unittest

from config.reader.Node import Node
from config.reader.NICs import P2PNIC, WiFiNIC, NIC
from config.reader.ConfigErrors import InvalidNetworkType, InvalidAccessPointValueForNICType


class NodeTestCases(unittest.TestCase):
    """
    Tests were created to test the Node class
    """

    def test_power_id_none(self):
        """
        Create a power id that is None, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node(None, "test", {"x": "123", "y": "321"}, [P2PNIC()])

    def test_power_id_empty(self):
        """
        Create a power id that is an empty string, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("", "test", {"x": "123", "y": "321"}, [P2PNIC()])

    def test_power_id_type(self):
        """
        Create a non-empty and non-None power id, should not throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node(1, "test", {"x": "123", "y": "321"}, [P2PNIC()])

    def test_network_id_none(self):
        """
        Create a network id that is None, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", None, {"x": "123", "y": "321"}, [P2PNIC()])

    def test_network_id_empty(self):
        """
        Create a network id that is an empty string, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "", {"x": "123", "y": "321"}, [P2PNIC()])

    def test_network_id_type(self):
        """
        Create a non-empty and non-None network id, should not throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", 1, {"x": "123", "y": "321"}, [P2PNIC()])

    def test_missing_location_x(self):
        """
        Create a location with the x missing, should throw an error
        :return:
        """
        with self.assertRaises(KeyError):
            node = Node("test", "test", {"y", "123"}, [P2PNIC()])

    def test_missing_location_y(self):
        """
        Create a location with the y missing, should throw an error
        :return:
        """
        with self.assertRaises(KeyError):
            node = Node("test", "test", {"x": "123"}, [P2PNIC()])

    def test_non_num_location_x(self):
        """
        Create a non num location for x in node location, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "a", "y": "123.1"}, [P2PNIC()])

    def test_non_num_location_y(self):
        """
        Create a non num location for y in node location, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "321", "y": "b"}, [P2PNIC()])

    def test_none_location_x(self):
        """
        Create a none location for x in node location, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": None, "y": "123"}, [P2PNIC()])

    def test_none_location_y(self):
        """
        Create a none location for y in node location, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "321", "y": None}, [P2PNIC()])

    def test_no_nic(self):
        """
        Create a Node with no NIC, should produce no error
        :return:
        """
        node = Node("test", "test", {"x": "321", "y": "321"}, [])

    def test_incorrect_type_nic(self):
        """
        Create a base type of NIC and a string, should create an error.
        :return:
        """
        with self.assertRaises(InvalidNetworkType):
            node = Node("test", "test", {"x": "321", "y": "321"}, [NIC()])

        with self.assertRaises(InvalidNetworkType):
            node = Node("test", "test", {"x": "321", "y": "321"}, ["p2p"])

    def test_correct(self):
        """
        Everything is correct, no error should be raised.
        :return:
        """
        node = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        node = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC()])
        node = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC(access_point=True)])

    def test_eq_incorrect_type(self):
        """
        Create two identical nodes and check if they are equal. They should not be equal.
        :return:
        """
        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = "123"
        self.assertFalse(n1 == n2)

    def test_eq_is_equal(self):
        """
        Create two identical nodes and check if they are equal. They should be equal.
        :return:
        """
        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertTrue(n1 == n2)

    def test_eq_not_equal(self):
        """
        Create two non-identical nodes and check if they are equal. They should not be equal.
        :return:
        """
        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test1", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertFalse(n1 == n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test1", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertFalse(n1 == n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "3211", "y": "321"}, [P2PNIC()])
        self.assertFalse(n1 == n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "321", "y": "3211"}, [P2PNIC()])
        self.assertFalse(n1 == n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC()])
        self.assertFalse(n1 == n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC(), P2PNIC()])
        self.assertFalse(n1 == n2)

    def test_ne_incorrect_type(self):
        """
        Create two identical nodes and check if they are equal. Should be true, they are not equal
        :return:
        """
        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = "123"
        self.assertTrue(n1 != n2)

    def test_ne_is_equal(self):
        """
        Create two identical nodes check if they are not equal. Should be false, since they are equal.
        :return:
        """
        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertFalse(n1 != n2)

    def test_ne_not_equal(self):
        """
        Create two non-identical nodes to check if they are not equal. Should be true, since they are not equal.
        :return:
        """
        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test1", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertTrue(n1 != n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test1", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertTrue(n1 != n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "3211", "y": "321"}, [P2PNIC()])
        self.assertTrue(n1 != n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "321", "y": "3211"}, [P2PNIC()])
        self.assertTrue(n1 != n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC()])
        self.assertTrue(n1 != n2)

        n1 = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        n2 = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC(), P2PNIC()])
        self.assertTrue(n1 != n2)

    def test_has_p2p_card(self):
        """
        Check to see if has_p2p_card method is working properly
        :return:
        """
        n = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertTrue(n.has_p2p_card())

        n = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC()])
        self.assertFalse(n.has_p2p_card())

        n = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC(), WiFiNIC()])
        self.assertTrue(n.has_p2p_card())

    def test_has_wifi_card(self):
        """
        Check to see if has_wifi_card method is working properly
        :return:
        """
        n = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertFalse(n.has_wifi_card())

        n = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC()])
        self.assertTrue(n.has_wifi_card())

        n = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC(), WiFiNIC()])
        self.assertTrue(n.has_wifi_card())

    def test_is_wifi_access_point(self):
        """
        Check to see if is_wifi_access_point method is working properly
        :return:
        """
        n = Node("test", "test", {"x": "321", "y": "321"}, [P2PNIC()])
        self.assertFalse(n.is_wifi_access_point())

        n = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC()])
        self.assertFalse(n.is_wifi_access_point())

        n = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC(access_point=False)])
        self.assertFalse(n.is_wifi_access_point())

        n = Node("test", "test", {"x": "321", "y": "321"}, [WiFiNIC(access_point=True)])
        self.assertTrue(n.is_wifi_access_point())

if __name__ == '__main__':
    unittest.main()
