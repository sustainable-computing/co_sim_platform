import unittest
from Node import Node


class NodeTestCases(unittest.TestCase):
    """
    Tests were created to test the Node class
    """

    def test_power_id_none(self):
        """
        Create a power id that is None, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node(None, "test", {"x": "123", "y": "321"})

    def test_power_id_empty(self):
        """
        Create a power id that is an empty string, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("", "test", {"x": "123", "y": "321"})

    def test_power_id_type(self):
        """
        Create a non-empty and non-None power id, should not throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node(1, "test", {"x": "123", "y": "321"})

    def test_network_id_none(self):
        """
        Create a network id that is None, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", None, {"x": "123", "y": "321"})

    def test_network_id_empty(self):
        """
        Create a network id that is an empty string, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "", {"x": "123", "y": "321"})

    def test_network_id_type(self):
        """
        Create a non-empty and non-None network id, should not throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", 1, {"x": "123", "y": "321"})

    def test_missing_location_x(self):
        """
        Create a location with the x missing, should throw an error
        :return:
        """
        with self.assertRaises(KeyError):
            node = Node("test", "test", {"y", "123"})

    def test_missing_location_y(self):
        """
        Create a location with the y missing, should throw an error
        :return:
        """
        with self.assertRaises(KeyError):
            node = Node("test", "test", {"x": "123"})

    def test_non_num_location_x(self):
        """
        Create a non num location for x in node location, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "a", "y": "123.1"})

    def test_non_num_location_y(self):
        """
        Create a non num location for y in node location, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "321", "y": "b"})

    def test_none_location_x(self):
        """
        Create a none location for x in node location, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": None, "y": "123"})

    def test_none_location_y(self):
        """
        Create a none location for y in node location, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "321", "y": None})

    def test_power_id_none_set_attr(self):
        """
        Create a power id that is None, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.power_id = None

    def test_power_id_empty_set_attr(self):
        """
        Create a power id that is an empty string, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.power_id = ""

    def test_power_id_type_set_attr(self):
        """
        Create a non-empty and non-None power id, should not throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.power_id = 1

    def test_network_id_none_set_attr(self):
        """
        Create a network id that is None, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.network_id = None

    def test_network_id_empty_set_attr(self):
        """
        Create a network id that is an empty string, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.network_id = ""

    def test_network_id_type_set_attr(self):
        """
        Create a non-empty and non-None network id, should not throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.network_id = 1

    def test_missing_location_x_set_attr(self):
        """
        Create a location with the x missing, should throw an error
        :return:
        """
        with self.assertRaises(KeyError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.location = {"y": "321"}

    def test_missing_location_y_set_attr(self):
        """
        Create a location with the y missing, should throw an error
        :return:
        """
        with self.assertRaises(KeyError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.location = {"x": "321"}

    def test_non_num_location_x_set_attr(self):
        """
        Create a non num location for x in node location, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.location = {"x": "x", "y": "321"}

    def test_non_num_location_y_set_attr(self):
        """
        Create a non num location for y in node location, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.location = {"x": "123", "y": "y"}

    def test_none_location_x_set_attr(self):
        """
        Create a none location for x in node location, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.location = {"x": None, "y": "123"}

    def test_none_location_y_set_attr(self):
        """
        Create a none location for y in node location, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            node = Node("test", "test", {"x": "123", "y": "321"})
            node.location = {"x": "123", "y": None}


if __name__ == '__main__':
    unittest.main()
