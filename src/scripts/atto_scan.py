from src.core import Parameter, Script
from src.instruments import Attocube

class AttoStep(Script):
    _DEFAULT_SETTINGS = Parameter([
        Parameter('axis', 'x', ['x', 'y', 'z'], 'Axis to step on'),
        Parameter('direction', 'Up', ['Up', 'Down'], 'step direction, up or down in voltage (or on physical switch)')
    ])

    _INSTRUMENTS = {'attocube': Attocube}
    _SCRIPTS = {}

    def __init__(self, instruments = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, log_function= log_function, data_path = data_path)

    def _function(self):
        """
        Updates the voltage and frequency on the attocube, and then does a single step in the specified direction
        """
        attocube = self.instruments['attocube']['instance']
        attocube_voltage = self.instruments['attocube']['settings'][self.settings['axis']]['voltage']
        attocube.update({self.settings['axis']: {'voltage': attocube_voltage}})
        attocube_freq = self.instruments['attocube']['settings'][self.settings['axis']]['freq']
        attocube.update({self.settings['axis']: {'freq': attocube_freq}})
        if self.settings['direction'] == 'Up':
            dir = 0
        elif self.settings['direction'] == 'Down':
            dir = 1
        self.instruments['attocube']['instance'].step(self.settings['axis'], dir)

if __name__ == '__main__':
    script, failed, instr = Script.load_and_append({'AttoStep': 'AttoStep'})

    print(script)
    print(failed)
    print(instr)

