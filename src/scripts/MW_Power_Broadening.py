import numpy as np
from matplotlib import patches

from src.core import Script, Parameter
from src.scripts import ESR_Selected_NVs
import os


class MWPowerBroadening(Script):
    _DEFAULT_SETTINGS = [
        Parameter('min_mw_power', -20.0, float, 'output power (dBm)'),
        Parameter('max_mw_power', -11.0, float, 'output power (dBm)'),
        Parameter('mw_power_step', 1.0, float, 'output power (dBm)')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {'ESR_Selected_NVs': ESR_Selected_NVs}

    def __init__(self, instruments=None, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        Script.__init__(self, name, settings=settings, instruments=instruments, scripts=scripts,
                        log_function=log_function, data_path=data_path)

        self.index = 0

        self.scripts['ESR_Selected_NVs'].log_function = self.log_function

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        mw_power_values = np.arange(self.settings['min_mw_power'],
                                    self.settings['max_mw_power'] + self.settings['mw_power_step'],
                                    self.settings['mw_power_step'])
        print('Powers', mw_power_values)

        for power in mw_power_values:
            self.scripts['ESR_Selected_NVs'].scripts['StanfordResearch_ESR'].settings['power_out'] = float(power)
            self.scripts['ESR_Selected_NVs'].scripts['StanfordResearch_ESR'].settings['tag'] = str(power) + 'dBm'
            self.scripts['ESR_Selected_NVs'].run()

    def stop(self):
        self._abort = True
        self.scripts['ESR_Selected_NVs'].stop()

    def plot(self, figure_list):
        self.scripts['ESR_Selected_NVs'].plot(figure_list)


if __name__ == '__main__':
    script, failed, instruments = Script.load_and_append(script_dict={'MWPowerBroadening': 'MWPowerBroadening'})

    print(script)
    print(failed)
    print(instruments)
