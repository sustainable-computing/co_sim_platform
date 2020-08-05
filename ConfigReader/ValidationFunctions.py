"""
Created on July 30, 2020
File contains all the validation tests needed to make sure the values stored in the Classes are valid.

@file    ValidationFunctions.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.07.30
@version 0.1
@company University of Alberta - Computing Science
"""

from ConfigErrors import InvalidNetworkType, InvalidAccessPointValueForNICType, \
    NetworkConnectionNumberOfNodesNotCorrect, NetworkConnectionHasNodesWithConnectionToSelf
from NICs import P2PNIC, WiFiNIC

# Stores the valid types of nics
valid_nic_types = [P2PNIC, WiFiNIC]


def check_non_empty_non_none_string(to_check):
    """
    Created to check that to_check is not None, is not an empty string and is not of some other type
    :param to_check:
    :return:
    """
    if isinstance(to_check, str) and to_check == "":
        raise ValueError
    elif not isinstance(to_check, str) or to_check is None:
        raise TypeError


def check_location_coordinates(location_to_check):
    """
    Check the location to make sure that it has both x and y parts, then checks that both x and y can be converted
    into doubles.
    :param location_to_check:
    :return:
    """
    if 'x' not in location_to_check or 'y' not in location_to_check:
        raise KeyError

    float(location_to_check['x'])
    float(location_to_check['y'])


def check_nic_types(nics_to_check):
    """
    Check to make sure that all the nics in nics_to_check are of type valid_nic_types and that there are not duplicated.
    :param nics_to_check:
    :return:
    """
    types_found = []
    # Iterate through every type and make sure there are no duplicated
    for nic in nics_to_check:
        found = False

        for valid_nic in valid_nic_types:
            if isinstance(nic, valid_nic):
                found = True
                break

        if not found:
            raise InvalidNetworkType

        types_found.append(nic.type)


def check_network_connection_type(network_connection_type):
    """
    Check to see if the network connection type is of a valid type.
    :param network_connection_type:
    :return:
    """
    if len(set(network_connection_type).intersection(set(valid_nic_types))) != len(network_connection_type):
        raise InvalidNetworkType


def check_network_connection_nodes(nodes):
    """
    Method checks to make sure there are only two nodes passed into the connection. Also checks to make sure that each
    node is valid using check_non_empty_non_none_string.
    :param nodes:
    :return:
    """
    if len(nodes) != 2:
        raise NetworkConnectionNumberOfNodesNotCorrect

    if len(set(nodes)) != len(nodes):
        raise NetworkConnectionHasNodesWithConnectionToSelf

    # Now make sure every node is valid
    for node in nodes:
        check_non_empty_non_none_string(node)
