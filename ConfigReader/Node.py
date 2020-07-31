from ConfigErrors import ImmutableObjectError, InvalidNICType, InvalidAccessPointValueForNICType


class Node:
    """
    Class was created to store the information on a node. Solely meant to be used by ConfigReader
    """
    # Stores the valid types
    __valid_nic_types = ["wifi", "p2p", None]
    # Stores the id of the node in the power system
    power_id = ""
    # Stores the id of the node in the network
    network_id = ""
    # Stores the network of the system
    location = {}
    # Stores the NIC card type
    nic_type = ""
    # If this network card is a wifi card, then this will be used
    access_point = False

    def __init__(self, power_id, network_id, location, nic_type=None, access_point=None):
        """
        Validates that all the data necessary is present and is of the correct type and then saves it
        :param power_id:
        :param network_id:
        :param location:
        """
        self.__check_power_id_type(power_id)
        self.__check_network_id_type(network_id)
        self.__check_location_coordinates(location)
        self.__check_network_card_type_and_access_point_value(nic_type, access_point)

        super(Node, self).__setattr__('power_id', power_id)
        super(Node, self).__setattr__('network_id', network_id)
        super(Node, self).__setattr__('location', location)
        super(Node, self).__setattr__('nic_type', nic_type)
        super(Node, self).__setattr__('access_point', access_point)

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError

    def __check_network_card_type_and_access_point_value(self, network_card_type, access_point):
        """
        Checks the value of network card type, if it is of type wifi or p2p, then check access point value. If type of
        NIC is wifi, then access_point should not be None, otherwise it should be None
        :param network_card_type:
        :param access_point:
        :return:
        """
        if not network_card_type in self.__valid_nic_types:
            raise InvalidNICType
        elif network_card_type != "wifi" and access_point is not None:
            raise InvalidAccessPointValueForNICType
        elif network_card_type == "wifi":
            # Check to make sure access_point is not None and is a bool
            if access_point is None or not isinstance(access_point, bool):
                raise InvalidAccessPointValueForNICType

    def __check_power_id_type(self, power_id):
        """
        Checks that the power id passed in is a non-empty string.
        :param power_id:
        :return:
        """
        self.__check_non_empty_non_none_string(power_id)

    def __check_network_id_type(self, network_id):
        """
        Checks that the network id passed in is a non-empty string.
        :param network_id:
        :return:
        """
        self.__check_non_empty_non_none_string(network_id)

    def __check_non_empty_non_none_string(self, to_check):
        """
        Created to check that to_check is not None, is not an empty string and is not of some other type
        :param to_check:
        :return:
        """
        if isinstance(to_check, str) and to_check == "":
            raise ValueError
        elif not isinstance(to_check, str) or to_check is None:
            raise TypeError

    def __check_location_coordinates(self, location_to_check):
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
