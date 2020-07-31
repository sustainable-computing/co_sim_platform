"""
Created on July 30, 2020
File was created to store all the errors created for Config reading

@file    ConfigErrors.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.07.30
@version 0.1
@company University of Alberta - Computing Science
"""

class ImmutableObjectError(Exception):
    """Raised when an Immutable object is being edited"""
    pass


class InvalidNetworkType(Exception):
    """Raised when an invalid type of NIC is passed in"""
    pass


class InvalidAccessPointValueForNICType(Exception):
    """Raised when:
     - the value of access point is None or not a bool if NIC is of type wifi
     - the value of access point in not None when the NIC is not wifi
    """
    pass


class NetworkConnectionNumberOfNodesNotCorrect(Exception):
    """Raised when a network connection does not have 2 nodes passed in."""
    pass


class NetworkConnectionHasNodesWithConnectionToSelf(Exception):
    """Raised when a node is connected to itself in the network connection."""
    pass

