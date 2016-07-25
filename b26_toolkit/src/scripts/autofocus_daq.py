import time

import numpy as np

from b26_toolkit.src.data_processing.fit_functions import fit_gaussian, guess_gaussian_parameter
from b26_toolkit.src.instruments import PiezoController
from b26_toolkit.src.plotting import plot_fluorescence_new
from src.core import Parameter, Script
from src.scripts import GalvoScanWithLightControl


class AutoFocus(Script):
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
        Parameter('wait_time', 0.1, float),
        Parameter('refined_scan', True, bool, 'Enable refined scan for hysteresis correction'),
        Parameter('refined_scan_range', 1.5, float, 'Width of refined scan'),
        Parameter('refined_scan_num_pts', 30, int, 'Number of points in refined scan')
    ]

    _INSTRUMENTS = {
        'z_piezo': PiezoController
    }
    _SCRIPTS = {
        'take_image': GalvoScanWithLightControl
    }

    def __init__(self, instruments, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Standard initialization for scripts. Also sets the number of scanning points to be 30x30 to speed autofocusing
        """
        Script.__init__(self, name, settings, instruments, scripts, log_function= log_function, data_path = data_path)

        self.scripts['take_image'].scripts['acquire_image'].settings['num_points'].update({'x': 30, 'y': 30})

    def _function(self):
        """
        Performs an autofocus using the focusing optimizer specified in settings and the scan range and settings
        specified in the subscript. Includes an optional 'refined scan' option to both get a better estimate of the
        ideal focus and to have a scan over a much smaller area to reduce the effect of piezo hysteresis
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

        def calc_progress(tag, refined_scan, i, N):
            """

            Args:
                tag: string - the current stage ot the script
                refined_scan: bool - if there will be a refined scan or not
                i: current loop iteration
                N: total number of iterations

            Returns:

            """
            # if tag == 'main_scan' and not refined_scan:
            #     progress = 99.0 * (np.where(sweep_voltages == voltage)[0] + 1) / float(self.settings['num_sweep_points'])
            # elif tag == 'main_scan' and refined_scan:
            #     progress = 99.0 * (np.where(sweep_voltages == voltage)[0] + 1) / (2.0 * float(self.settings['num_sweep_points']))
            # elif tag == 'refined_scan':
            #     progress = 50.0 + 99.0 * (np.where(sweep_voltages == voltage)[0] + 1) / (
            #     2.0 * float(self.settings['num_sweep_points']))
            if tag == 'main_scan' and not refined_scan:
                progress = 99.0 * (i + 1) / N
            elif tag == 'main_scan' and refined_scan:
                progress = 99.0 * (i + 1) / (2.0 * N)
            elif tag == 'refined_scan':
                progress = 50.0 + 99.0 * (i + 1) / (2.0 * N)
            return progress

        def autofocus_loop(sweep_voltages, tag=None):
            #COMMENT_ME

            self.data[tag + '_sweep_voltages'] = sweep_voltages
            self.data[tag + '_focus_function_result'] = []

            for index, voltage in enumerate(sweep_voltages):

                if self._abort:
                    self.log('Leaving autofocusing loop')
                    break

                # set the voltage on the piezo
                z_piezo.voltage = float(voltage)
                time.sleep(self.settings['wait_time'])

                # take a galvo scan
                self.scripts['take_image'].run()
                self.current_image = self.scripts['take_image'].data['image_data']
                self.extent = self.scripts['take_image'].data['extent']

                # calculate focusing function for this sweep
                self.data[tag + '_focus_function_result'].append(
                    calc_focusing_optimizer(self.current_image, self.settings['focusing_optimizer']))

                # update progress bar
                progress = calc_progress(tag, self.settings['refined_scan'], index, len(sweep_voltages))
                self.updateProgress.emit(progress)

                # save image if the user requests it
                if self.settings['save_images']:
                    self.scripts['take_image'].save_image_to_disk(
                        '{:s}\\image_{:03d}.jpg'.format(self.filename_image, index))


        def autofocus_fit(x_data,y_data):
            #COMMENT_ME
            estimate_params = guess_gaussian_parameter(x_data,y_data)
            fit_params = fit_gaussian(x_data,y_data, starting_params=estimate_params, bounds=None)

            return fit_params

        if self.settings['piezo_min_voltage'] < self.settings['piezo_max_voltage']:
            self.log('Min voltage must be less than max!')
            return

        self.filename_image = None
        if self.settings['save'] or self.settings['save_images']:
            # create and save images
            self.filename_image = '{:s}\\image\\'.format(self.filename())
            # if not os.path.exists(self.filename_image):
            #     os.makedirs(self.filename_image)

        sweep_voltages = np.linspace(self.settings['piezo_min_voltage'], self.settings['piezo_max_voltage'], self.settings['num_sweep_points'])

        z_piezo = self.instruments['z_piezo']['instance']
        z_piezo.update(self.instruments['z_piezo']['settings'])

        autofocus_loop(sweep_voltages, tag='main_scan')

        fit_params = autofocus_fit(self.data['main_scan_sweep_voltages'], self.data['main_scan_focus_function_result'])

        self.data['main_focusing_fit_parameters'] = fit_params

        # check to see if data should be saved and save it
        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk('{:s}\\autofocus.jpg'.format(self.filename_image))
            self.current_image = None

        if self.settings['refined_scan'] and not self._abort:
            center = self.data['main_scan_focusing_fit_parameters'][2]
            min = center - self.settings['refined_scan_range']/2.0
            max = center + self.settings['refined_scan_range'] / 2.0
            sweep_voltages = np.linspace(min, max, self.settings['refined_scan_num_pts'])
            self.autofocus_loop(sweep_voltages, tag='refined_scan')

            self.current_image = None

            # # check to see if data should be saved and save it
            # if self.settings['save']:
            #     # self.log('Saving...')
            #     self.save_b26()
            #     self.save_data()
            #     self.save_log()
            #     # self.log('Finished saving.')
            #
            #     self.save_image_to_disk('{:s}\\autofocus.jpg'.format(self.filename_image))


    def _plot(self, axes_list):
        # COMMENT_ME
        axis1 = axes_list[0]
        axis2 = axes_list[1]
        # plot current focusing data
        axis1.plot(self.data['main_scan_sweep_voltages'][0:len(self.data['main_scan_focus_function_result'])],
                   self.data['main_scan_focus_function_result'])

        if 'refined_scan_sweep_voltages' in self.data.keys():
            axis1.plot(self.data['refined_scan_sweep_voltages'][0:len(self.data['refined_scan_focus_function_result'])],
                       self.data['refined_scan_focus_function_result'])



        # plot best fit
        if 'main_scan_focusing_fit_parameters' in self.data.keys() \
                and np.all(self.data['main_scan_focusing_fit_parameters'])\
                and len(self.data['main_scan_sweep_voltages']) == len(self.data['main_scan_focus_function_result']):
            gaussian = lambda x, params: params[0] + params[1] * np.exp(-1.0 * (np.square(x - params[2]) / (2 * params[3]) ** 2))

            fit_domain = np.linspace(self.settings['piezo_min_voltage'], self.settings['piezo_max_voltage'], 100)
            fit = gaussian(fit_domain, self.data['main_scan_focusing_fit_parameters'])

            axis1.plot(self.data['main_scan_sweep_voltages'], self.data['main_scan_focus_function_result'], 'b',
                       fit_domain, fit, 'r')
            axis1.legend(['data', 'best_fit'])


        # plot best fit
        if 'refined_scan_focusing_fit_parameters' in self.data.keys() \
                and np.all(self.data['refined_scan_focusing_fit_parameters'])\
                and len(self.data['refined_scan_sweep_voltages']) == len(self.data['refined_scan_focus_function_result']):
            gaussian = lambda x, params: params[0] + params[1] * np.exp(-1.0 * (np.square(x - params[2]) / (2 * params[3]) ** 2))

            center = self.data['main_scan_focusing_fit_parameters'][2]
            min = center - self.settings['refined_scan_range']/2.0
            max = center + self.settings['refined_scan_range']/2.0
            fit_domain = np.linspace(min, max, 100)

            fit = gaussian(fit_domain, self.data['refined_scan_focusing_fit_parameters'])

            axis1.plot(self.data['refined_scan_sweep_voltages'], self.data['refined_scan_focus_function_result'], 'b',
                       fit_domain, fit, 'r')
            axis1.legend(['data', 'best_fit'])


        # format plot
        axis1.set_xlim([self.data['main_scan_sweep_voltages'][0], self.data['main_scan_sweep_voltages'][-1]])
        axis1.set_xlabel('Piezo Voltage [V]')

        if self.settings['focusing_optimizer'] == 'mean':
            ylabel = 'Image Mean [kcounts]'
        elif self.settings['focusing_optimizer'] == 'standard_deviation':
            ylabel = 'Image Standard Deviation [kcounts]'
        elif self.settings['focusing_optimizer'] == 'normalized_standard_deviation':
            ylabel = 'Image Normalized Standard Deviation [arb]'
        else:
            ylabel = self.settings['focusing_optimizer']

        axis1.set_ylabel(ylabel)
        axis1.set_title('Autofocusing Routine')

        if self.current_image is not None:
            plot_fluorescence_new(self.current_image, self.extent, axis2)


if __name__ == '__main__':
    scripts, loaded_failed, instruments = Script.load_and_append({"af": 'AutoFocus'})
    print(scripts, loaded_failed, instruments)
