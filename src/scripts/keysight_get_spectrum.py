from src.core import Script, Parameter
from src.instruments import SpectrumAnalyzer \
    # , MicrowaveGenerator, CryoStation
from collections import deque
import time
import numpy as np

class KeysightGetSpectrum(Script):
    # COMMENT_ME

    _DEFAULT_SETTINGS = [
        # Parameter('start_frequency', 2.7e9, float, 'start frequency of spectrum'),
        # Parameter('stop_frequency', 3e9, float, 'end frequency of spectrum'),
        # Parameter('output_power',0.0, float, 'output power (dBm)'),
        # Parameter('output_on',True, bool, 'enable output'),
    ]

    _INSTRUMENTS = {
        'spectrum_analyzer' : SpectrumAnalyzer
    }

    _SCRIPTS = {}

    def __init__(self, instruments = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, log_function= log_function, data_path=data_path)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """



        instrument = self.instruments['spectrum_analyzer']['instance']
        settings = self.instruments['spectrum_analyzer']['settings']

        instrument.update(settings)
        trace = instrument.trace

        self.data = trace

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()



    def _plot(self, axes_list):
        #COMMENT_ME
        axes = axes_list[0]

        spectrum = self.data['amplitudes']
        freq = self.data['frequencies']

        axes.plot(freq, spectrum)
        axes.set_xlabel('frequencies')
        axes.set_xlabel('spectrum (??)')