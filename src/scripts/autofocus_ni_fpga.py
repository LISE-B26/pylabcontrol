from src.core import Parameter, Script
from src.scripts import GalvoScanNIFpga
import numpy as np
import scipy as sp
import os
import time
from copy import deepcopy


class AutoFocusNIFPGA(Script):
    """
Autofocus: Takes images at different piezo voltages and uses a heuristic to figure out the point at which the objective
            is focused.
    """

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', '----data_tmp_default----', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', False, bool, 'save data on/off'),
        Parameter('save_images', False, bool, 'save image taken at each voltage'),
        Parameter('piezo_min_voltage', 45, float, 'lower bound of piezo voltage sweep'),
        Parameter('piezo_max_voltage', 60, float, 'upper bound of piezo voltage sweep'),
        Parameter('num_sweep_points', 10, int, 'number of values to sweep between min and max voltage'),
        Parameter('focusing_optimizer', 'standard_deviation',
                  ['mean', 'standard_deviation', 'normalized_standard_deviation'], 'optimization function for focusing'),
        Parameter('wait_time', 0.1, float),
        Parameter('refined_scan', True, bool, 'Enable refined scan for hysteresis correction'),
        Parameter('refined_scan_range', 1.5, float, 'Width of refined scan'),
        Parameter('refined_scan_num_pts', 30, int, 'Number of points in refined scan')
    ])

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

        assert self.settings['piezo_min_voltage'] < self.settings['piezo_max_voltage'], 'Min voltage must be less than max!'

        # update instrument
        fpga_instr = self.scripts['take_image'].instruments['NI7845RGalvoScan']['instance']

        self.filename_image = None
        if self.settings['save'] or self.settings['save_images']:
            # create and save images
            self.filename_image = '{:s}\\image\\'.format(self.filename())
            if not os.path.exists(self.filename_image):
                os.makedirs(self.filename_image)

        sweep_voltages = np.linspace(self.settings['piezo_min_voltage'], self.settings['piezo_max_voltage'], self.settings['num_sweep_points'])


        self.autofocus_loop(sweep_voltages, fpga_instr=fpga_instr, tag='main_scan')

        # check to see if data should be saved and save it
        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

            self.save_image_to_disk('{:s}\\autofocus.jpg'.format(self.filename_image))

        if self.settings['refined_scan']:
            center = self.data['main_scan_focusing_fit_parameters'][2]
            min = center - self.settings['refined_scan_range']/2.0
            max = center + self.settings['refined_scan_range'] / 2.0
            sweep_voltages = np.linspace(min, max, self.settings['refined_scan_num_pts'])
            self.autofocus_loop(sweep_voltages, fpga_instr=fpga_instr, tag='refined_scan')

            # check to see if data should be saved and save it
            if self.settings['save']:
                # self.log('Saving...')
                self.save_b26()
                self.save_data()
                self.save_log()
                # self.log('Finished saving.')

                self.save_image_to_disk('{:s}\\autofocus.jpg'.format(self.filename_image))

    def _plot(self, axes_list):
        axis_focus, axis_image = axes_list
        # plot current focusing data
        axis_focus.plot(self.data['main_scan_sweep_voltages'][0:len(self.data['main_scan_focus_function_result'])],
                   self.data['main_scan_focus_function_result'])

        if 'refined_scan_sweep_voltages' in self.data.keys():
            axis_focus.plot(self.data['refined_scan_sweep_voltages'][0:len(self.data['refined_scan_focus_function_result'])],
                       self.data['refined_scan_focus_function_result'])



        # plot best fit
        if 'main_scan_focusing_fit_parameters' in self.data.keys() \
                and np.all(self.data['main_scan_focusing_fit_parameters'])\
                and len(self.data['main_scan_sweep_voltages']) == len(self.data['main_scan_focus_function_result']):
            gaussian = lambda x, params: params[0] + params[1] * np.exp(-1.0 * (np.square(x - params[2]) / (2 * params[3]) ** 2))

            fit_domain = np.linspace(self.settings['piezo_min_voltage'], self.settings['piezo_max_voltage'], 100)
            fit = gaussian(fit_domain, self.data['main_scan_focusing_fit_parameters'])

            axis_focus.plot(self.data['main_scan_sweep_voltages'], self.data['main_scan_focus_function_result'], 'b',
                       fit_domain, fit, 'r')
            axis_focus.legend(['data', 'best_fit'])


        # plot best fit
        if 'refined_scan_focusing_fit_parameters' in self.data.keys() \
                and np.all(self.data['refined_scan_focusing_fit_parameters'])\
                and len(self.data['refined_scan_sweep_voltages']) == len(self.data['refined_scan_focus_function_result']):
            gaussian = lambda x, params: params[0] + params[1] * np.exp(-1.0 * (np.square(x - params[2]) / (2 * params[3]) ** 2))

            center = self.data['main_scan_focusing_fit_parameters'][2]
            min = center - self.settings['refined_scan_range']/2.0
            max = center + self.settings['refined_scan_range']/2.0
            fit_domain = np.linspace(min, max, 100)

            fit = gaussian(fit_domain, self.data['refined_focusing_fit_parameters'])

            axis_focus.plot(self.data['refined_scan_sweep_voltages'], self.data['refined_scan_focus_function_result'], 'b',
                       fit_domain, fit, 'r')
            axis_focus.legend(['data', 'best_fit'])


        # format plot
        axis_focus.set_xlim([self.data['main_scan_sweep_voltages'][0], self.data['main_scan_sweep_voltages'][-1]])
        axis_focus.set_xlabel('Piezo Voltage [V]')

        if self.settings['focusing_optimizer'] == 'mean':
            ylabel = 'Image Mean [kcounts]'

        elif self.settings['focusing_optimizer'] == 'standard_deviation':
            ylabel = 'Image Standard Deviation [kcounts]'

        elif self.settings['focusing_optimizer'] == 'normalized_standard_deviation':
            ylabel = 'Image Normalized Standard Deviation [arb]'

        else:
            ylabel = self.settings['focusing_optimizer']

        axis_focus.set_ylabel(ylabel)
        axis_focus.set_title('Autofocusing Routine')



    def autofocus_loop(self, sweep_voltages, fpga_instr, tag = None):

        def fit_focus():
            # fit the data and set piezo to focus spot
            gaussian = lambda x, noise, amp, center, width: noise + amp * np.exp(
                -1.0 * (np.square((x - center)) / (2 * (width ** 2))))

            noise_guess = np.min(self.data[tag + '_focus_function_result'])
            amplitude_guess = np.max(self.data[tag + '_focus_function_result']) - noise_guess
            center_guess = np.mean(self.data[tag + '_sweep_voltages'])
            width_guess = 0.8

            reasonable_params = [noise_guess, amplitude_guess, center_guess, width_guess]

            try:
                p2, success = sp.optimize.curve_fit(gaussian, self.data[tag + '_sweep_voltages'],
                                                    self.data[tag + '_focus_function_result'], p0=reasonable_params,
                                                    bounds=([0, [np.inf, np.inf, 100., 100.]]), max_nfev=2000)

                self.log('Found fit parameters: ' + str(p2))

                if p2[2] > sweep_voltages[-1]:
                    fpga_instr.piezo = float(sweep_voltages[-1])
                    self.log('Best fit found center to be above max sweep range, setting voltage to max, {0} V'.format(
                        sweep_voltages[-1]))
                elif p2[2] < sweep_voltages[0]:
                    fpga_instr.piezo = float(sweep_voltages[0])
                    self.log('Best fit found center to be below min sweep range, setting voltage to min, {0} V'.format(
                        sweep_voltages[0]))
                else:
                    fpga_instr.piezo = float(p2[2])
            except(ValueError):
                p2 = [0, 0, 0, 0]
                average_voltage = np.mean(self.data[tag + '_sweep_voltages'])
                self.log('Could not converge to fit parameters, setting piezo to middle of sweep range, {0} V'.format(
                    average_voltage))
                fpga_instr.piezo = float(average_voltage)

            return p2

        self.data[tag + '_sweep_voltages'] = sweep_voltages
        self.data[tag + '_focus_function_result'] = []

        for index, voltage in enumerate(sweep_voltages):

            if self._abort:
                self.log('Leaving autofocusing loop')
                break

            # set the voltage on the piezo
            fpga_instr.piezo = float(voltage)
            time.sleep(self.settings['wait_time'])

            # take a galvo scan
            self.scripts['take_image'].run()


            current_image = self.scripts['take_image'].data['image_data']
            self.data['current_image'] = deepcopy(current_image)
            self.data['extent'] = self.scripts['take_image'].data['extent']
            # self.log('Took image.')

            # calculate focusing function for this sweep
            if self.settings['focusing_optimizer'] == 'mean':
                self.data[tag + '_focus_function_result'].append(np.mean(current_image))

            elif self.settings['focusing_optimizer'] == 'standard_deviation':
                self.data[tag + '_focus_function_result'].append(np.std(current_image))

            elif self.settings['focusing_optimizer'] == 'normalized_standard_deviation':
                self.data[tag + '_focus_function_result'].append(np.std(current_image) / np.mean(current_image))

            # update progress bar
            if tag == 'main_scan' and not self.settings['refined_scan']:
                progress = 99.0 * (np.where(sweep_voltages == voltage)[0] + 1) / float(self.settings['num_sweep_points'])
            elif tag == 'main_scan' and self.settings['refined_scan']:
                progress = 99.0 * (np.where(sweep_voltages == voltage)[0] + 1) / (2.0 * float(self.settings['num_sweep_points']))
            elif tag == 'refined_scan':
                progress = 50.0 + 99.0 * (np.where(sweep_voltages == voltage)[0] + 1) / (
                2.0 * float(self.settings['num_sweep_points']))
            self.updateProgress.emit(progress)

            # save image if the user requests it
            if self.settings['save_images']:
                self.scripts['take_image'].save_image_to_disk('{:s}\\image_{:03d}.jpg'.format(self.filename_image, index))
                self.scripts['take_image'].save_data('{:s}\\image_{:03d}.csv'.format(self.filename_image, index), 'image_data')

        p2 = [0, 0, 0, 0] # dont' fit for now
        # p2 = fit_focus()
        self.data[tag + '_focusing_fit_parameters'] = p2


