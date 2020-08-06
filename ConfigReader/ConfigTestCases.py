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
from ConfigErrors import NodeWithNetworkIdAlreadyExistsInNetwork, NodeWithPowerIdAlreadyExistsInNetwork, \
    InvalidNetworkType


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

    def test_duplicate_power_id_nodes(self):
        """
        Passes a file with duplicate power id nodes into Config, should produce an error
        :return:
        """
        # Read the file
        file = open("TestFiles/duplicate_power_id_nodes.json")
        config_dup = Config(file)
        with self.assertRaises(NodeWithPowerIdAlreadyExistsInNetwork):
            config_dup.read_config()
        file.close()

    def test_duplicate_network_id_nodes(self):
        """
        Passes a file with duplicate network id nodes into Config, should produce an error
        :return:
        """
        # Read the file
        file = open("TestFiles/duplicate_network_id_nodes.json")
        config_dup = Config(file)
        with self.assertRaises(NodeWithNetworkIdAlreadyExistsInNetwork):
            config_dup.read_config()
        file.close()

    def test_nic_wrong_type(self):
        """
        Read a file where the NIC type is not valid
        :return:
        """
        # Read the file
        file = open("TestFiles/wrong_type_nic.json")
        config_dup = Config(file)
        with self.assertRaises(InvalidNetworkType):
            config_dup.read_config()
        file.close()


if __name__ == '__main__':
    unittest.main()
