from src.core import Parameter, Script
from src.scripts import ScriptMinimalDummy
import src.scripts
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
        for script_name in self.scripts:
            self.scripts[script_name]._function()

    @staticmethod
    def script_sequence_factory(name, scripts):
        return type(name, (ScriptSequence, ), {'_SCRIPTS': scripts})

if __name__ == '__main__':
    smc = ScriptMinimalDummy()
    scripts = {'ScriptMinimalDummy': ScriptMinimalDummy}
    script_loop = ScriptSequence.script_sequence_factory('loop', scripts)
    setattr(src.scripts, 'loop', script_loop)
    # a = script_loop({'SMC': smc})
    # a._function()

    script, failed, instr = Script.load_and_append({'loop':
                                                        {'class': 'loop',
                                                         'settings': {},
                                                         'scripts': {'ScriptMinimalDummy': {'class': 'ScriptMinimalDummy', 'settings': {'parameter': 3}}}
                                                         }
                                                    }
                                                   )

    print(script)
    print(failed)
    print(instr)