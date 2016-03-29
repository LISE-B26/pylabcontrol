import datetime
import time
from abc import ABCMeta, abstractmethod, abstractproperty
from copy import deepcopy
from src.core import Parameter, Instrument
from PyQt4 import QtCore
from collections import deque
import os
import pandas as pd
import json as json


class Script(object):
    # __metaclass__ = ABCMeta

    # ========================================================================================
    # ======= Following old_functions have to be customized for each instrument subclass =========
    # ========================================================================================

    # '''
    # returns the default settings of the script
    # settings contain Parameters, Instruments and Scripts
    # :return:
    # '''
    # _DEFAULT_SETTINGS = Parameter([
    #     Parameter('parameter', 1),
    #     Parameter('file_path', './some/path')
    # ])
    #

    # ========================================================================================
    # ======= Following old_functions are generic ================================================
    # ========================================================================================

    def __init__(self, name = None, settings = None, instruments = None, scripts = None):
        """
        executes scripts and stores script parameters and settings
        Args:
            name (optinal):  name of script, if not provided take name of function
            settings (optinal): a Parameter object that contains all the information needed in the script
        """

        if name is None:
            name = self.__class__.__name__
        assert isinstance(name, str)
        self.name = name

        self._instruments = {}
        if instruments is None:
            instruments = {}
        else:
            assert isinstance(instruments, dict)
            assert instruments.keys() == self._INSTRUMENTS.keys()
        self.instruments = instruments

        self._scripts = {}
        if scripts is None:
            scripts = {}
        self.scripts = scripts

        # set end time to be before start time if script hasn't been excecuted this tells us
        self.start_time = datetime.datetime.now()
        self.end_time = self.start_time - datetime.timedelta(seconds=1)

        self._settings = deepcopy(self._DEFAULT_SETTINGS)

        if settings is not None:
            self.update(settings)
        self._abort = False


    # @abstractmethod
    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        # some generic function
        raise NotImplementedError

    @property
    def _DEFAULT_SETTINGS(self):
        """
        returns the default parameter_list of the script this function should be over written in any subclass
        """
        raise NotImplementedError("Subclass did not implement _DEFAULT_SETTINGS")
    @property
    def _INSTRUMENTS(self):
        """

        Returns: a dictionary of the instruments, were key is the instrument name and value is the instrument class
        if there is not instrument it should return an empty dict

        """
        raise NotImplementedError("Subclass did not implement _INSTRUMENTS")
    @property
    def _SCRIPTS(self):
        """

        Returns: a dictionary of the instruments, were key is the instrument name and value is the instrument class
        if there is not instrument it should return an empty dict

        """
        raise NotImplementedError("Subclass did not implement _SCRIPTS")

    def __str__(self):

        output_string = '{:s} (class type: {:s})\n'.format(self.name, self.__class__.__name__)

        output_string += 'settings:\n'
        for key, value in self.settings.iteritems():
            output_string += "{:s} : {:s}\n".format(key, str(value))
        return output_string
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        assert isinstance(value, str)
        self._name = value

    @property
    def instrumets(self):
        return self._instruments
    @instrumets.setter
    def instruments(self, instrument_dict):
        assert isinstance(instrument_dict, dict)
        assert instrument_dict.keys() == self._INSTRUMENTS.keys(), "keys in{:s}\nkeys expected{:s}".format(str(instrument_dict.keys()), str( self._INSTRUMENTS.keys()))

        for key, value in self._INSTRUMENTS.iteritems():
            assert isinstance(instrument_dict[key], self._INSTRUMENTS[key])
            self._instruments.update({key: instrument_dict[key]})

    @property
    def scripts(self):
        return self._scripts
    @scripts.setter
    def scripts(self, script_dict):
        assert isinstance(script_dict, dict)
        assert script_dict.keys() == self._SCRIPTS.keys(), "keys in{:s}\nkeys expected{:s}".format(str(script_dict.keys()), str( self._SCRIPTS.keys()))

        for key, value in self._SCRIPTS.iteritems():
            assert isinstance(script_dict[key], self._SCRIPTS[key])
            self._scripts.update({key: script_dict[key]})

    @property
    def settings(self):
        '''
        :return: returns the settings of the script
        settings contain Parameters, Instruments and Scripts
        '''
        return self._settings

    def update(self, settings):
        '''
        updates the internal dictionary and sends changed values to instrument
        Args:
            settings: parameters to be set
        # mabe in the future:
        # Returns: boolean that is true if update successful

        '''
        self._settings.update(settings)

    @property
    def end_time(self):
        '''
        time when script execution started
        :return:
        '''
        return self._time_stop
    @end_time.setter
    def end_time(self, value):
        assert isinstance(value, datetime.datetime)
        self._time_stop = value

    @property
    def start_time(self):
        '''
        time when script execution started
        :return:
        '''
        return self._time_start
    @start_time.setter
    def start_time(self, value):
        assert isinstance(value, datetime.datetime)
        self._time_start = value

    @property
    def excecution_time(self):
        '''
        :return: script excecition time as time_delta object to get time in seconds use .total_seconds()
        '''
        return self.end_time - self.start_time

    def run(self):
        '''
        executes the script
        :return: boolean if execution of script finished succesfully
        '''
        self.is_running = True
        self.start_time  = datetime.datetime.now()
        print('starting script at {:s} on {:s}'.format(self.start_time.strftime('%H:%M:%S'),self.start_time.strftime('%d/%m/%y')))
        self._function()

        self.end_time  = datetime.datetime.now()
        print('script finished at {:s} on {:s}'.format(self.end_time.strftime('%H:%M:%S'),self.end_time.strftime('%d/%m/%y')))
        success = self._abort == False
        return success


        return success

    def stop(self):
        self._abort == True



    def save(self):
        """
        saves self.data
        requires that the script has
         - a self.data dictionary that holds the data
         - a 'path' parameter
         - a 'tag' parameter
        """

        path = self.settings['path']
        tag = self.settings['tag']

        # if deque object, take the last dataset, which is the most recent
        if isinstance(self.data, deque):
            data = self.data[-1]
        elif isinstance(self.data, dict):
            data = self.data
        else:
            raise TypeError("unknown datatype!")

        if os.path.exists(path) == False:
            os.makedirs(path)

        # ======= save self.data ==============================
        if len(set([len(v) for k, v in data.iteritems()]))==1:
            # if all entries of the dictionary are the same length we can write the data into a single file
            file_path = "{:s}\\{:s}_{:s}.{:s}".format(
                path,
                self.end_time.strftime('%y%m%d-%H_%M_%S'),
                tag,
                'dat'
            )

            df = pd.DataFrame(data)
            df.to_csv(file_path)

        else:
            # otherwise, we write each entry into a separate file into a subfolder data

            path = "{:s}\\data\\".format(path)
            if os.path.exists(path) == False:
                os.makedirs(path)
            for key, value in self.data.iteritems():


                file_path = "{:s}\\{:s}_{:s}.{:s}".format(
                    path,
                    self.end_time.strftime('%y%m%d-%H_%M_%S'),
                    tag,
                    key
                )

                df = pd.DataFrame(value)
                df.to_csv(file_path)

        # ======= save self.settings ==============================
        file_path = "{:s}\\{:s}_{:s}.{:s}".format(
                        path,
                        self.end_time.strftime('%y%m%d-%H_%M_%S'),
                        tag,
                        'set'
                    )
        with open(file_path, 'w') as outfile:
            tmp = json.dump(self.settings, outfile, indent=4)


        # ======= save self.instruments ==============================

        if self.instruments is not {}:

            file_path = "{:s}\\{:s}_{:s}.{:s}".format(
                            path,
                            self.end_time.strftime('%y%m%d-%H_%M_%S'),
                            tag,
                            'inst'
                        )
            inst_dict = {k : v.settings for k, v in self.instruments.iteritems()}
            with open(file_path, 'w') as outfile:
                tmp = json.dump(inst_dict, outfile, indent=4)

if __name__ == '__main__':
    pass


