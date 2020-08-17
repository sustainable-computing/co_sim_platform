"""
Created on August 05, 2020
File contains the types of network connections

@file    AppConnectionsTestCases.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.05
@version 0.1
@company University of Alberta - Computing Science
"""

import unittest
from config.reader.AppConnections import AppConnections
from config.reader.AppConnectionsTypes import ControlAppConnectionPathType, ActuatorAppConnectionPathType, \
    BaseAppConnectionPathType
from config.reader.ConfigErrors import InvalidAppConnectionType


class AppConnectionsTestCases(unittest.TestCase):
    """
    Tests were created to test the AppConnections class
    """

    def test_sender_none(self):
        """
        Create a app connection where the sender is none, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            app_conn = AppConnections(None, "123", ControlAppConnectionPathType())

    def test_sender_empty(self):
        """
        Create a app connection where the sender is empty, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            app_conn = AppConnections("", "123", ControlAppConnectionPathType())

    def test_sender_type(self):
        """
        Create a app connection where the sender is non-string, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            app_conn = AppConnections(1, "123", ControlAppConnectionPathType())

    def test_receiver_none(self):
        """
        Create a app connection where the receiver is none, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            app_conn = AppConnections("123", None, ControlAppConnectionPathType())

    def test_receiver_empty(self):
        """
        Create a app connection where the receiver is empty, should throw an error
        :return:
        """
        with self.assertRaises(ValueError):
            app_conn = AppConnections("123", "", ControlAppConnectionPathType())

    def test_receiver_type(self):
        """
        Create a app connection where the receiver is non-string, should throw an error
        :return:
        """
        with self.assertRaises(TypeError):
            app_conn = AppConnections("123", 1, ControlAppConnectionPathType())

    def test_app_connections_base_type(self):
        """
        Create a app connection where the path type is base, should throw an error
        :return:
        """
        with self.assertRaises(InvalidAppConnectionType):
            app_conn = AppConnections("123", "123", BaseAppConnectionPathType())

    def test_app_connections_actuator_type(self):
        """
        Create a app connection where the path type is actuator, no error
        :return:
        """
        app_conn = AppConnections("123", "123", ActuatorAppConnectionPathType())

    def test_app_connections_control_type(self):
        """
        Create a app connection where the path type is control, no error
        :return:
        """
        app_conn = AppConnections("123", "123", ControlAppConnectionPathType())

    def test_eq_equal(self):
        """
        Compare two app cons that have the sender, receiver and path type being equal.
        :return:
        """
        ac1 = AppConnections("123", "123", ControlAppConnectionPathType())
        ac2 = AppConnections("123", "123", ControlAppConnectionPathType())
        self.assertTrue(ac1 == ac2)

        ac1 = AppConnections("321", "123", ActuatorAppConnectionPathType())
        ac2 = AppConnections("321", "123", ActuatorAppConnectionPathType())
        self.assertTrue(ac1 == ac2)

    def test_eq_not_equal_sender(self):
        """
        Compare two app conns that do not have the same sender and test eq operator.
        :return:
        """
        ac1 = AppConnections("123", "123", ControlAppConnectionPathType())
        ac2 = AppConnections("321", "123", ControlAppConnectionPathType())
        self.assertFalse(ac1 == ac2)

    def test_eq_not_equal_receiver(self):
        """
        Compare two app conns that do not have the same receiver and test eq operator.
        :return:
        """
        ac1 = AppConnections("123", "123", ControlAppConnectionPathType())
        ac2 = AppConnections("123", "321", ControlAppConnectionPathType())
        self.assertFalse(ac1 == ac2)

    def test_eq_not_equal_path_type(self):
        """
        Compare two app conns that do not have the same path type and test eq operator.
        :return:
        """
        ac1 = AppConnections("123", "123", ControlAppConnectionPathType())
        ac2 = AppConnections("123", "123", ActuatorAppConnectionPathType())
        self.assertFalse(ac1 == ac2)

        ac1 = AppConnections("123", "123", ActuatorAppConnectionPathType())
        ac2 = AppConnections("123", "123", ControlAppConnectionPathType())
        self.assertFalse(ac1 == ac2)

    def test_ne_equal(self):
        """
        Compare two equal app cons using not equal operator.
        :return:
        """
        ac1 = AppConnections("123", "123", ControlAppConnectionPathType())
        ac2 = AppConnections("123", "123", ControlAppConnectionPathType())
        self.assertFalse(ac1 != ac2)

        ac1 = AppConnections("321", "123", ActuatorAppConnectionPathType())
        ac2 = AppConnections("321", "123", ActuatorAppConnectionPathType())
        self.assertFalse(ac1 != ac2)

    def test_ne_not_equal_sender(self):
        """
        Compare two not equal sender using the not equal operator.
        :return:
        """
        ac1 = AppConnections("123", "123", ControlAppConnectionPathType())
        ac2 = AppConnections("321", "123", ControlAppConnectionPathType())
        self.assertTrue(ac1 != ac2)

    def test_ne_not_equal_receiver(self):
        """
        Compare two not equal receiver using the not equal operator.
        :return:
        """
        ac1 = AppConnections("123", "123", ControlAppConnectionPathType())
        ac2 = AppConnections("123", "321", ControlAppConnectionPathType())
        self.assertTrue(ac1 != ac2)

    def test_ne_not_equal_path_type(self):
        """
        Compare two app conns that do not have the same path type and test != operator.
        :return:
        """
        ac1 = AppConnections("123", "123", ControlAppConnectionPathType())
        ac2 = AppConnections("123", "123", ActuatorAppConnectionPathType())
        self.assertTrue(ac1 != ac2)

        ac1 = AppConnections("123", "123", ActuatorAppConnectionPathType())
        ac2 = AppConnections("123", "123", ControlAppConnectionPathType())
        self.assertTrue(ac1 != ac2)


if __name__ == '__main__':
    unittest.main()
