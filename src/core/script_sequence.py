from src.core import Parameter, Script
import numpy as np

class ScriptSequence(Script):
    _number_of_classes = 0
    _class_list = []

    _DEFAULT_SETTINGS = []

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Default script initialization
        """

        #
        # if isinstance(scripts, list) and isinstance(scripts[0], Script):
        #
        #     self._SCRIPTS = {s.name: s.__class__ for s in scripts}
        #     scripts = {s.name: s for s in scripts}
        # else:
        #     script_class =
        #     self._SCRIPTS = {s.name: s.__class__ for s in scripts}
        #     print('xxxxx', self._SCRIPTS.__class__)

        Script.__init__(self, name, scripts = scripts, settings = settings, log_function= log_function, data_path = data_path)


    def _function(self):
        """
        """

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

    @classmethod
    def set_up_script(cls, name, factory_scripts, script_parameter_list, param_sweep_bool):
        if param_sweep_bool:
            sweep_params = ScriptSequence.populate_sweep_param(factory_scripts)
            factory_settings = [
                Parameter('script_order', script_parameter_list),
                Parameter('sweep_param', sweep_params[0], sweep_params, 'variable over which to sweep'),
                Parameter('min_value', 0, float, 'min parameter value'),
                Parameter('max_value', 0, float, 'max parameter value'),
                Parameter('N/value_step', 0, float,
                          'either number of steps or parameter value step, depending on mode'),
                Parameter('stepping_mode', 'N', ['N', 'value_step'],
                          'Switch between number of steps and step amount')
            ]
        else:
            factory_settings = [
                Parameter('script_order', script_parameter_list),
                Parameter('N', 0, int, 'times the subscripts will be executed')
            ]
        ss = ScriptSequence.script_sequence_factory(name, factory_scripts,
                                                    factory_settings)  # dynamically creates class
        ScriptSequence.import_dynamic_script(src.scripts, name, ss)  # imports created script in src.scripts.__init__

    @staticmethod
    def script_sequence_factory(name, scripts, settings):
        return type(name, (ScriptSequence, ), {'_SCRIPTS': scripts, '_DEFAULT_SETTINGS': settings})

    @staticmethod
    def import_dynamic_script(module, name, script_class):
        setattr(module, name, script_class)


    @staticmethod
    def populate_sweep_param(scripts):
        '''

        Args:
            scripts: a dict of classes inheriting from scripts

        Returns:

        '''


        def get_parameter_from_dict(trace, dic, parameter_list):
            """
            appends keys in the dict to a list in the form key.subkey.subsubkey
            Args:
                trace: initial prefix
                dic: dictionary
                parameter_list: list to which append the parameters

            Returns:

            """
            for key, value in dic.iteritems():
                if isinstance(value, dict):
                    parameter_list = get_parameter_from_dict(trace + '.' + key, value, parameter_list)
                else:
                    parameter_list.append(trace + '.' + key)
            return parameter_list

        parameter_list = []
        for script_name in scripts.keys():
            for setting in vars(scripts[script_name])['_DEFAULT_SETTINGS']:
                parameter_list = get_parameter_from_dict(script_name, setting, parameter_list)


        return parameter_list

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

    def plot(self, figure_list):
        self._current_subscript_stage['current_subscript'].plot(figure_list)

if __name__ == '__main__':
    from src.scripts import ScriptMinimalDummy

    import src.scripts
    smc = ScriptMinimalDummy()
    scripts = {'ScriptMinimalDummy': ScriptMinimalDummy}
    settings = [Parameter('repetitions', 0, int, 'times the subscript will be executed')]
    script_loop = ScriptSequence.script_sequence_factory('loop', scripts, settings)
    ScriptSequence.import_dynamic_script(src.scripts, 'loop', script_loop)
    # a = script_loop({'SMC': smc})
    # a._function()

    script, failed, instr = Script.load_and_append({'loop':
                                                        {'class': 'loop',
                                                         'settings': {'repetitions': 1},
                                                         'scripts': {'ScriptMinimalDummy': {'class': 'ScriptMinimalDummy', 'settings': {'parameter': 3}}}
                                                         }
                                                    }
                                                   )
    print(script['loop'].settings)
    print(script)
    print(failed)
    print(instr)