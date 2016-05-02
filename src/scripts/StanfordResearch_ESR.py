from src.instruments import microwave_generator
from src.core.scripts import Script

from src.old_hardware_modules import APD as APDIn

# import standard libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import time
import pandas as pd
from PyQt4 import QtGui
from src.core import Parameter
from src.instruments import MicrowaveGenerator, DAQ

class StanfordResearch_ESR(Script):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/----data_tmp_default----', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('power_out', -45.0, float, 'output power (dBm)'),
        Parameter('esr_avrg', 50, int, 'number of esr averages'),
        Parameter('freq start', 2.82e9, float, 'start frequency of scan'),
        Parameter('freq stop', 2.92e9, float, 'end frequency of scan'),
        Parameter('freq points', 100, int, 'number of frequencies in scan'),
        Parameter('integration_time', 0.01, float, 'measurement time of fluorescent counts')
        # Parameter('runs_between_focusing', 10, int, 'runs after which we refocus - not implemented yet!!!')
    ])

    _INSTRUMENTS = {
        'microwave_generator': MicrowaveGenerator,
        'daq' : DAQ
    }

    _SCRIPTS = {

    }
    updateProgress = Signal(int)

    def __init__(self, instruments, scripts, name=None, settings=None, log_output=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_output=log_output)
        QThread.__init__(self)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        def calc_progress(power):
            raise NotImplementedError

            return progress

            raise NotImplementedError

        # send 100 to signal that script is finished
        self.updateProgress.emit(100)

    def plot(self, axes):
        raise NotImplementedError
