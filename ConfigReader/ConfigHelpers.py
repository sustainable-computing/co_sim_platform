"""
Created on August 12, 2020
File contains helper for the config readers/validators.

@file    ConfigHelpers.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.12
@version 0.1
@company University of Alberta - Computing Science
"""
from NICs import WiFiNIC


def find_access_point_in_wifi_nodes(nodes):
    """
    Find and return the access point in the wifi nodes.
    :param nodes:
    :return:
    """
    return get_wifi_node(True, nodes)


def find_non_access_point_in_wifi_nodes(nodes):
    """
    Find and return the non access point in the wifi nodes.
    :param nodes:
    :return:
    """
    return get_wifi_node(False, nodes)


def get_wifi_node(access_point, nodes):
    """
    If access point is true, returns the access point from the nodes, if access point is false, returns the non access
    point from the nodes.
    :param access_point:
    :param nodes:
    :return:
    """
    for node in nodes:
        wifi_nic = get_nic_of_type(node.nic_types, WiFiNIC)
        if wifi_nic.access_point == access_point:
            return node

    return None


def get_nic_of_type(nics, nic_type):
    """
    Go through nics and find the nic that is of type nic_type, otherwise throw a type error.
    :param nics:
    :param nic_type:
    :return:
    """
    for nic in nics:
        if isinstance(nic, nic_type):
            return nic

    raise TypeError(str(nic_type) + " not found in " + str(nics))


def check_if_node_is_of_type(node, node_type):
    """
    Check if a node is of type passed in.
    :return:
    """
    if not isinstance(node, node_type):
        raise TypeError(str(node) + " is not of type " + str(node_type))
