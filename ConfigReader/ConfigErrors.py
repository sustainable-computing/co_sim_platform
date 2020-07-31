"""
File was created to store all the errors created for Config reading
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

