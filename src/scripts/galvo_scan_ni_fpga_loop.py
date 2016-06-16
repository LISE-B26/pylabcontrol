from src.core import Parameter, Script
from PySide.QtCore import Signal, QThread
from src.scripts import GalvoScanNIFpga
import numpy as np
import scipy as sp
import os
import time
from copy import deepcopy
import datetime
from src.plotting.plots_2d import plot_fluorescence


class GalvoScanNIFPGALoop(Script, QThread):
    """
Autofocus: Takes images at different piezo voltages and uses a heuristic to figure out the point at which the objective
            is focused.
    """

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', '----data_tmp_default----', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', False, bool, 'save data on/off')
    ])

    _SCRIPTS = {
        'take_image': GalvoScanNIFpga
    }

    _INSTRUMENTS = {}
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(float)

    def __init__(self, scripts, instruments = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, instruments, scripts, log_function= log_function, data_path = data_path)
        # QtCore.QThread.__init__(self)
        QThread.__init__(self)

        self._plot_type = 'two'

        # self.scripts['take_image'].settings['num_points'].update({'x': 30, 'y': 30})

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # update instrument
        fpga_instr = self.scripts['take_image'].instruments['NI7845RGalvoScan']['instance']

        self.filename_image = None
        if self.settings['save']:
            # create and save images
            self.filename_image = '{:s}\\image\\'.format(self.filename())
            if not os.path.exists(self.filename_image):
                os.makedirs(self.filename_image)
        self.data = {}
        while True:
            if self._abort:
                self.log('Leaving autofocusing loop')
                break
            self.scripts['take_image'].run()
            self.scripts['take_image'].wait()
            current_image = self.scripts['take_image'].data['image_data']
            self.data['current_image'] = deepcopy(current_image)
            self.data['extent'] = self.scripts['take_image'].data['extent']
            self.updateProgress.emit(50)

        # check to see if data should be saved and save it
        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

            self.save_image_to_disk('{:s}\\autofocus.jpg'.format(self.filename_image))

        # update progress bar to show fit, reset _abort if it was triggered
        self.updateProgress.emit(100)

        self._abort = False

    def plot(self, figure1, figure2 = None):
        axis1 = self.get_axes(figure1)
        plot_fluorescence(self.data['current_image'], self.data['extent'], axis1)

    def stop(self):
        self._abort = True



if __name__ == '__main__':


    #
    scripts, loaded_failed, instruments = Script.load_and_append({"gs": 'GalvoScanNIFPGALoop'})
    print(scripts)

