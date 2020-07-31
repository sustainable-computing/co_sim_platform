"""
File contains all the validation tests needed to make sure the values stored in the Classes are valid.
"""
from ConfigErrors import InvalidNetworkType, InvalidAccessPointValueForNICType, \
    NetworkConnectionNumberOfNodesNotCorrect, NetworkConnectionHasNodesWithConnectionToSelf

# Stores the valid types of nics
valid_nic_types = ["wifi", "p2p"]

def check_non_empty_non_none_string(to_check):
    """
    Created to check that to_check is not None, is not an empty string and is not of some other type
    :param to_check:
    :return:
    """
    if isinstance(to_check, str) and to_check == "":
        raise ValueError
    elif not isinstance(to_check, str) or to_check is None:
        raise TypeError


def check_location_coordinates(location_to_check):
    """
    Check the location to make sure that it has both x and y parts, then checks that both x and y can be converted
    into doubles.
    :param location_to_check:
    :return:
    """
    if 'x' not in location_to_check or 'y' not in location_to_check:
        raise KeyError

    float(location_to_check['x'])
    float(location_to_check['y'])


def check_network_card_type_and_access_point_value(network_card_types, access_point):
    """
    Checks the value of network card type, if it is of type wifi or p2p, then check access point value. If type of
    NIC is wifi, then access_point should not be None, otherwise it should be None
    :param network_card_type:
    :param access_point:
    :param valid_nic_types:
    :return:
    """
    check_network_connection_type(network_card_types)

    if "wifi" not in network_card_types and access_point is not None:
        raise InvalidAccessPointValueForNICType
    elif "wifi" in network_card_types:
        # Check to make sure access_point is not None and is a bool
        if access_point is None or not isinstance(access_point, bool):
            raise InvalidAccessPointValueForNICType


def check_network_connection_type(network_connection_type):
    """
    Check to see if the network connection type is of a valid type.
    :param network_connection_type:
    :return:
    """
    if len(set(network_connection_type).intersection(set(valid_nic_types))) != len(network_connection_type):
        raise InvalidNetworkType

def check_network_connection_nodes(nodes):
    """
    Method checks to make sure there are only two nodes passed into the connection. Also checks to make sure that each
    node is valid using check_non_empty_non_none_string.
    :param nodes:
    :return:
    """
    if len(nodes) != 2:
        raise NetworkConnectionNumberOfNodesNotCorrect

    if len(set(nodes)) != len(nodes):
        raise NetworkConnectionHasNodesWithConnectionToSelf

    # Now make sure every node is valid
    for node in nodes:
        check_non_empty_non_none_string(node)
