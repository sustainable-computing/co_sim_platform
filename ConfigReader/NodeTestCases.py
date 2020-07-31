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

from Node import Node
from ConfigErrors import ImmutableObjectError, InvalidNetworkType, InvalidAccessPointValueForNICType


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
            node = Node(None, "test", {"x": "123", "y": "321"}, ["p2p"])

    def test_power_id_empty(self):
        """
        Create a power id that is an empty string, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("", "test", {"x": "123", "y": "321"}, ["p2p"])

    def test_power_id_type(self):
        """
        Create a non-empty and non-None power id, should not throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node(1, "test", {"x": "123", "y": "321"}, ["p2p"])

    def test_network_id_none(self):
        """
        Create a network id that is None, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", None, {"x": "123", "y": "321"}, ["p2p"])

    def test_network_id_empty(self):
        """
        Create a network id that is an empty string, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "", {"x": "123", "y": "321"}, ["p2p"])

    def test_network_id_type(self):
        """
        Create a non-empty and non-None network id, should not throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", 1, {"x": "123", "y": "321"}, ["p2p"])

    def test_missing_location_x(self):
        """
        Create a location with the x missing, should throw an error
        :return:
        """
        with self.assertRaises(KeyError):
            node = Node("test", "test", {"y", "123"}, ["p2p"])

    def test_missing_location_y(self):
        """
        Create a location with the y missing, should throw an error
        :return:
        """
        with self.assertRaises(KeyError):
            node = Node("test", "test", {"x": "123"}, ["p2p"])

    def test_non_num_location_x(self):
        """
        Create a non num location for x in node location, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "a", "y": "123.1"}, ["p2p"])

    def test_non_num_location_y(self):
        """
        Create a non num location for y in node location, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "321", "y": "b"}, ["p2p"])

    def test_none_location_x(self):
        """
        Create a none location for x in node location, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": None, "y": "123"}, ["p2p"])

    def test_none_location_y(self):
        """
        Create a none location for y in node location, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "321", "y": None}, ["p2p"])

    def test_invalid_nic_type(self):
        """
        Create a node with an invalid type of nic
        :return:
        """
        with self.assertRaises(InvalidNetworkType):
            node = Node("test", "test", {"x": "321", "y": "123"}, ["not_valid"])

    def test_nic_wifi_with_none_access_point(self):
        """
        Create a node with a wifi nic card, but no access point value passed in
        :return:
        """
        with self.assertRaises(InvalidAccessPointValueForNICType):
            node = Node("test", "test", {"x": "321", "y": "123"}, ["wifi"])

    def test_nic_p2p_with_access_point(self):
        """
        Create a node with a p2p nic card, but with an access point value
        :return:
        """
        with self.assertRaises(InvalidAccessPointValueForNICType):
            node = Node("test", "test", {"x": "321", "y": "123"}, ["p2p"], access_point=False)


if __name__ == '__main__':
    unittest.main()
