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
    type = "base"

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError


class ControlAppConnectionPathType(BaseAppConnectionPathType):
    """
    A control app connection path type
    """
    type = "control"


class ActuatorAppConnectionPathType(BaseAppConnectionPathType):
    """
    A actuator app connection path type
    """
    type = "actuator"
