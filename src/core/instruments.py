
from PyQt4 import QtCore
from abc import ABCMeta, abstractmethod, abstractproperty


from src.core import Parameter

class Instrument(object):
    '''
    generic instrument class

    for subclass overwrite following functions / properties:
        - _settings_default => parameter object, that is a list of parameters that can be set to configure the instrument
        - update => function that sends parameter changes to the instrument
        - values => dictionary that contains all the values that can be read from the instrument
        - get_values => function that actually requests the values from the instrument
        - is_connected => property that checks if instrument is actually connected
    '''
    __metaclass__ = ABCMeta
    _is_connected = False #internal flag that indicated if instrument is actually connected

    # ========================================================================================
    # ======= Following functions have to be customized for each instrument subclass =========
    # ========================================================================================

    def __init__(self, name=None, settings=None):

        self._settings = self._settings_default

        if settings is not None:
            self.update(settings)

        if name is None:
            name = self.__class__.__name__

        self.name = name

    @abstractproperty
    def _settings_default(self):
        """
        returns the default parameter_list of the instrument this function should be over written in any subclass
        """
        settings_default = Parameter([
            Parameter('test1', 0, int, 'test parameter (int)'),
            Parameter('test2' ,
                      [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                       Parameter('test2_2', 0.0, float, 'test parameter (float)')
                       ])
        ])
        return settings_default

    @abstractmethod
    def update(self, settings):
        '''
        updates the internal dictionary and sends changed values to instrument
        Args:
            settings: parameters to be set
        # mabe in the future:
        # Returns: boolean that is true if update successful

        '''
        self._settings.update(settings)

    @abstractproperty
    def _probes(self):
        """

        Returns: a dictionary that contains the values that can be read from the instrument
        the key is the name of the value and the value of the dictionary is an info

        """
        return {'value1': 'this is some value from the instrument', 'value2': 'this is another'}

    @abstractmethod
    def read_probes(self, key):
        """
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        """
        assert key in self._probes.keys()

        value = None

        return value

    @abstractproperty
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected

    # ========================================================================================
    # ======= Following functions are generic ================================================
    # ========================================================================================
    # do not override this, override get_values instead
    def __getattr__(self, name):
        try:
            return self.read_probes(name)
        except (KeyError):
            #restores standard behavior for missing keys
            raise AttributeError('class ' + type(self).__name__ +' has no attribute ' + str(name))

    def __setattr__(self, key, value):
        try:
            self.update({key: value})
        except (AssertionError, AttributeError, KeyError):
            object.__setattr__(self, key, value)

    def __repr__(self):

        output_string = '{:s} (class type: {:s})'.format(self.name, self.__class__.__name__)

        return output_string

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        assert isinstance(value, str)
        self._name = value

    @property
    def settings(self):
        return self._settings
