from src.core import Parameter, Script
from src.scripts import GalvoScanNIFpga
import numpy as np
import scipy as sp
import os
import time
from copy import deepcopy
import datetime
from src.plotting.plots_2d import plot_fluorescence_new, update_fluorescence


class GalvoScanNIFPGALoop(Script):
    """
Autofocus: Takes images at different piezo voltages and uses a heuristic to figure out the point at which the objective
            is focused.
    """

    _DEFAULT_SETTINGS = []

    _SCRIPTS = {
        'take_image': GalvoScanNIFpga
    }

    _INSTRUMENTS = {}

    def __init__(self, scripts, instruments = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, instruments, scripts, log_function= log_function, data_path = data_path)

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

    def _plot(self, axes_list):
        max_counts_plot = self.scripts['take_image'].settings['max_counts_plot']
        extent =  self.scripts['take_image'].settings['extent']
        plot_fluorescence_new(self.data['current_image'].transpose(), extent, axes_list[0], max_counts=max_counts_plot)


    def _update_plot(self, axes_list):
        """
        updates the image data. This is more efficient than replotting from scratch
        Args:
            axes_list:
        Returns:

        """
        axes_image = axes_list[0]
        max_counts_plot = self.scripts['take_image'].settings['max_counts_plot']
        update_fluorescence(self.data['current_image'].transpose(), axes_image, max_counts_plot)


    def get_axes_layout(self, figure_list):
        """
        returns the axes objects the script needs to plot its data
        the default creates a single axes object on each figure
        This can/should be overwritten in a child script if more axes objects are needed
        Args:
            figure_list: a list of figure objects
        Returns:
            axes_list: a list of axes objects

        """

        # only pick the first figure from the figure list, this avoids that get_axes_layout clears all the figures
        return Script.get_axes_layout(self, [figure_list[0]])
if __name__ == '__main__':


    #
    scripts, loaded_failed, instruments = Script.load_and_append({"gs": 'GalvoScanNIFPGALoop'})
    print(scripts)

