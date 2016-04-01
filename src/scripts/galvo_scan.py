from src.core import Script, Parameter
from PyQt4 import QtCore
from PySide.QtCore import Signal, QThread
import time
from collections import deque
from src.instruments import ZIHF2
import numpy as np
from src.core import plotting


class GalvoScan(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('point_a', (0.0, 0.0), tuple, 'top left corner point of scan region')

    ])

    _INSTRUMENTS = {}
    # _INSTRUMENTS = {'zihf2' : Galvo}

    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None, log_output = None, timeout = 1000000000):

        self._recording = False
        self._timeout = timeout

        Script.__init__(self, name, settings, instruments, log_output = log_output)
        QThread.__init__(self)

        self.data = deque()



    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self.data.clear() # clear data queue

        self.log()
        # if self.settings['save']:
        #     self.save()


    def plot(self, axes):

        raise NotImplementedError

if __name__ == '__main__':
    pass

