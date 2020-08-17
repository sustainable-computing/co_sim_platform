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


class InvalidNetworkConnectionType(Exception):
    """Raised when an invalid type of network connection is passed in"""
    pass


class InvalidAppConnectionType(Exception):
    """Raised when an invalid type of app connection is passed in"""
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


class NodeWithNetworkIdAlreadyExistsInNetwork(Exception):
    """Raised when a node with a network id is being created that is already taken."""
    pass


class NodeWithPowerIdAlreadyExistsInNetwork(Exception):
    """Raised when a node with a power id is being created that is already taken."""
    pass


class NodeInNetworkConnectionDoesNotExist(Exception):
    """Raised when a node in a network connection does not exist in nodes part of the file."""
    pass


class NodeInAppConnectionDoesNotExist(Exception):
    """Raised when a node in a applications connection does not exist part of the file."""
    pass


class NodeInNetworkConnectionDoesHaveCorrectNIC(Exception):
    """Raised when a node in a network connection does not have the correct nic."""
    pass


class NetworkConnectionAlreadyExists(Exception):
    """Raised when a network connection between two nodes already exists."""
    pass


class NoAccessPointFoundInNetworkConnection(Exception):
    """Raised when two wifi nodes are connected but an access point has not been found."""
    pass


class NoNonAccessPointFoundInNetworkConnection(Exception):
    """Raised when two wifi nodes are connected but a non-access-point has not been found."""
    pass


class NodeTooFarAwayFromAccessPoint(Exception):
    """Raised when a wifi node and an access point are too far away, for now that is 50m or more."""
    pass
