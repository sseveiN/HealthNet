hclass EnumField(object):
    """
    Custom enum field to allow enums without installing plugins
    """
    def __init__(self, *string_list):
        """
        Initialize the enum
        :param string_list: List of strings to initialize
        """
        self.__dict__.update([(string, number) for (number, string) in enumerate(string_list)])

    def get_choices(self):
        """
        Gets the choices in the enum
        :return: the enum choices
        """
        return tuple(enumerate(self.__dict__.keys()))

    def choices(self):
        """
        Returns the choices of the enum
        :return: the enum choices
        """
        return self.get_choices()