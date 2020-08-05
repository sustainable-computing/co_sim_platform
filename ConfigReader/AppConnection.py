"""
Created on July 30, 2020

@file    AppConnection.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.07.30
@version 0.1
@company University of Alberta - Computing Science
"""


class AppConnection:
    """
    Class was created to store the application connections. This does not include physical connections between nodes,
    it only includes server/client connections between nodes
    """
    # Stores the server
    server = ""
    # Stores the client
    client = ""
    # Store the type of the client
    client_type = ""

    def __init__(self, nodes, conn_type):
        """
        Validates all the information passed in and stores it within itself. Meaning the server and client id should be
        of type string and not empty. The client type should be of type sensor or controller. Not other strings or
        actuator.
        :param nodes:
        :param type:
        """
        # check_network_connection_nodes(nodes)
        # super(NetworkConnection, self).__setattr__('conn_type', conn_type)

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError
