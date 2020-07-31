"""
File contains all the validation tests needed to make sure the values stored in the Classes are valid.
"""
from ConfigErrors import InvalidNICType, InvalidAccessPointValueForNICType


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


def check_network_card_type_and_access_point_value(network_card_types, access_point, valid_nic_types):
    """
    Checks the value of network card type, if it is of type wifi or p2p, then check access point value. If type of
    NIC is wifi, then access_point should not be None, otherwise it should be None
    :param network_card_type:
    :param access_point:
    :param valid_nic_types:
    :return:
    """
    if len(set(network_card_types).intersection(set(valid_nic_types))) != len(network_card_types):
        raise InvalidNICType
    elif "wifi" not in network_card_types and access_point is not None:
        raise InvalidAccessPointValueForNICType
    elif "wifi" in network_card_types:
        # Check to make sure access_point is not None and is a bool
        if access_point is None or not isinstance(access_point, bool):
            raise InvalidAccessPointValueForNICType