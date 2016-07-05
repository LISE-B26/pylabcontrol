from src.core import Script, Parameter
from src.instruments import SpectrumAnalyzer, CryoStation
from src.scripts import KeysightGetSpectrum
import numpy as np
import time


class KeysightSpectrumVsPower(Script):

    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', '', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', False, bool, 'save data on/off'),
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
    def __init__(self, instruments, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, scripts =scripts, instruments = instruments, log_function= log_function, data_path = data_path)
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

        initial_power = spectrum_analyzer.settings['output_power']
        print('initial_power', initial_power)

        self.save_b26(save_data=False, save_instrumets=True, save_log=False, save_settings=True)

        for power in power_values:

            self.log('current u-wave power : {:0.2f} dBm'.format(power))
            uwave_power.append(power)
            times.append(time.strftime('%Y_%m_%d_%H_%M_%S'))
            stage_1_temp.append(self.instruments['cryo_station'].platform_temp)
            stage_2_temp.append(self.instruments['cryo_station'].stage_1_temp)
            platform_temp.append(self.instruments['cryo_station'].stage_2_temp)

            # set power and wait to thermalized
            spectrum_analyzer.mode = 'TrackingGenerator'
            spectrum_analyzer.output_power = power
            time.sleep(self.settings['wait_time'])  #since the spectrum analyzer takes a full second =)

            self.scripts['get_spectrum'].update({'output_power': power})
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

            self.save_b26(save_data=True, save_instrumets=False, save_log=False, save_settings=False)

            progress = calc_progress(power)
            self.updateProgress.emit(progress)


        self.save_b26(save_data=False, save_instrumets=False, save_log=True, save_settings=False)

        spectrum_analyzer.output_power = initial_power


    def _plot(self, axes_list):
        self.scripts['get_spectrum'].plot(axes_list)
