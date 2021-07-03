"""
Created on August 05, 2020
File contains the types of network connections

@file    AppConnectionsTypes.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.05
@version 0.1
@company University of Alberta - Computing Science
"""


class BaseAppConnectionPathType:
    """
    The base app connection type.
    """
    # Stores the type of the network connection
    app_conn_type = "base"

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
        If the app_conn_type is equal, return true, otherwise false.
        :param other:
        :return:
        """
        if isinstance(other, BaseAppConnectionPathType):
            return self.app_conn_type == other.app_conn_type
        return False

    def __ne__(self, other):
        """
        If the app_conn_type is equal, return true, otherwise false.
        :param other:
        :return:
        """
        return not self.__eq__(other)


class ControlAppConnectionPathType(BaseAppConnectionPathType):
    """
    A control app connection path type
    """
    app_conn_type = "control"


class ActuatorAppConnectionPathType(BaseAppConnectionPathType):
    """
    A actuator app connection path type
    """
    app_conn_type = "actuator"
