import json


class ConfigReader:
    """
    Class was created to read the config file passed in. This is done so that the file is only read once and then the
    data can be passed to each simulator without having to read the file again.
    """
    file = ""

    def __init__(self, file):
        """
        The initializer, saves the file pointer passed in. Since the setting of file starts reading the file, this will
        also read the file passed in
        :param file:
        """
        self.file = file
