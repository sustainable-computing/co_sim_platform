"""
Created on July 30, 2020
File contains the classes that will read the config files.

@file    ConfigReader.py
@author  Amrinder S. Grewal
@email   asgrewal@ualberta.ca
@date    2020.07.30
@version 0.1
@company University of Alberta - Computing Science
"""

import json


class ConfigReader:
    """
    Class was created to read the config file passed in. This is done so that the file is only read once and then the
    data can be passed to each simulator without having to read the file again.
    """
    def __init__(self, file):
        """
        The initializer, saves the file pointer passed in. Since the setting of file starts reading the file, this will
        also read the file passed in
        :param file:
        """
        self.file = file

    def __setattr__(self, key, value):
        """
        Modified to start reading the file once file has been set
        :param key:
        :param value:
        :return:
        """
        # Call the writer like normal
        super(ConfigReader, self).__setattr__(key, value)
        # Now call the method that will read the file if file was changed
        if key == 'file':
            self.__read_file()

    def __read_file(self):
        """
        Method reads the file pointer that has been stored as the member
        :return:
        """
