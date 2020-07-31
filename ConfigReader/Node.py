class Node:
    """
    Class was created to store the information on a node. Solely meant to be used by ConfigReader
    """
    # Stores the id of the node in the power system
    power_id = ""
    # Stores the id of the node in the network
    network_id = ""
    # Stores the network of the system
    location = {}

    def __init__(self, power_id, network_id, location):
        """
        Validates that all the data necessary is present and is of the correct type and then saves it
        :param power_id:
        :param network_id:
        :param location:
        """
        self.__check_power_id_type(power_id)
        self.__check_network_id_type(network_id)
        self.__check_location_coordinates(location)

        self.power_id = power_id
        self.network_id = network_id
        self.location = location

    def __setattr__(self, key, value):
        """
        Overridden to check that the value being set to the members is correct before writing it
        :param key:
        :param value:
        :return:
        """
        if key == "power_id":
            self.__check_power_id_type(value)
        elif key == "network_id":
            self.__check_network_id_type(value)
        elif key == "location":
            self.__check_location_coordinates(value)

        super(Node, self).__setattr__(key, value)

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
