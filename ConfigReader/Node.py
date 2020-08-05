"""
Created on July 30, 2020
File contains the class that will store nodes.

@file    Node.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.07.30
@version 0.1
@company University of Alberta - Computing Science
"""

from ConfigErrors import ImmutableObjectError
from ValidationFunctions import check_location_coordinates, check_non_empty_non_none_string, check_nic_types


class Node:
    """
    Class was created to store the information on a node. Solely meant to be used by ConfigReader
    """
    # Stores the id of the node in the power system
    power_id = ""
    # Stores the id of the node in the network
    network_id = ""
    # Stores the network of the system
    location = {}
    # Stores the NIC card type, should be nic objects that are passed in
    nic_types = []
    # If this network card is a wifi card, then this will be used
    access_point = False

    def __init__(self, power_id, network_id, location, nic_types, access_point=None):
        """
        Validates that all the data necessary is present and is of the correct type and then saves it
        :param power_id:
        :param network_id:
        :param location:
        """
        self.__check_power_id_type(power_id)
        self.__check_network_id_type(network_id)
        check_location_coordinates(location)
        check_nic_types(nic_types)

        super(Node, self).__setattr__('power_id', power_id)
        super(Node, self).__setattr__('network_id', network_id)
        super(Node, self).__setattr__('location', location)
        super(Node, self).__setattr__('nic_types', nic_types)
        super(Node, self).__setattr__('access_point', access_point)

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError

    def __check_power_id_type(self, power_id):
        """
        Checks that the power id passed in is a non-empty string.
        :param power_id:
        :return:
        """
        check_non_empty_non_none_string(power_id)

    def __check_network_id_type(self, network_id):
        """
        Checks that the network id passed in is a non-empty string.
        :param network_id:
        :return:
        """
        check_non_empty_non_none_string(network_id)

