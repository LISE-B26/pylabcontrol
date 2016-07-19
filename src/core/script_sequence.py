from src.core import Parameter, Script
import src.scripts
import numpy as np
from PyQt4.QtCore import pyqtSlot

class ScriptIterator(Script):
    '''
This is a template class for scripts that iterate over a series of subscripts in either a loop /
a parameter sweep / future: list of points.
CAUTION: This class has some circular dependencies with Script that are avoided by only importing it in very local scope
in Script (since this inherits from Script, it can't be imported globally in Script). Use caution when making changes in
Script.
    '''

    _DEFAULT_SETTINGS = []
    # The default settings as dynamically created:
    # if param_sweep_bool:
    #     sweep_params = Script.populate_sweep_param(factory_scripts, [''])
    #     factory_settings = [
    #         Parameter('script_order', script_order),
    #         Parameter('sweep_param', sweep_params[0], sweep_params, 'variable over which to sweep'),
    #         Parameter('min_value', 0, float, 'min parameter value'),
    #         Parameter('max_value', 0, float, 'max parameter value'),
    #         Parameter('N/value_step', 0, float,
    #                   'either number of steps or parameter value step, depending on mode'),
    #         Parameter('stepping_mode', 'N', ['N', 'value_step'],
    #                   'Switch between number of steps and step amount')
    #     ]
    # else:
    #     factory_settings = [
    #         Parameter('script_order', script_order),
    #         Parameter('N', 0, int, 'times the subscripts will be executed')
    #     ]

    _INSTRUMENTS = {}
    _SCRIPTS = {}
    #_SCRIPTS is populated dynamically with the required subscripts

    _number_of_classes = 0 # keeps track of the number of dynamically created ScriptIterator classes that have been created
    _class_list = [] # list of current dynamically created ScriptIterator classes

    def __init__(self, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Default script initialization
        """

        Script.__init__(self, name, scripts = scripts, settings = settings, log_function= log_function, data_path = data_path)


    def _function(self):
        '''
        Runs either a loop or a parameter sweep over the subscripts in the order defined by the setting 'script_order'
        '''
        def get_sweep_parameters():
            #in both cases, param values have tolist to make sure that they are python types (ex float) rather than numpy
            #types (ex np.float64), the latter of which can cause typing issues
            if self.settings['stepping_mode'] == 'N':
                param_values = np.linspace(self.settings['min_value'], self.settings['max_value'], int(self.settings['N/value_step']), endpoint=True).tolist()
            elif self.settings['stepping_mode'] == 'value_step':
                param_values = np.linspace(self.settings['min_value'], self.settings['max_value'], (self.settings['max_value'] - self.settings['min_value'])/self.settings['N/value_step'] + 1, endpoint=True).tolist()
            return param_values

        script_names = self.settings['script_order'].keys()
        script_indices = [self.settings['script_order'][name] for name in script_names]
        _, sorted_script_names = zip(*sorted(zip(script_indices, script_names)))
        if 'sweep_param' in self.settings:
            param_values = get_sweep_parameters()
            for value in param_values:
                if self.settings['sweep_param'] == '':
                    self.log('Choose a sweep parameter!')
                    return
                split_trace = self.settings['sweep_param'].split('.')
                script = split_trace[0]
                setting = split_trace[1:]

                script_settings = self.scripts[script].settings
                curr_type = type(reduce(lambda x,y: x[y], setting, script_settings)) #traverse nested dict to get type of variable
                update_dict = reduce(lambda y, x: {x: y}, reversed(setting), curr_type(value)) #creates nested dictionary from list
                script_settings.update(update_dict)
                for script_name in sorted_script_names:
                    self.scripts[script_name].run()
        else:
            for i in range(0, self.settings['N']):
                for script_name in sorted_script_names:
                    self.scripts[script_name].run()

    # @classmethod
    # def set_up_script(cls, factory_scripts, script_parameter_list, param_sweep_bool):
    #     if param_sweep_bool:
    #         sweep_params = ScriptIterator.populate_sweep_param(factory_scripts)
    #         factory_settings = [
    #             Parameter('script_order', script_parameter_list),
    #             Parameter('sweep_param', sweep_params[0], sweep_params, 'variable over which to sweep'),
    #             Parameter('min_value', 0, float, 'min parameter value'),
    #             Parameter('max_value', 0, float, 'max parameter value'),
    #             Parameter('N/value_step', 0, float,
    #                       'either number of steps or parameter value step, depending on mode'),
    #             Parameter('stepping_mode', 'N', ['N', 'value_step'],
    #                       'Switch between number of steps and step amount')
    #         ]
    #     else:
    #         factory_settings = [
    #             Parameter('script_order', script_parameter_list),
    #             Parameter('N', 0, int, 'times the subscripts will be executed')
    #         ]
    #     class_name = 'class' + str(cls._number_of_classes)
    #     ss = ScriptIterator.script_sequence_factory(class_name, factory_scripts,
    #                                                 factory_settings)  # dynamically creates class
    #     print('SS', vars(ss))
    #     #prevent multiple importation of the same script with different names
    #     # for someclass in cls._class_list:
    #     #     if (vars(ss)['_SCRIPTS'] == vars(someclass)['_SCRIPTS']):
    #     #         print('CLASSNAME', vars(someclass)['_CLASS'])
    #     #         return vars(someclass)['_CLASS']
    #     ScriptIterator.import_dynamic_script(src.scripts, class_name, ss)  # imports created script in src.scripts.__init__
    #     cls._class_list.append(ss)
    #     cls._number_of_classes += 1
    #     return class_name
    #
    # @staticmethod
    # def script_sequence_factory(name, scripts, settings):
    #     return type(name, (ScriptIterator, ), {'_SCRIPTS': scripts, '_DEFAULT_SETTINGS': settings})
    #
    # @staticmethod
    # def import_dynamic_script(module, name, script_class):
    #     setattr(module, name, script_class)

        # subscript_settings = []
        # scripts_to_search = {}
        # # get first layer of scripts
        # for script_name in scripts.keys():
        #     scripts_to_search.update({script_name: {'trace': '', 'class': scripts[script_name]}})
        # # uncomment lines below to iterate over ALL subscripts
        # # while scripts_to_search:
        # for script_name in scripts_to_search.keys():
        #     trace = scripts_to_search[script_name]['trace'] + script_name + '.'
        #     for setting in vars(scripts_to_search[script_name]['class'])['_DEFAULT_SETTINGS']:
        #         subscript_settings.append(trace + setting.keys()[0])
        #     # subscripts = scripts_to_search[script_name]['object'].scripts
        #     del scripts_to_search[script_name]
        #     # for subscript_name in subscripts:
        #     #     scripts_to_search.update({subscript_name: {'trace': trace, 'object': subscripts[subscript_name]}})
        # return subscript_settings

    @pyqtSlot(int)
    def _receive_signal(self, progress):
        """
        this function takes care of signals emitted by the subscripts
        Args:
            progress: progress of subscript
        """

        self.progress = 100. * (float(self.index) + float(progress) / 100.) / self.settings['N']
        self.updateProgress.emit(int(self.progress))

    def plot(self, figure_list):
        '''
        When each subscript is called, uses its standard plotting

        Args:
            figure_list: list of figures passed from the guit

        '''
        #TODO: be smarter about how we plot ScriptIterator
        self._current_subscript_stage['current_subscript'].plot(figure_list)

if __name__ == '__main__':
    pass

    #TODO: update example code
    #OLD SAMPLE CODE WITH OUTDATED API
    # from src.scripts import ScriptMinimalDummy
    #
    # import src.scripts
    # smc = ScriptMinimalDummy()
    # scripts = {'ScriptMinimalDummy': ScriptMinimalDummy}
    # settings = [Parameter('repetitions', 0, int, 'times the subscript will be executed')]
    # script_loop = ScriptIterator.script_sequence_factory('loop', scripts, settings)
    # ScriptIterator.import_dynamic_script(src.scripts, 'loop', script_loop)
    # # a = script_loop({'SMC': smc})
    # # a._function()
    #
    # script, failed, instr = Script.load_and_append({'loop':
    #                                                     {'class': 'loop',
    #                                                      'settings': {'repetitions': 1},
    #                                                      'scripts': {'ScriptMinimalDummy': {'class': 'ScriptMinimalDummy', 'settings': {'parameter': 3}}}
    #                                                      }
    #                                                 }
    #                                                )
    # print(script['loop'].settings)
    # print(script)
    # print(failed)
    # print(instr)
