from ConfigErrors import ImmutableObjectError


class NetworkConnection:
    """
    Class was created to store the network connections. This includes connections between machines, but not connections
    between applications, ie Server/Client connections will not be stored here.
    """
    def __init__(self, nodes):

    def __setattr__(self, key, value):
        """
        Overridden to ensure that nothing in the class is mutable after creation
        :param key:
        :param value:
        :return:
        """
        raise ImmutableObjectError