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

from config.reader.ConfigErrors import ImmutableObjectError
from config.reader.ValidationFunctions import check_location_coordinates, check_non_empty_non_none_string, \
    check_nic_types
from config.reader.NICs import P2PNIC, WiFiNIC

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

    def __init__(self, power_id, network_id, location, nic_types):
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
        super(Node, self).__setattr__('location', {'x': float(location['x']), 'y': float(location['y'])})
        super(Node, self).__setattr__('nic_types', nic_types)

    def has_p2p_card(self):
        """
        Check the nics to see if it has a p2p card.
        :return:
        """
        return self.__has_type_of_card(P2PNIC)

    def has_wifi_card(self):
        """
        Check the nics to see if it has a wifi card.
        :return:
        """
        return self.__has_type_of_card(WiFiNIC)

    def is_wifi_access_point(self):
        """
        Check the nics to see if it has a wifi card.
        :return:
        """
        # Get wifi cards
        wifi_cards = self.__get_type_of_cards(WiFiNIC)
        if len(wifi_cards) > 0:
            for card in wifi_cards:
                if card.access_point:
                    return True

        return False

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError

    def __has_type_of_card(self, card_type):
        """
        Check to see if Node has a type of card in nic_types
        :param card_type:
        :return:
        """
        if len(self.__get_type_of_cards(card_type)) > 0:
            return True
        else:
            return False

    def __get_type_of_cards(self, card_type):
        """
        Gets and returns all the cards of type, well type
        :param card_type:
        :return:
        """
        to_return = []
        for card in self.nic_types:
            if isinstance(card, card_type):
                to_return.append(card)

        return to_return

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

    def __eq__(self, other):
        """
        Over-ridden to make it easier to compare two nodes and see if they are equal
        :param other:
        :return:
        """
        # Check type of node
        if isinstance(other, Node):
            return (other.power_id == self.power_id) and \
                    (other.network_id == self.network_id) and \
                    (other.location["x"] == self.location["x"]) and \
                    (other.location["y"] == self.location["y"]) and \
                    (self.__compare_nic_types(other.nic_types))
        return False

    def __ne__(self, other):
        """
        Over-ridden to make it easier to compare two nodes and see if they are not equal. Just inverts the bool returned
        by other.
        :param other:
        :return:
        """
        return not self.__eq__(other)

    def __compare_nic_types(self, other_nics):
        """
        Compare's NICs. They need to be in the same order for this to be successful.
        :param other_nics:
        :return:
        """
        # If the length is not the same, return false
        if len(self.nic_types) != len(other_nics):
            return False

        # If the length if the same, start comparing the NIC types
        for i in range(0, len(self.nic_types)):
            if self.nic_types[i] != other_nics[i]:
                return False

        # Everything matches, return true
        return True

    def __str__(self):
        """
        Returns a string describing the node.
        :return:
        """
        string_to_return = "\nNode Object: \n" \
                           "\t power_id: " + self.power_id + "\n" \
                           "\t network_id: " + self.network_id + "\n" \
                           "\t location: " + self.network_id + "\n" \
                           "\t nics: "

        for nic in self.nic_types:
            string_to_return += ("(" + str(nic) + "), ")

        string_to_return = string_to_return[:-2]
        string_to_return += "\n"

        return string_to_return
