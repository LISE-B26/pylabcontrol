"""
    This file is part of PyLabControl.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
from copy import deepcopy
from PyLabControl.src.core.read_write_functions import save_b26_file, get_config_value
import os, inspect
from importlib import import_module

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

    def __init__(self, name=None, settings=None):
        # make a deepcopy of the default settings
        # because _DEFAULT_SETTINGS is a class variable and thus shared among the instances
        self._settings = deepcopy(self._DEFAULT_SETTINGS)

        if name is None:
            name = self.__class__.__name__

        self.name = name

        self._is_connected = False  # internal flag that indicated if instrument is actually connected
        self._initialized = True

    # apply settings to instrument should be carried out in derived class

    def _DEFAULT_SETTINGS(self):
        """
        returns the default parameter_list of the instrument this function should be over written in any subclass
        """
        raise NotImplementedError

    def update(self, settings):
        '''
        updates the internal dictionary and sends changed values to instrument
        Args:
            settings: parameters to be set
        # mabe in the future:
        # Returns: boolean that is true if update successful

        '''
        self._settings.update(settings)

    def _PROBES(self):
        """

        Returns: a dictionary that contains the values that can be read from the instrument
        the key is the name of the value and the value of the dictionary is an info

        """
        raise NotImplementedError

    def read_probes(self, key = None):
        """
        function is overloaded:
            - read_probes()
            - read_probes(key)

        Args:
            key: name of requested value

        Returns:
            - if called without argument: returns the values of all probes in dictionary form
            - if called with argument: returns the value the requested key

        """

        if key is None:
            # return the value all probe in dictionary form
            d = {}
            for k in self._PROBES.keys():
                d[k] = self.read_probes(k)
            return d
        else:
            # return the value of the requested key if the key corresponds to a valid probe
            assert key in self._PROBES.keys()

            value = None

            return value

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
        """
        allows to read instrument inputs in the form value = instrument.input
        Args:
            name: name of input channel

        Returns: value of input channel
        """
        try:
            return self.read_probes(name)
        except:
            # restores standard behavior for missing keys
            raise AttributeError('class ' + type(self).__name__ + ' has no attribute ' + str(name))


    def __setattr__(self, key, value):
        """
        this allows to address instrument outputs of the form instrument.output = value
        """
        try:
            if not self._initialized:
                # fall back to regular behaviour of the parent class
                object.__setattr__(self, key, value)
            else:
                # call internal update function that updates the instrument and keeps track of the settings
                self.update({key: value})
        except (AttributeError, KeyError):
            object.__setattr__(self, key, value)

    def __repr__(self):
        """

        Returns: the instrument as a string  for display

        """

        output_string = '{:s} (class type: {:s})'.format(self.name, self.__class__.__name__)

        return output_string

    @property
    def name(self):
        """

        Returns: instrument name

        """
        return self._name
    @name.setter
    def name(self, value):
        """
        check if value is a string and if so set name = value
        """
        if isinstance(value, unicode):
            value = str(value)
        assert isinstance(value, str), "{:s}".format(str(value))
        self._name = value

    @property
    def settings(self):
        """

        Returns: instrument settings

        """
        return self._settings



    def to_dict(self):
        """

        Returns: the instrument itself as a dictionary

        """

        dictator = {self.name: {'class': self.__class__.__name__, 'settings': self.settings}}

        return dictator


    def save_b26(self, filename):
        """
        saves the instrument to path as a .b26 file

        Args:
            filename: path of file
        """
        save_b26_file(filename, instruments = self.to_dict())

    @staticmethod
    def load_and_append(instrument_dict, instruments = None):
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
        if instruments is None:
            instruments = {}

        updated_instruments = {}
        updated_instruments.update(instruments)
        loaded_failed = []

        # import all the instruments from additional modules that contain instruments. This name of those modules is in the config file that is located
        # in the main directory
        path_to_config = '/'.join(os.path.normpath(os.path.dirname(inspect.getfile(Instrument))).split('\\')[0:-2]) + '/config.txt'
        module_list = get_config_value('SCRIPT_MODULES', path_to_config).split(';')
        module_list = [import_module(module_name+'.src.instruments') for module_name in module_list]


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
                raise TypeError('instrument_class_name not recognized for {0}'.format(instrument_name))


            if len(instrument_class_name.split('.')) == 1:
                module_path = 'src.instruments'
            else:
                module_path = 'src.instruments.' + '.'.join(instrument_class_name.split('.')[0:-1])
                instrument_class_name = instrument_class_name.split('.')[-1]

            # check if the requested instruments is in one of the modules
            for mod in module_list:
                if hasattr(mod, instrument_class_name):
                    module = mod
                    break

            if module is None:
                module = import_module('PyLabControl.src.instruments')
                assert hasattr(module, instrument_class_name)  # check if instrument is really in the main src.instrument module

            # check if instrument already exists
            if instrument_name in instruments.keys():
                print('WARNING: instrument {:s} already exists. Did not load!'.format(instrument_name))
                loaded_failed.append(instrument_name)
            else:
                instrument_instance = None

                # ==== import module =======
                try:
                    # # try to import the instrument
                    # module = __import__(module_path, fromlist=[instrument_class_name])
                    # this returns the name of the module that was imported.
                    class_of_instrument = getattr(module, instrument_class_name)
                    if instrument_settings is None:
                        # this creates an instance of the class with default settings
                        instrument_instance = class_of_instrument(name=instrument_name)
                    else:
                        # this creates an instance of the class with custom settings
                        instrument_instance = class_of_instrument(name=instrument_name, settings=instrument_settings)

                except AttributeError as e:
                    print('XX error in instruments', e.message)
                except Exception as e2:
                    # raise e2
                    pass
                    # catches when we try to create an instrument of a class that doesn't exist!
                    # raise AttributeError

                if instrument_instance is None:
                    loaded_failed.append(instrument_name)
                else:
                    # adds the instance to our dictionary
                    updated_instruments[instrument_name] = instrument_instance

        return updated_instruments, loaded_failed


if __name__ == '__main__':


    instr, fail = Instrument.load_and_append({'MaestroLightControl': {'class': 'MaestroLightControl', 'settings': {'port': 'COM5', 'block green': {'settle_time': 0.2, 'position_open': 7600, 'position_closed': 3800, 'open': True, 'channel': 0}}}})
    print(instr)
    print(fail)