
from PyQt4 import QtCore
from abc import ABCMeta, abstractmethod, abstractproperty
from copy import deepcopy
import yaml
from src.core import Parameter
from src.core.read_write_functions import save_b26_file

class Instrument(object):
    '''
    generic instrument class

    for subclass overwrite following old_functions / properties:
        - _settings_default => parameter object, that is a list of parameters that can be set to configure the instrument
        - update => function that sends parameter changes to the instrument
        - values => dictionary that contains all the values that can be read from the instrument
        - get_values => function that actually requests the values from the instrument
        - is_connected => property that checks if instrument is actually connected
    '''
    __metaclass__ = ABCMeta
    _is_connected = False #internal flag that indicated if instrument is actually connected
    _initialized = False

    # ========================================================================================
    # ======= Following old_functions have to be customized for each instrument subclass =========
    # ========================================================================================

    def __init__(self, name=None, settings=None):
        # make a deepcopy of the default settings
        # because _DEFAULT_SETTINGS is a class variable and thus shared among the instances
        self._settings = deepcopy(self._DEFAULT_SETTINGS)
        # todo: check why the following two lines give an error
        # apply settings to instrument
        # self.update(self._settings)
        if settings is not None:
            self.update(settings)

        if name is None:
            name = self.__class__.__name__

        self.name = name

        self._initialized = True

    @abstractproperty
    def _DEFAULT_SETTINGS(self):
        """
        returns the default parameter_list of the instrument this function should be over written in any subclass
        """
        pass

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
    def _PROBES(self):
        """

        Returns: a dictionary that contains the values that can be read from the instrument
        the key is the name of the value and the value of the dictionary is an info

        """
        pass

    @abstractmethod
    def read_probes(self, key):
        """
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        """
        assert key in self._PROBES.keys()

        value = None

        return value

    # @abstractproperty
    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected

    # ========================================================================================
    # ======= Following old_functions are generic ================================================
    # ========================================================================================
    # do not override this, override get_values instead
    def __getattr__(self, name):
        # # # === OLD JG =========== start
        # # not sure if keyerror is the right thing to catch
        # try:
        #     return self.read_probes(name)
        # except (KeyError):
        #     #restores standard behavior for missing keys
        #     raise AttributeError('class ' + type(self).__name__ +' has no attribute ' + str(name))
        # # === OLD JG =========== end

        try:
            return self.read_probes(name)
        except:
            # restores standard behavior for missing keys
            raise AttributeError('class ' + type(self).__name__ + ' has no attribute ' + str(name))


    def __setattr__(self, key, value):
        try:
            if not self._initialized:
                object.__setattr__(self, key, value)
            else:
                self.update({key: value})
        except (AttributeError, KeyError):
            object.__setattr__(self, key, value)

    def __repr__(self):

        output_string = '{:s} (class type: {:s})'.format(self.name, self.__class__.__name__)

        return output_string

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        if isinstance(value, unicode):
            value = str(value)
        assert isinstance(value, str), "{:s}".format(str(value))
        self._name = value

    @property
    def settings(self):
        return self._settings



    def to_dict(self):
        """

        Returns: itself as a dictionary

        """

        dictator = {self.name: {'class': self.__class__.__name__, 'settings': self.settings}}

        return dictator


    def save(self, filename):
        """
        save the instrument to path as a .b26 file

        Args:
            filename: path of file
        """

        instrument_class = self.__class__.__name__
        inst_dict = {self.name: {'class': instrument_class, 'settings': self.settings}}

        save_b26_file(filename, instruments = inst_dict)

    @staticmethod
    def load(input, instrument_instances = {}):
        """
        load instrument from input


        Args:
            input:  (1) a path to a file, that contains a valid dictionary with instrument settings
                    (2) a valid dictionary with instrument settings

        Returns:

        Args:
            instruments:
            instruments is a dictionary with
            (key,value) = (name of the instrument, instrument class name),
            for example instruments = {'Chamber Pressure Gauge': 'PressureGauge'}

            or

            (key,value) = (name of the instrument, {'instrument_class' : instrument class name, "settings", dict with settings}),


        Returns:
            a dictionary with (key,value) = (name of instrument, instance of instrument class) for all of the instruments
            passed to the function that were successfully imported and initialized. Otherwise, instruments are omitted
            in the outputted list.

        Examples:
            In the following, instrument_1 loads correctly, but instrument_2 does not, so only an instance of instrument_1
            is outputted.

        """


        if isinstance(input, str):
            # try to load file
            with open(input, 'r') as infile:
                instrument_dict = yaml.safe_load(infile)
        else:
            assert isinstance(input, dict)
            instrument_dict = input


        for instrument_name, instrument_class_name in instrument_dict.iteritems():
            if isinstance(instrument_class_name, dict):
                instrument_settings = instrument_class_name['settings']
                instrument_class_name = str(instrument_class_name['class'])
            else:
                instrument_settings = None

            if len(instrument_class_name.split('.')) == 1:
                module_path = 'src.instruments'
            else:
                module_path = 'src.instruments.' + '.'.join(instrument_class_name.split('.')[0:-1])
                instrument_class_name = instrument_class_name.split('.')[-1]

            # check if instrument already exists

            if instrument_name in instrument_instances.keys():
                print('WARNING: instrument {:s} already exists. Did not load!'.format(instrument_name))
            else:

                # ==== import module =======
                try:
                    # try to import the instrument
                    module = __import__(module_path, fromlist=[instrument_class_name])

                    # this returns the name of the module that was imported.
                    class_of_instrument = getattr(module, instrument_class_name)
                except AttributeError as e:
                    print(e.message)
                    # catches when we try to create an instrument of a class that doesn't exist!
                    raise AttributeError

                if instrument_settings is None:
                    # this creates an instance of the class with default settings
                    instrument_instance = class_of_instrument(name=instrument_name)
                else:
                    # this creates an instance of the class with custom settings
                    instrument_instance = class_of_instrument(name=instrument_name, settings=instrument_settings)

                # adds the instance to our output ditionary
                instrument_instances[instrument_name] = instrument_instance

        return instrument_instances



if __name__ == '__main__':

    # path to instrument classes
    # path_to_instrument = 'C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\src\\instruments'
    #
    # # path to a instrument file
    # intrument_filename = 'Z:\\Lab\\Cantilever\\Measurements\\160414_MW_transmission_vs_Power\\160414-18_59_33_test.inst'
    #

    filename = 'C:\\Users\\Experiment\\Desktop\\Jan\\test.inst'


    instruments = Instrument.load(filename)

    print(instruments)
    filename = 'C:\\Users\\Experiment\\Desktop\\Jan\\test2.inst'
    instruments = Instrument.load(filename, instruments)

    print(instruments)

