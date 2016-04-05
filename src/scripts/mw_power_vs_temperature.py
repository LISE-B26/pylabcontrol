from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.instruments import SpectrumAnalyzer, MicrowaveGenerator, CryoStation
from collections import deque
import time
import numpy as np

class MWSpectraVsPower(Script, QThread):

    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('start_frequency', 2.7e9, float, 'start frequency of spectrum'),
        Parameter('end_frequency', 3e9, float, 'end frequency of spectrum'),
        Parameter('microwave_frequency', 3e9, float, 'frequency of microwave'),
        Parameter('uwave_power_min', -45.0, float, 'microwave power min (dBm)'),
        Parameter('uwave_power_max', -12.0, float,'microwave power max (dBm)'),
        Parameter('uwave_power_step', 2.0, float,'microwave power step (dBm)'),
        Parameter('wait_time', 2.0, float,'time to wait after change in power (seconds)')
    ])

    _INSTRUMENTS = {
        'microwave_generator' : MicrowaveGenerator,
        'cryo_station' : CryoStation,
        'spectrum_analyzer' : SpectrumAnalyzer
    }

    _SCRIPTS = {}

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(int)
    def __init__(self, instruments = None, name = None, settings = None,  log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, log_output = log_output)
        # QtCore.QThread.__init__(self)
        QThread.__init__(self)
        # self.data = deque()

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        def calc_progress(power):
            min, max =self.settings['uwave_power_min'], self.settings['uwave_power_max']

            progress = power-min / (max-min) *100

            return progress

        # set up instruments
        # todo: FINISH IMPLEMENTATIUON
        self.instruments['microwave_generator'].FREQ = self.settings['microwave_frequency']



        self.save(save_data=False, save_instrumets=True, save_log=False, save_settings=True)


        power_values = [float(power) for power in np.arange(self.settings['uwave_power_min'], self.settings['uwave_power_max'], self.settings['uwave_power_step'])]

        stage_1_temp = []
        stage_2_temp = []
        platform_temp = []
        times = []
        spectrum = []
        uwave_power = []


        for power in power_values:
        # for power in range(self.settings['uwave_power_min'], self.settings['uwave_power_max'], self.settings['uwave_power_step']):
            # set u-wave power
            self.instruments['microwave_generator'].AMPR = power
            time.sleep(self.settings['wait_time'])  #since the spectrum analyzer takes a full second =)

            uwave_power.append(power)
            times.append(time.strftime('%Y_%m_%d_%H_%M_%S'))
            stage_1_temp.append(self.instruments['cryo_station'].platform_temp)
            stage_2_temp.append(self.instruments['cryo_station'].stage_1_temp)
            platform_temp.append(self.instruments['cryo_station'].stage_2_temp)


            trace = self.instruments['spectrum_analyzer'].trace
            freq = [item[0] for item in trace]
            trans = [item[1] for item in trace]

            spectrum.append(trans)

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

            self.log('current u-wave power : {:0.2f} dBm'.format(power))

            self.updateProgress.emit(progress)
        self.save(save_data=False, save_instrumets=False, save_log=True, save_settings=False)

        self.instruments['microwave_generator'].AMPR = -60


    def plot(self, axes):

        spectrum = self.data[-1]['spectrum']
        freq = self.data[-1]['frequency']

        axes.plot(freq, spectrum)