if __name__ == '__main__':
    from src.core.read_write_functions import load_b26_file
    from src.core import Instrument

    in_data = load_b26_file('C:\\b26_tmp\\gui_settings.b26')

    instruments = in_data['instruments']
    scripts = in_data['scripts']
    probes = in_data['probes']

    instruments, failed = Instrument.load_and_append(instruments)
    scripts, failed, instruments = Script.load_and_append(
        script_dict=scripts,
        instruments=instruments,
        data_path='c:\\')

    #
    # scripts, loaded_failed, instruments = Script.load_and_append({"af": 'AutoFocusNIFPGA'})
    # print('===++++++===========++++++===========++++++========')
    print(scripts)
    # print('===++++++===========++++++===========++++++========')
    print(scripts['AutoFocusNIFPGA'].scripts['take_image'].instruments['NI7845RGalvoScan'])
    # print(type(scripts['af'].scripts['take_image'].instruments['NI7845RGalvoScan']['settings']))
    # print(type(scripts['af'].scripts['take_image'].instruments['NI7845RGalvoScan']['instance']))
    #
    # self.scripts, failed, self.instruments = Script.load_and_append(
    #     script_dict=scripts,
    #     instruments=self.instruments,
    #     log_function=self.log,
    #     data_path=self.gui_settings['data_folder'])

