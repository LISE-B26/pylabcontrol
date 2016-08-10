
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import time
from PyLabControl.src.instruments import Plant, PIControler
from PyLabControl.src.core import Parameter, Script


class PlantWithControler(Script):
    """
    script to bring the detector response to zero
    two channels are set to a fixed voltage while the signal of the third channel is varied until the detector response is zero
    """

    _DEFAULT_SETTINGS = [
        Parameter('sample rate', 0.5, float, 'sample rate in Hz')
    ]

    _INSTRUMENTS = {
        'plant': Plant,
        'controler': PIControler
    }

    _SCRIPTS = {

    }

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_function=None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_function=log_function, data_path = data_path)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        plant = self.instruments['plant']['instance']
        controler = self.instruments['controler']['instance']
        plant.update(self.instruments['plant']['settings'])
        controler.update(self.instruments['controler']['settings'])

        time_step = 1./self.settings['sample rate']

        controler.update({'time_step': time_step})

        self.data = {'plant_output':[], 'control_output':[]}
        while not self._abort:

            measurement = plant.output
            self.data['plant_output'].append(measurement)

            control_value = controler.controler_output(measurement)
            self.data['control_output'].append(control_value)


            self.progress = 50
            self.updateProgress.emit(90)

            time.sleep(time_step)




    def _plot(self, axes_list):

        if self.data['plant_output'] != []:
            axes1, axes2 = axes_list

            signal = self.data['plant_output']
            control_value = self.data['control_output']

            axes1.plot(signal, '-o')
            axes1.set_title('detector signal')
            axes2.plot(control_value, '-o')
            axes2.set_title('control value')
            axes1.hold(False)
            axes2.hold(False)
