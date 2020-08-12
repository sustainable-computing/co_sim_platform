"""
Created on August 05, 2020
File contains the app connections class, will be used to hold connections between senders and receivers.

@file    AppConnections.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.05
@version 0.1
@company University of Alberta - Computing Science
"""

from ValidationFunctions import check_non_empty_non_none_string, check_app_connection_types


class AppConnections:
    """
    Holds the connection between the server and the receiver and the type of connection
    """
    # The node sending the data
    sender = ""
    # The node receiving the data
    receiver = ""
    # The type of connection
    path_type = None

    def __init__(self, sender, receiver, path_type):
        """
        Just validates the sender, the receiver and the path type, then assigns it to the members.
        :param sender:
        :param receiver:
        :param path_type:
        """
        # Check that the sender and the receiver ids are valid
        check_non_empty_non_none_string(sender)
        check_non_empty_non_none_string(receiver)
        # Check that the path type is valid
        check_app_connection_types(path_type)

        super(AppConnections, self).__setattr__('sender', sender)
        super(AppConnections, self).__setattr__('receiver', receiver)
        super(AppConnections, self).__setattr__('path_type', path_type)

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
        Compare and make sure the the app connections are equal by comparing sender, receiver and path_type
        :param other:
        :return:
        """
        if isinstance(other, AppConnections):
            return (self.sender == other.sender
                    and self.receiver == other.receiver
                    and self.path_type == other.path_type)
        return False

    def __ne__(self, other):
        """
        Returns the opposite of eq.
        :param other:
        :return:
        """
        return not self.__eq__(other)