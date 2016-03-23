import datetime

from PyQt4 import QtCore

from src.core import Parameter, Instrument


class Script_new(object):


    # ========================================================================================
    # ======= Following functions have to be customized for each instrument subclass =========
    # ========================================================================================

    def __init__(self, script_function, name = None, settings = None):
        """
        executes scripts_old and stores script parameters and settings
        Args:
            script_function (required): script that
            name (optinal):  name of script, if not provided take name of function
            settings (optinal): a Parameter object that contains all the information needed in the script
        """

        assert hasattr(script_function, '__call__')
        self._function = script_function

        if name is None:
            name = script_function.__class__.__name__
        assert isinstance(name, str)
        self.name = name

        # set end time to be before start time if script hasn't been excecuted this tells us
        self.start_time = datetime.datetime.now()
        self.end_time = self.start_time - datetime.timedelta(seconds=1)

        self._settings = settings
        self._abort = False


    @property
    def _settings_default(self):
        '''
        returns the default settings of the script
        settings contain Parameters, Instruments and Scripts
        :return:
        '''
        settings_default = Parameter([
            Parameter('parameter', 1),
            Parameter('file_path', './some/path'),
            Parameter('instrument', Instrument())
        ])
        return settings_default

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time
        print('I am a test function counting to 3...')
        for i in range(3):
            time.sleep(0.1)
            print(i)


    # ========================================================================================
    # ======= Following functions are generic ================================================
    # ========================================================================================

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

    def update(self, settings_new):
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
                raise TypeError('settings should be a valid list or dictionary!')
            return settings_new

        for setting in check_settings_list(settings_new):
            # get index of setting in default list
            index = [i for i, s in enumerate(self.settings_default) if s == setting]
            if len(index)>1:
                raise TypeError('Error: Dublicate setting in default list')
            elif len(index)==1:
                self.settings[index[0]].update(setting)

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

class Script(object):
    def __init__(self, name = None, settings = []):
        '''
        generic script class
        :param name: name of script
        :param threading: if script is excecuted on thread, default is False
        '''
        if name is None:
            name = self.__class__.__name__
        self.name = name
        # set end time to be before start time if script hasn't been excecuted this tells us
        self.time_start = datetime.datetime.now()
        self.time_end =self.time_start - datetime.timedelta(seconds=1)

        self._settings = self.settings_default
        self.update_settings(settings)
        self._abort = False

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
        for element in self.settings:
            output_string += str(element)+'\n'
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
    def settings(self):
        '''
        :return: returns the settings of the script
        settings contain Parameters, Instruments and Scripts
        '''
        return self._settings

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
                raise TypeError('settings should be a valid list or dictionary!')
            return settings_new

        for setting in check_settings_list(settings_new):
            # get index of setting in default list
            index = [i for i, s in enumerate(self.settings_default) if s == setting]
            if len(index)>1:
                raise TypeError('Error: Dublicate setting in default list')
            elif len(index)==1:
                self.settings[index[0]].update(setting)

    @property
    def dict(self):
        '''
        returns the configuration of the script as a dictionary
        that contains {'parameters': parameters, 'instrument_tests':instrument_tests, 'scripts_old': scripts_old}
        :return: nested dictionary with entries name and value
        '''
        # build dictionary

        config = {}
        # todo: implement
        # for p in self._parameter_list:
        #     config.update(p.dict)

        return config

    @property
    def time_end(self):
        '''
        time when script execution started
        :return:
        '''
        return self._time_stop
    @time_end.setter
    def time_end(self, value):
        assert isinstance(value, datetime.datetime)
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
        assert isinstance(value, datetime.datetime)
        self._time_start = value

    @property
    def excecution_time(self):
        '''
        :return: script excecition time as time_delta object to get time in seconds use .total_seconds()
        '''
        return self.time_end - self.time_start

    def run(self):
        '''
        executes the script
        :return: boolean if execution of script finished succesfully
        '''
        self.is_running = True
        self.time_start  = datetime.datetime.now()
        while self.is_running and self._abort == False:
            # do something
            self.is_running = False

        self.time_end  = datetime.datetime.now()

        success = self._abort == False
        return success


        return success

    def stop(self):
        self._abort == True

class QtScript(QtCore.QThread, Script):
    '''
    This class starts a script on its own thread
    '''
    updateProgress = QtCore.pyqtSignal(int)
    #You can do any extra things in this init you need
    def __init__(self, name = None, settings = []):
        """

        :param
        :return:
        """
        self._recording = False

        QtCore.QThread.__init__(self)
        Script.__init__(self, name, settings)

    def __del__(self):
        self.stop()

    #A QThread is run by calling it's start() function, which calls this run()
    #function in it's own "thread".
    def run(self):
        import time

        self.is_running = True
        self.time_start  = datetime.datetime.now()

        for i in range(100):
        # while self.is_running and self._abort == False:
            # do something
            self.updateProgress.emit(i+1)
            # self.updateProgress.emit(random.random())
            time.sleep(0.05)

        self.time_end  = datetime.datetime.now()

        success = self._abort == False
        return success

    def stop(self):
        self._abort = False


