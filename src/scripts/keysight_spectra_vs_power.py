from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.instruments import SpectrumAnalyzer, CryoStation
from src.scripts import KeysightGetSpectrum
import numpy as np
import time


class KeysightSpectrumVsPower(Script, QThread):

    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/----data_tmp_default----', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('power_out_min',-45.0, float, 'output power (dBm) min'),
        Parameter('power_out_step',5.0, float, 'output power (dBm) step'),
        Parameter('power_out_max',-15.0, float, 'output power (dBm) max'),
        Parameter('wait_time',2.0, float, 'wait time in seconds')
    ])

    _INSTRUMENTS = {
        'cryo_station' : CryoStation
    }

    _SCRIPTS = {
        'get_spectrum' : KeysightGetSpectrum
    }
    updateProgress = Signal(int)
    def __init__(self, instruments, scripts, name = None, settings = None,  log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings,scripts =scripts, instruments = instruments, log_output = log_output)
        QThread.__init__(self)
    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        def calc_progress(power):
            min, max =self.settings['power_out_min'], self.settings['power_out_max']

            progress = ( power-min ) / ( max-min ) * 100.0

            return progress

        power_values = [float(power) for power in np.arange(self.settings['power_out_min'], self.settings['power_out_max'], self.settings['power_out_step'])]

        stage_1_temp = []
        stage_2_temp = []
        platform_temp = []
        times = []
        spectrum = []
        uwave_power = []

        spectrum_analyzer = self.scripts['get_spectrum'].instruments['spectrum_analyzer']

        self.save(save_data=False, save_instrumets=True, save_log=False, save_settings=True)

        for power in power_values:

            spectrum_analyzer.output_power = power
            time.sleep(self.settings['wait_time'])  #since the spectrum analyzer takes a full second =)

            uwave_power.append(power)
            times.append(time.strftime('%Y_%m_%d_%H_%M_%S'))
            stage_1_temp.append(self.instruments['cryo_station'].platform_temp)
            stage_2_temp.append(self.instruments['cryo_station'].stage_1_temp)
            platform_temp.append(self.instruments['cryo_station'].stage_2_temp)

            self.scripts['get_spectrum'].run()

            freq = self.scripts['get_spectrum'].data['frequency']
            transmission = self.scripts['get_spectrum'].data['spectrum']

            spectrum.append(transmission)

            data = {
                'stage_1_temp' : stage_1_temp,
                'stage_2_temp' : stage_2_temp,
                'platform_temp' : platform_temp,
                'times' : times,
                'spectrum' : spectrum,
                'frequency' : freq,
                'uwave_power' : uwave_power
            }

            self.data = data

            self.save(save_data=True, save_instrumets=False, save_log=False, save_settings=False)

            progress = calc_progress(power)
            self.updateProgress.emit(progress)
            self.log('current u-wave power : {:0.2f} dBm'.format(power))

        self.save(save_data=False, save_instrumets=False, save_log=True, save_settings=False)

        spectrum_analyzer.output_power = -60.0



    def plot(self, axes):

        self.scripts['get_spectrum'].plot(axes)
