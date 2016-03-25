import datetime
import time
from abc import ABCMeta, abstractmethod, abstractproperty
from copy import deepcopy
from src.core import Parameter, Instrument
from PyQt4 import QtCore


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

    def __init__(self, name = None, settings = None):
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

    def __str__(self):
        pass
        #todo: finsish implementation
        # def parameter_to_string(parameter):
        #     # print('parameter', parameter)
        #     return_string = ''
        #     # if value is a list of parameters
        #     if isinstance(parameter.value, list) and isinstance(parameter.value[0],Parameter):
        #         return_string += '{:s}\n'.format(parameter.name)
        #         for element in parameter.value:
        #             return_string += parameter_to_string(element)
        #     elif isinstance(parameter, Parameter):
        #         return_string += '\t{:s}:\t {:s}\n'.format(parameter.name, str(parameter.value))
        #
        #     return return_string
        #
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


if __name__ == '__main__':
    pass