# class QtScript_Dummy(QtScript):
#     #This is the signal that will be emitted during the processing.
#     #By including int as an argument, it lets the signal know to expect
#     #an integer argument when emitting.
#     updateProgress = QtCore.Signal(int)
#
#     def __init__(self, name, threading, settings):
#         super(QtScript_Dummy, self).__init__(name, settings)
#
#     @property
#     def settings_default(self):
#         '''
#         returns the default settings of the script
#         settings contain Parameters, Instruments and Scripts
#         :return:
#         '''
#         settings_default = [
#             Parameter('a', 0, [0,1]),
#             Parameter({'b':0.1}),
#             Parameter({'threading':True}),
#             Instrument_Dummy('dummy inst')
#         ]
#         return settings_default
#     @property
#     def a(self):
#         return [element for element in self.settings if element.name == 'a'][0]
#
#     #A QThread is run by calling it's start() function, which calls this run()
#     #function in it's own "thread".
#     def run(self):
#         import time
#         import random
#
#         self.is_running = True
#         self.time_start  = datetime.datetime.now()
#         while self.is_running and self._abort == False:
#             signal = random.random()
#             # do something
#             self.updateProgress.emit()
#             print('a', signal)
#             time.sleep(0.2)
#
#         self.time_end  = datetime.datetime.now()
#
#         success = self._abort == False
#         return success

class QtScript_Dummy(QtScript):
    def __init__(self, name, settings = []):
        super(QtScript_Dummy, self).__init__(name, settings)
    @property
    def settings_default(self):
        '''
        returns the default settings of the script
        settings contain Parameters, Instruments and Scripts
        :return:
        '''
        settings_default = [
            Parameter('a', 0, [0,1]),
            Parameter('txt', 'a', ['a','b']),
            Parameter('param', [Parameter('a', 0, [0,1]), Parameter('b', 2, [2,3])]),
            Parameter({'b':0.1}),
            Parameter({'b':True}),
            Instrument_Dummy('dummy inst'),
            Sub_Script_Dummy('sub_script')
        ]
        return settings_default
    def run(self):
        '''
        executes the script
        :return: boolean if execution of script finished succesfully
        '''
        import time
        self.is_running = True
        self.time_start  = datetime.datetime.now()
        print('this is script {:s}'.format(self.name))
        print('counting')
        for i in range(10):
            time.sleep(0.1)
            print(i)
        self.time_end  = datetime.datetime.now()

        print('run subscript')
        for element in self.settings:
            if isinstance(element, Script) and element.name == 'sub_script':
                element.run()


        success = self._abort == False
        print('total execution time: {:s}'.format(str(self.excecution_time)))
        self.is_running = False

        return success

class Script_Dummy(Script):
    def __init__(self, name, settings = []):
        super(Script_Dummy, self).__init__(name, settings)
    @property
    def settings_default(self):
        '''
        returns the default settings of the script
        settings contain Parameters, Instruments and Scripts
        :return:
        '''
        settings_default = [
            Parameter('a', 0, [0,1]),
            Parameter('txt', 'a', ['a','b']),
            Parameter('param', [Parameter('a', 0, [0,1]), Parameter('b', 2, [2,3])]),
            Parameter({'b':0.1}),
            Parameter({'b':True}),
            # Instrument_Dummy('dummy inst'),
            Sub_Script_Dummy('sub_script')
        ]
        return settings_default
    def run(self):
        '''
        executes the script
        :return: boolean if execution of script finished succesfully
        '''
        import time
        self.is_running = True
        self.time_start  = datetime.datetime.now()
        print('this is script {:s}'.format(self.name))
        print('counting')
        for i in range(10):
            time.sleep(0.1)
            print(i)
        self.time_end  = datetime.datetime.now()

        print('run subscript')
        for element in self.settings:
            if isinstance(element, Script) and element.name == 'sub_script':
                element.run()


        success = self._abort == False
        print('total execution time: {:s}'.format(str(self.excecution_time)))
        self.is_running = False

        return success

class Sub_Script_Dummy(Script):
    def __init__(self, name, settings = []):
        super(Sub_Script_Dummy, self).__init__(name, settings)
    @property
    def settings_default(self):
        '''
        returns the default settings of the script
        settings contain Parameters, Instruments and Scripts
        :return:
        '''
        settings_default = [
            Parameter('a', 0, [0,1]),
            Parameter('txt', 'a', ['a','b']),
            Parameter('param', [Parameter('a', 0, [0,1]), Parameter('b', 2, [2,3])]),
            Parameter({'b':0.1}),
            Parameter({'b':True}),
            Instrument_Dummy('dummy inst')
        ]
        return settings_default
    def run(self):
        '''
        executes the script
        :return: boolean if execution of script finished succesfully
        '''
        self.is_running = True
        self.time_start  = datetime.datetime.now()
        print('this is script {:s}'.format(self.name))
        print('my settings are:')
        for setting in self.settings:
            print(setting)

        self.time_end  = datetime.datetime.now()

        success = self._abort == False
        print('total execution time: {:s}'.format(self.excecution_time))
        self.is_running = False

        return success

def testing():
    script = Script_Dummy('test script', False, {'a': 0, 'b':1.2})

    print(script)
    print(script.settings)


if __name__ == '__main__':

    pass


