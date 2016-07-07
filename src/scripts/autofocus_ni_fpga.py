from src.core import Parameter, Script
from src.scripts import GalvoScanNIFpga

from src.instruments import PiezoController
from src.scripts import GalvoScanWithLightControl

import numpy as np
import scipy as sp
import os
import time
from copy import deepcopy
from PyQt4.QtCore import pyqtSlot
from src.plotting.plots_2d import plot_fluorescence_new, update_fluorescence

class AutoFocusGeneric(Script):
    """
Autofocus: Takes images at different piezo voltages and uses a heuristic to figure out the point at which the objective
            is focused.
    """

    _DEFAULT_SETTINGS = [
        Parameter('save_images', False, bool, 'save image taken at each voltage'),
        Parameter('piezo_min_voltage', 45, float, 'lower bound of piezo voltage sweep'),
        Parameter('piezo_max_voltage', 60, float, 'upper bound of piezo voltage sweep'),
        Parameter('num_sweep_points', 10, int, 'number of values to sweep between min and max voltage'),
        Parameter('focusing_optimizer', 'standard_deviation',
                  ['mean', 'standard_deviation', 'normalized_standard_deviation'], 'optimization function for focusing'),
        Parameter('wait_time', 0.1, float)
    ]

    # the take image script depends on the particular hardware, e.g. DAQ or NIFPGA
    _SCRIPTS = {
        'take_image': NotImplemented
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

    @pyqtSlot(int)
    def _receive_signal(self, progress):
        """
        this function takes care of signals emitted by the subscripts
        the default behaviour is that it just reemits the signal
        Args:
            progress: progress of subscript take_image
        """
        # just ignore the signals from the subscript, we just send out our own signal
        pass
        # sender_emitter = self.sender()
        #
        # if self._current_subscript_stage['current_subscript'] is self.scripts['take_image']:
        #     img_index = self._current_subscript_stage['subscript_exec_count']['take_image']
        #     total_img_count = self.settings['num_sweep_points']
        #     progress = 1.* ((img_index -1 + float(progress)/ 100)/ total_img_count)
        # else:
        #     print('WHERE DID THIS SIGNAL COME FROM??? sender', sender_emitter)
        #
        #     current_image = self.scripts['take_image'].data['image_data']
        #     self.data['current_image'] = deepcopy(current_image)
        #     self.data['extent'] = self.scripts['take_image'].data['extent']
        #
        # self.updateProgress.emit(int(100.*progress))

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """


        def calc_focusing_optimizer(image, optimizer):
            """
            calculates a measure for how well the image is focused
            Args:
                optimizer: one of the three strings: mean, standard_deviation, normalized_standard_deviation
            Returns:  measure for how well the image is focused
            """
            if optimizer == 'mean':
                return np.mean(image)
            elif optimizer == 'standard_deviation':
                return np.std(image)
            elif optimizer == 'normalized_standard_deviation':
                return np.std(image) / np.mean(image)

        def autofocus_loop(sweep_voltages):
            """
            this is the actual autofocus loop
            Args:
                sweep_voltages: array of sweep voltages

            Returns:

            """
            # update instrument

            for index, voltage in enumerate(sweep_voltages):

                if self._abort:
                    self.log('Leaving autofocusing loop')
                    break

                # set the voltage on the piezo
                self._step_piezo(voltage, self.settings['wait_time'])

                # take a galvo scan
                self.scripts['take_image'].run()
                self.data['current_image'] = deepcopy(self.scripts['take_image'].data['image_data'])

                # calculate focusing function for this sweep
                self.data['focus_function_result'].append(
                    calc_focusing_optimizer(self.data['current_image'], self.settings['focusing_optimizer']))

                # save image if the user requests it
                if self.settings['save_images']:
                    self.scripts['take_image'].save_image_to_disk(
                        '{:s}\\image_{:03d}.jpg'.format(self.filename_image, index))
                    self.scripts['take_image'].save_data('{:s}\\image_{:03d}.csv'.format(self.filename_image, index),
                                                         'image_data')

                progress = 100. * index / len(sweep_voltages)
                self.updateProgress.emit(progress)
            p2 = [0, 0, 0, 0]  # dont' fit for now
            # p2 = fit_focus()
            self.data['fit_parameters'] = p2

        def fit_focus():
            # fit the data and set piezo to focus spot
            gaussian = lambda x, noise, amp, center, width: noise + amp * np.exp(
                -1.0 * (np.square((x - center)) / (2 * (width ** 2))))

            noise_guess = np.min(self.data['focus_function_result'])
            amplitude_guess = np.max(self.data['focus_function_result']) - noise_guess
            center_guess = np.mean(self.data['sweep_voltages'])
            width_guess = 0.8

            reasonable_params = [noise_guess, amplitude_guess, center_guess, width_guess]

            try:
                p2, success = sp.optimize.curve_fit(gaussian, self.data['_sweep_voltages'],
                                                    self.data['focus_function_result'], p0=reasonable_params,
                                                    bounds=([0, [np.inf, np.inf, 100., 100.]]), max_nfev=2000)

                self.log('Found fit parameters: ' + str(p2))

                if p2[2] > sweep_voltages[-1]:
                    fpga_instr.piezo = float(sweep_voltages[-1])
                    self.log(
                        'Best fit found center to be above max sweep range, setting voltage to max, {0} V'.format(
                            sweep_voltages[-1]))
                elif p2[2] < sweep_voltages[0]:
                    fpga_instr.piezo = float(sweep_voltages[0])
                    self.log(
                        'Best fit found center to be below min sweep range, setting voltage to min, {0} V'.format(
                            sweep_voltages[0]))
                else:
                    fpga_instr.piezo = float(p2[2])
            except(ValueError):
                p2 = [0, 0, 0, 0]
                average_voltage = np.mean(self.data['sweep_voltages'])
                self.log(
                    'Could not converge to fit parameters, setting piezo to middle of sweep range, {0} V'.format(
                        average_voltage))
                fpga_instr.piezo = float(average_voltage)

            return p2

        if self.settings['piezo_min_voltage'] > self.settings['piezo_max_voltage']:
            self.log('Min voltage must be less than max!')
            return


        if self.settings['save'] or self.settings['save_images']:
            self.filename_image = '{:s}\\image\\'.format(self.filename())
        else:
            self.filename_image = None

        sweep_voltages = np.linspace(self.settings['piezo_min_voltage'], self.settings['piezo_max_voltage'], self.settings['num_sweep_points'])

        self.data['sweep_voltages'] = sweep_voltages
        self.data['focus_function_result'] = []
        self.data['fit_parameters'] = [0, 0, 0, 0]
        self.data['current_image'] = np.zeros([1,1])
        self.data['extent'] = None

        autofocus_loop(sweep_voltages)

        # check to see if data should be saved and save it
        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk('{:s}\\autofocus.jpg'.format(self.filename_image))

    def _step_piezo(self, voltage, wait_time):
        """
        steps the piezo.  Has to be overwritten specifically for each different hardware realization
        voltage: target piezo voltage
        wait_time: settle time after voltage step
        """
        NotImplementedError

    def _plot(self, axes_list):

        axis_focus, axis_image = axes_list

        # if take image is running we take the data from there otherwise we use the scripts own image data
        if self._current_subscript_stage['current_subscript'] is self.scripts['take_image']:

            if 'image_data' in self.scripts['take_image'].data:
                current_image = self.scripts['take_image'].data['image_data']
                extent = self.scripts['take_image'].data['extent']
            else:
                current_image = None
        else:
            current_image = self.data['current_image']
            extent = self.data['extent']
        if current_image is not None:
            plot_fluorescence_new(current_image, extent, axis_image)

        if 'focus_function_result' in self.data:
            foucs_data = self.data['focus_function_result']
            sweep_voltages = self.data['sweep_voltages']
            if len(foucs_data)>0:
                axis_focus.plot(sweep_voltages[0:len(foucs_data)],foucs_data)
                axis_focus.hold(False)

    def _update_plot(self, axes_list):

        axis_focus, axis_image = axes_list

        # if take image is running we take the data from there otherwise we use the scripts own image data
        if self._current_subscript_stage['current_subscript'] is self.scripts['take_image']:
            if 'image_data' in self.scripts['take_image'].data:
                current_image = self.scripts['take_image'].data['image_data']
            else:
                current_image = None
        else:
            current_image = self.data['current_image']

        if current_image is not None:
            update_fluorescence(current_image, axis_image)

        axis_focus, axis_image = axes_list

        update_fluorescence(self.data['current_image'], axis_image)

        focus_data = self.data['focus_function_result']
        sweep_voltages = self.data['sweep_voltages']
        if len(focus_data) > 0:
            axis_focus.plot(sweep_voltages[0:len(focus_data)], focus_data)
            axis_focus.hold(False)


class AutoFocusNIFPGA(AutoFocusGeneric):
    """
Autofocus: Takes images at different piezo voltages and uses a heuristic to figure out the point at which the objective
            is focused.
    """

    _SCRIPTS = {
        'take_image': GalvoScanNIFpga
    }

    def __init__(self, scripts, instruments = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, instruments, scripts, log_function= log_function, data_path = data_path)

    def _step_piezo(self, voltage, wait_time):
        """
        steps the piezo.  Has to be overwritten specifically for each different hardware realization
        voltage: target piezo voltage
        wait_time: settle time after voltage step
        """
        fpga_instr = self.scripts['take_image'].instruments['NI7845RGalvoScan']['instance']
        # set the voltage on the piezo
        fpga_instr.piezo = float(voltage)
        time.sleep(wait_time)


class AutoFocusDAQ(AutoFocusGeneric):
    """
Autofocus: Takes images at different piezo voltages and uses a heuristic to figure out the point at which the objective
            is focused.
    """

    _INSTRUMENTS = {
        'z_piezo': PiezoController
    }
    _SCRIPTS = {
        'take_image': GalvoScanWithLightControl
    }

    def __init__(self, scripts, instruments = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, instruments, scripts, log_function= log_function, data_path = data_path)

    def _step_piezo(self, voltage, wait_time):
        """
        steps the piezo.  Has to be overwritten specifically for each different hardware realization
        voltage: target piezo voltage
        wait_time: settle time after voltage step
        """
        z_piezo = self.instruments['z_piezo']['instance']
        # set the voltage on the piezo
        z_piezo.voltage = float(voltage)
        time.sleep(self.settings['wait_time'])

    def _function(self):
        #update piezo settings
        z_piezo = self.instruments['z_piezo']['instance']
        z_piezo.update(self.instruments['z_piezo']['settings'])
        AutoFocusGeneric._function(self)
if __name__ == '__main__':


    # from src.core.read_write_functions import load_b26_file
    from src.core import Instrument
    #
    # in_data = load_b26_file('C:\\b26_tmp\\gui_settings.b26')
    #
    # instruments = in_data['instruments']
    # scripts = in_data['scripts']
    # probes = in_data['probes']
    #
    # instruments, failed = Instrument.load_and_append(instruments)
    # scripts, failed, instruments = Script.load_and_append(
    #     script_dict=scripts,
    #     instruments=instruments,
    #     data_path='c:\\')


    # scripts, loaded_failed, instruments = Script.load_and_append({"af": 'AutoFocusNIFPGA'})
    # print('===++++++===========++++++===========++++++========')
    # print(scripts)
    # print('===++++++===========++++++===========++++++========')
    # print(scripts['af'].scripts['take_image'].instruments['NI7845RGalvoScan'])
    # print(type(scripts['af'].scripts['take_image'].instruments['NI7845RGalvoScan']['settings']))
    # print(type(scripts['af'].scripts['take_image'].instruments['NI7845RGalvoScan']['instance']))
    #
    # self.scripts, failed, self.instruments = Script.load_and_append(
    #     script_dict=scripts,
    #     instruments=self.instruments,
    #     log_function=self.log,
    #     data_path=self.gui_settings['data_folder'])
    scripts, loaded_failed, instruments = Script.load_and_append({'take_image': 'GalvoScanNIFpga'})
    print('===++++++===========++++++===========++++++========')
    print(scripts)
    print('===++++++===========++++++===========++++++========')

    af = AutoFocusNIFPGA(scripts=scripts)
    print(af)
