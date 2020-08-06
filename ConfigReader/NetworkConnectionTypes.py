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
    type = "base"

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError


class NetworkConnectionP2P(NetworkConnectionTypeBase):
    """
    A p2p network connection type
    """
    type = "p2p"


class NetworkConnectionWiFi(NetworkConnectionTypeBase):
    """
    A WiFi network connection type
    """
    type = "wifi"
