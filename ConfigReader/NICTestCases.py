"""
Created on August 5, 2020
File contains the class that will test NIC class. Super simple in this case.

@file    NICTestCases.py
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
        self.assertEqual("base", nic.nic_type, "TYPE FOR BASE NIC CLASS IS NOT base")

    def test_type_of_nic_p2p(self):
        """
        Tests the type of NIC p2p class. No Error
        :return:
        """
        nic = P2PNIC()
        self.assertEqual("p2p", nic.nic_type, "TYPE FOR BASE NIC CLASS IS NOT p2p")

    def test_change_of_type_in_nic_p2p(self):
        """
        Tries to change the type of the P2P NIC card. Should throw an error.
        :return:
        """
        with self.assertRaises(ImmutableObjectError):
            nic = P2PNIC()
            nic.nic_type = "another_type"

    def test_type_of_nic_wifi(self):
        """
        Tests the type of NIC wifi class. No Error
        :return:
        """
        nic = WiFiNIC()
        self.assertEqual("wifi", nic.nic_type, "TYPE FOR BASE NIC CLASS IS NOT wifi")

    def test_change_of_type_in_nic_wifi(self):
        """
        Tries to change the type of the P2P NIC card. Should throw an error.
        :return:
        """
        with self.assertRaises(ImmutableObjectError):
            nic = WiFiNIC()
            nic.nic_type = "another_type"

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

    def test_eq_for_all_types(self):
        """
        Check the equality operator for each type.
        :return:
        """
        nic1 = WiFiNIC()
        nic2 = WiFiNIC()
        self.assertTrue(nic1 == nic2)

        nic1 = P2PNIC()
        nic2 = P2PNIC()
        self.assertTrue(nic1 == nic2)

        nic1 = WiFiNIC(access_point=True)
        nic2 = WiFiNIC(access_point=True)
        self.assertTrue(nic1 == nic2)

        nic1 = WiFiNIC(access_point=True)
        nic2 = WiFiNIC(access_point=False)
        self.assertFalse(nic1 == nic2)

    def test_ne_for_all_types(self):
        """
        Check if the __ne__ operator is working correctly.
        :return:
        """
        nic1 = WiFiNIC()
        nic2 = WiFiNIC()
        self.assertFalse(nic1 != nic2)

        nic1 = P2PNIC()
        nic2 = P2PNIC()
        self.assertFalse(nic1 != nic2)

        nic1 = WiFiNIC(access_point=True)
        nic2 = WiFiNIC(access_point=True)
        self.assertFalse(nic1 != nic2)

        nic1 = WiFiNIC(access_point=True)
        nic2 = WiFiNIC(access_point=False)
        self.assertTrue(nic1 != nic2)


if __name__ == '__main__':
    unittest.main()
