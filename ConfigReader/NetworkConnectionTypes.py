"""
Created on August 05, 2020
File contains the types of network connections

@file    NetworkConnectionTypes.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.05
@version 0.1
@company University of Alberta - Computing Science
"""


class NetworkConnectionTypeBase:
    """
    The base network connection type.
    """
    # Stores the type of the network connection
    conn_type = "base"

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError

    def __eq__(self, other):
        """
        Checks to see if conn_type of two NetworkConnections is the same
        :param other:
        :return:
        """
        if isinstance(other, NetworkConnectionTypeBase):
            return self.conn_type == other.conn_type
        return False

    def __ne__(self, other):
        """
        Checks to see if conn_type of two NetworkConnections is not the same, opposite of eq
        :param other:
        :return:
        """
        return not self.__eq__(other)


class NetworkConnectionP2P(NetworkConnectionTypeBase):
    """
    A p2p network connection type
    """
    conn_type = "p2p"


class NetworkConnectionWiFi(NetworkConnectionTypeBase):
    """
    A WiFi network connection type
    """
    conn_type = "wifi"
