from src.instruments import microwave_generator
from src.core.scripts import Script
from PySide.QtCore import Signal, QThread

# import standard libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import time
import pandas as pd
from PySide.QtCore import Signal, QThread
from src.core import Parameter
from src.instruments import NI7845RReadWrite
from collections import deque

class FPGA_PolarizationController(Script):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('channel_WP_1', 5, range(8), 'channel that controls waveplate 1'),
        Parameter('channel_WP_2', 6, range(8), 'channel that controls waveplate 2'),
        Parameter('channel_WP_3', 7, range(8), 'channel that controls waveplate 3'),
        Parameter('V_1', 0.0, float, 'voltage applied to waveplate 1'),
        Parameter('V_2', 0.0, float, 'voltage applied to waveplate 2'),
        Parameter('V_3', 0.0, float, 'voltage applied to waveplate 3')
    ])

    _INSTRUMENTS = {
        'FPGA_IO': NI7845RReadWrite
    }

    _SCRIPTS = {

    }
    # updateProgress = Signal(int)

    def __init__(self, instruments, scripts = None, name=None, settings=None, log_output=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments, log_output=log_output)
        # QThread.__init__(self)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        fpga_io = self.instruments['FPGA_IO']['instance']
        fpga_io.update(self.instruments['FPGA_IO']['settings'])


    def plot(self, axes):
        pass

    def stop(self):
        self._abort = True


if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'pol_control': 'FPGA_PolarizationController'}, script, instr)

    print(script)
    print(failed)
    print(instr)