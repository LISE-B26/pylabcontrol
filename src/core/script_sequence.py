from src.core import Parameter, Script
from src.scripts import ScriptMinimalDummy
import src.scripts
import numpy as np
class ScriptSequence(Script):
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
        Performs a single attocube step with the voltage and frequency, and in the direction, specified in settings
        """
        if 'sweep_param' in self.settings:
            if self.settings['stepping_mode'] == 'N':
                param_values = range(self.settings['min_value'], self.settings['max_value'], self.settings['N/value_step'])
            elif self.settings['stepping_mode'] == 'value_step':
                param_values = np.linspace(self.settings['min_value'], self.settings['max_value'], self.settings['N/value_step']).tolist()
            for value in param_values:
                [script, setting] = self.settings['sweep_param'].split('.')
                self.scripts[script]['settings'].update({setting: value})
                for script_name in self.scripts:
                    self.scripts[script_name]._function()
        else:
            for i in range(0, self.settings['N']):
                for script_name in self.scripts:
                    self.scripts[script_name]._function()

    @staticmethod
    def script_sequence_factory(name, scripts, settings):
        return type(name, (ScriptSequence, ), {'_SCRIPTS': scripts, '_DEFAULT_SETTINGS': settings})

    @staticmethod
    def import_dynamic_script(namespace, name, script_class):
        setattr(namespace, name, script_class)

if __name__ == '__main__':
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