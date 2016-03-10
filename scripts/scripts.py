import time
import numpy as np

from hardware_modules.instruments import Parameter, Instrument
# todo: inherit from threading
class Script(object):
    def __init__(self, name = None, threading = False):
        if name is None:
            name = self.__class__.__name__
        self.name = name
        self.threading = threading

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
        output_string += 'threading = {:s}'.format(str(self.threading))
        #
        # for parameter in self.parameter_list:
        #     # output_string += parameter_to_string(parameter)
        #     output_string += str(parameter)+'\n'
        #
        return output_string
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value
        else:
            raise TypeError('Name has to be a string')

    @property
    def settings_default(self):
        '''
        returns the default settings of the script
        settings contain Parameters, Instruments and Scripts
        :return:
        '''
        settings_default = []
        return settings_default

    @property
    def parameters(self):
        '''
        :return: returns the settings of the script
        settings contain Parameters, Instruments and Scripts
        '''
        return self._parameters


    def update_settings(self, settings_new):
        '''
        updates the settings if they exist
        :param settings_new:
        :return:
        '''

        def check_settings_list(settings):
            '''
            check if settings is a list of settings or a dictionary
            if it is a dictionary we create a settings list from it
            '''
            if isinstance(settings, dict):
                settings_new = []
                for key, value in settings.iteritems():
                    settings_new.append(Parameter(key, value))
            elif isinstance(settings, list):
                # if list element is not a  parameter, instrument or script cast it into a parameter
                settings_new = [element if isinstance(element, (Parameter, Instrument, Script)) else Parameter(element) for element in settings]
            else:
                raise TypeError('parameters should be a valid list or dictionary!')

            return settings_new

    @property
    def dict(self):
        '''
        returns the configuration of the script as a dictionary
        that contains {'parameters': parameters, 'instruments':instruments, 'scripts': scripts}
        :return: nested dictionary with entries name and value
        '''
        # build dictionary

        config = {}
        # todo: implement
        # for p in self._parameter_list:
        #     config.update(p.dict)

        return config

    @property
    def threading(self):
        '''
        boolean if True, script is executed on a thread if False it is not
        '''
        return self._threading
    @threading.setter
    def threading(self, value):
        assert isinstance(value, bool)
        self._threading = value

    @property
    def time_end(self):
        '''
        time when script execution started
        :return:
        '''
        return self._time_stop
    @time_end.setter
    def time_end(self, value):
        assert isinstance(value, time.struct_time)
        self._time_stop = value

    @property
    def time_start(self):
        '''
        time when script execution started
        :return:
        '''
        return self._time_start
    @time_start.setter
    def time_start(self, value):
        assert isinstance(value, time.struct_time)
        self._time_start = value

    def start(self, threading = []):
        '''
        executes the script
        :param threading: optional argument that decides if script is run on a thread, if not provided this is determined by threading property
        :return: boolean if execution of script finished succesfully
        '''
        self.is_running = True
        self.time_start  = time.localtime()
        while self.is_running and self.abort == False:
            # do something
            self.is_running = False

        self.time_end  = time.localtime()

        success = self.abort == False
        return success

    def stop(self):
        '''
        stops the script
        :return: boolean if termination of script finished succesfully
        '''
        success = True
        self.abort = True
        # todo: can we implement here to kill a thread?

        return success

class Script_Dummy(object):
    def __init__(self):

        self.signal = None
    def run(self):
        self.running  = True
        while self.running:
            time.sleep(0.1)
            self.signal = np.random.random()
    def stop(self):
        self.running  = False



if __name__ == '__main__':

    inst = fake_inst()
    inst.run()
    for i in range(10):
        print(inst.signal)
    inst.stop()

