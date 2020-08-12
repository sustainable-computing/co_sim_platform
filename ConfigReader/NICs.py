"""
Created on August 5, 2020
File contains all NIC type classes.

@file    NICs.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.05
@version 0.1
@company University of Alberta - Computing Science
"""
from ConfigErrors import ImmutableObjectError


class NIC:
    """
    Created to store the base type of NIC, where its not specified to be p2p or wifi, etc.
    """
    # Stores the type of card, this cannot be set, each class has its own type that is set but cannot be changed
    nic_type = "base"

    def __str__(self):
        """
        Returns a description of the nic
        :return:
        """
        return self.nic_type

    def __eq__(self, other):
        """
        Method checks to see if the type of other is correct and if type var is equal in self and other.
        :param other:
        :return:
        """
        if isinstance(other, NIC):
            return self.nic_type == other.nic_type
        return False

    def __ne__(self, other):
        """
        Returns the opposite value of __eq__, compares type
        :param other:
        :return:
        """
        return not self.__eq__(other)


class P2PNIC(NIC):
    """
    Created to store the p2p NIC card.
    """
    # Stores the type of card, this cannot be set, each class has its own type that is set but cannot be changed
    nic_type = "p2p"

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError


class WiFiNIC(NIC):
    """
    Created to store the Wifi NIC card.
    """
    # Stores the type of card, this cannot be set, each class has its own type that is set but cannot be changed
    nic_type = "wifi"
    # Indicates if the wifi card is an access-point or not, by default its not
    access_point = False

    def __init__(self, access_point=False):
        """
        Created so that the value of access point can be set on creation of the class
        :param access_point:
        """
        super(WiFiNIC, self).__setattr__('access_point', access_point)

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError

    def __str__(self):
        """
        Returns a description of the nic
        :return:
        """
        return self.nic_type + ", access_point: " + str(self.access_point)

    def __eq__(self, other):
        """
        Method checks to see if the type of other is correct and if type var is equal in self and other.
        :param other:
        :return:
        """
        if super(WiFiNIC, self).__eq__(other):
            return self.access_point == other.access_point
        return False

    def __ne__(self, other):
        """
        Returns the opposite value of __eq__, compares type
        :param other:
        :return:
        """
        return not self.__eq__(other)
