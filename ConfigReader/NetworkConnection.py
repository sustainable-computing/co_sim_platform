"""
Created on July 30, 2020
File contains the class that will store network connections.

@file    NetworkConnection.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.07.30
@version 0.1
@company University of Alberta - Computing Science
"""

from ConfigErrors import ImmutableObjectError
from ValidationFunctions import check_network_connection_nodes, check_network_connection_types


class NetworkConnection:
    """
    Class was created to store the network connections. This includes connections between machines, but not connections
    between applications, ie Server/Client connections will not be stored here.
    """
    # Stores the nodes in the connection
    nodes = []
    # Stores the type of connection
    conn_type = ""

    def __init__(self, nodes, conn_type):
        """
        Validates all the information passed in and stores it within itself. Meaning there should be two nodes passed in
        . Each node should be a string, which will be the id of the string
        :param nodes:
        :param type:
        """
        check_network_connection_nodes(nodes)
        check_network_connection_types(conn_type)

        super(NetworkConnection, self).__setattr__('nodes', nodes)
        super(NetworkConnection, self).__setattr__('conn_type', conn_type)

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError
