
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

        save_b26_file(filename, instruments = self.to_dict())

    @staticmethod
    def load_and_append(instrument_dict, instruments = {}):
        """
        load instrument from instrument_dict and append to instruments

        Args:
            instrument_dict: dictionary of form

                instrument_dict = {
                name_of_instrument_1 :
                    {"settings" : settings_dictionary, "class" : name_of_class}
                name_of_instrument_2 :
                    {"settings" : settings_dictionary, "class" : name_of_class}
                ...
                }

            or

                instrument_dict = {
                name_of_instrument_1 : name_of_class,
                name_of_instrument_2 : name_of_class
                ...
                }

            where name_of_class is either a class or the name of a class

            instruments: dictionary of form

                instruments = {
                name_of_instrument_1 : instance_of_instrument_1,
                name_of_instrument_2 : instance_of_instrument_2,
                ...
                }



        Returns:
                dictionary updated_instruments that contains the old and the new instruments

                and list loaded_failed = [name_of_instrument_1, name_of_instrument_2, ....] that contains the instruments that were requested but could not be loaded

        """
        updated_instruments = {}
        updated_instruments.update(instruments)
        loaded_failed = []

        for instrument_name, instrument_class_name in instrument_dict.iteritems():
            instrument_settings = None
            if isinstance(instrument_class_name, dict):
                instrument_settings = instrument_class_name['settings']
                instrument_class_name = str(instrument_class_name['class'])
            elif isinstance(instrument_class_name, Instrument):
                instrument_class_name = instrument_class_name.__class__
            elif isinstance(instrument_class_name, str):
                pass
            else:
                raise TypeError('instrument_class_name not recognized')

            if len(instrument_class_name.split('.')) == 1:
                module_path = 'src.instruments'
            else:
                module_path = 'src.instruments.' + '.'.join(instrument_class_name.split('.')[0:-1])
                instrument_class_name = instrument_class_name.split('.')[-1]

            # check if instrument already exists
            if instrument_name in instruments.keys():
                print('WARNING: instrument {:s} already exists. Did not load!'.format(instrument_name))
                loaded_failed.append(instrument_name)
            else:
                instrument_instance = None
                # ==== import module =======
                try:
                    # try to import the instrument
                    module = __import__(module_path, fromlist=[instrument_class_name])
                    # this returns the name of the module that was imported.
                    class_of_instrument = getattr(module, instrument_class_name)

                    if instrument_settings is None:
                        # print('FF -- mss')
                        # this creates an instance of the class with default settings
                        instrument_instance = class_of_instrument(name=instrument_name)
                    else:
                        # print('FF -- m', class_of_instrument, instrument_name, instrument_settings)
                        # this creates an instance of the class with custom settings
                        instrument_instance = class_of_instrument(name=instrument_name, settings=instrument_settings)

                except AttributeError as e:
                    print(e.message)
                    print('module', module)
                    print('class_of_instrument', class_of_instrument)
                    print('instrument_class_name', instrument_class_name)
                    print('instrument_name', instrument_name)
                    print('instrument_settings', instrument_settings)

                    # catches when we try to create an instrument of a class that doesn't exist!
                    raise AttributeError

                if instrument_instance is None:
                    loaded_failed.append(instrument_name)
                else:
                    # adds the instance to our dictionary
                    updated_instruments[instrument_name] = instrument_instance

        return updated_instruments, loaded_failed



if __name__ == '__main__':

    # path to instrument classes
    # path_to_instrument = 'C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\src\\instruments'
    #
    # # path to a instrument file
    # intrument_filename = 'Z:\\Lab\\Cantilever\\Measurements\\160414_MW_transmission_vs_Power\\160414-18_59_33_test.inst'
    #

# from src.core.read_write_functions import load_b26_file
# filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\XX.b26"
# data = load_b26_file(filename)
# inst = {}
# instruments, instruments_failed = Instrument.load_and_append(data['instruments'], instruments = inst)
# print('loaded', instruments)
# print('inst', inst)
# print('failed', instruments_failed)
# print('load again')
# instruments_failed = Instrument.load_and_append(data['instruments'], instruments)
# print('loaded', instruments)
# print('failed', instruments_failed)
#



    from src.core import Instrument



    instr, fail = Instrument.load_and_append({'MaestroLightControl': {'class': 'MaestroLightControl', 'settings': {'port': 'COM5', 'block green': {'settle_time': 0.2, 'position_open': 7600, 'position_closed': 3800, 'open': True, 'channel': 0}}}})
    print(instr)
    print(fail)