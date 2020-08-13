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
    NetworkConnectionNumberOfNodesNotCorrect, NetworkConnectionHasNodesWithConnectionToSelf, \
    InvalidNetworkConnectionType, InvalidAppConnectionType
from NICs import P2PNIC, WiFiNIC
from NetworkConnectionTypes import NetworkConnectionWiFi, NetworkConnectionP2P
from AppConnectionsTypes import ControlAppConnectionPathType, ActuatorAppConnectionPathType
from math import sqrt
from ConfigHelpers import find_access_point_in_wifi_nodes, find_non_access_point_in_wifi_nodes

# Stores the valid types of nics
valid_nic_types = [P2PNIC, WiFiNIC]
valid_network_connection_types = [NetworkConnectionP2P, NetworkConnectionWiFi]
valid_app_connection_types = [ActuatorAppConnectionPathType, ControlAppConnectionPathType]


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

        types_found.append(nic.nic_type)


def check_if_passed_in_is_of_valid_type(passed_in, valid_types):
    """
    Iterates through valid_types to check if passed_in is of that type.
    :param passed_in:
    :param valid_types:
    :return:
    """
    found = False
    for valid_type in valid_types:
        if isinstance(passed_in, valid_type):
            found = True
            break

    return found


def check_network_connection_types(network_connection_type):
    """
    Check to see if the network connection type is of a valid type.
    :param network_connection_type:
    :return:
    """
    found = check_if_passed_in_is_of_valid_type(network_connection_type, valid_network_connection_types)

    if not found:
        raise InvalidNetworkConnectionType


def check_app_connection_types(app_connection_type):
    """
    Check if the app connection type is of a valid type
    :param app_connection_type:
    :return:
    """
    found = check_if_passed_in_is_of_valid_type(app_connection_type, valid_app_connection_types)

    if not found:
        raise InvalidAppConnectionType


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


def check_distance_between_wifi_access_point_and_node(nodes):
    """
    Check the distance between ap and node to make sure it is less than 50m.
    :param nodes:
    :return:
    """
    # Make sure there are only two nodes in nodes
    if len(nodes) != 2:
        raise NetworkConnectionNumberOfNodesNotCorrect

    ap = find_access_point_in_wifi_nodes(nodes)
    node = find_non_access_point_in_wifi_nodes(nodes)

    distance = sqrt(((ap.location['x'] - node.location['x']) ** 2) + ((ap.location['y'] - node.location['y']) ** 2))

    if distance < 50:
        return True
    else:
        return False
