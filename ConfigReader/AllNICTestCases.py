"""
Created on August 5, 2020
File contains the class that will test NIC class. Super simple in this case.

@file    AllNICTestCases.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.08.05
@version 0.1
@company University of Alberta - Computing Science
"""

import unittest

from NICs import NIC, P2PNIC, WiFiNIC
from ConfigErrors import ImmutableObjectError


class AllNICTestCases(unittest.TestCase):
    """
    Tests were created to test the NIC class and its sub-classes
    """

    def test_type_of_nic_base(self):
        """
        Tests the type of NIC base class. No error
        :return:
        """
        nic = NIC()
        self.assertEqual("base", nic.type, "TYPE FOR BASE NIC CLASS IS NOT base")

    def test_type_of_nic_p2p(self):
        """
        Tests the type of NIC p2p class. No Error
        :return:
        """
        nic = P2PNIC()
        self.assertEqual("p2p", nic.type, "TYPE FOR BASE NIC CLASS IS NOT p2p")

    def test_change_of_type_in_nic_p2p(self):
        """
        Tries to change the type of the P2P NIC card. Should throw an error.
        :return:
        """
        with self.assertRaises(ImmutableObjectError):
            nic = P2PNIC()
            nic.type = "another_type"

    def test_type_of_nic_wifi(self):
        """
        Tests the type of NIC wifi class. No Error
        :return:
        """
        nic = WiFiNIC()
        self.assertEqual("wifi", nic.type, "TYPE FOR BASE NIC CLASS IS NOT wifi")

    def test_change_of_type_in_nic_wifi(self):
        """
        Tries to change the type of the P2P NIC card. Should throw an error.
        :return:
        """
        with self.assertRaises(ImmutableObjectError):
            nic = WiFiNIC()
            nic.type = "another_type"

    def test_access_point_setting_at_init_in_wifi_nic(self):
        """
        Checks that the wifi access point can be set to false/true at the init of WifiNIC
        :return:
        """
        # Create a NIC without setting access_point
        nic = WiFiNIC()
        self.assertEqual(False, nic.access_point, "WIFI NIC ACCESS POINT NOW FALSE WHEN NOT SET IN INIT")
        nic = WiFiNIC(access_point=False)
        self.assertEqual(False, nic.access_point, "WIFI NIC ACCESS POINT NOW FALSE WHEN SET IN INIT")
        nic = WiFiNIC(access_point=True)
        self.assertEqual(True, nic.access_point, "WIFI NIC ACCESS POINT NOW TRUE WHEN SET IN INIT")


if __name__ == '__main__':
    unittest.main()
