from src.core import Parameter, Script
from PySide.QtCore import Signal, QThread
from src.instruments import PiezoController
from src.scripts import GalvoScan
import numpy as np
import scipy as sp
import os


class AutoFocus(Script, QThread):
    """
Autofocus: Takes images at different piezo voltages and uses a heuristic to figure out the point at which the objective
            is focused.
    """

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/----data_tmp_default----', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('save_images', False, bool, 'save image taken at each voltage'),
        Parameter('piezo_min_voltage', 30.0, float, 'lower bound of piezo voltage sweep'),
        Parameter('piezo_max_voltage', 70.0, float, 'upper bound of piezo voltage sweep'),
        Parameter('num_sweep_points', 10, int, 'number of values to sweep between min and max voltage'),
        Parameter('focusing_optimizer', 'standard_deviation', ['mean', 'standard_deviation'], 'optimization function for focusing'),
        Parameter('wait_time', 0.1, float)
    ])

    _INSTRUMENTS = {
        'z_piezo': PiezoController
    }
    _SCRIPTS = {
        'take_image': GalvoScan
    }

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(float)

    def __init__(self, instruments, scripts, name = None, settings = None, log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, instruments, scripts, log_output = log_output)
        # QtCore.QThread.__init__(self)
        QThread.__init__(self)

        self._plot_type = 'two'


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        assert self.settings['piezo_min_voltage'] < self.settings['piezo_max_voltage'], 'Min voltage must be less than max!'

        z_piezo = self.instruments['z_piezo']['instance']
        z_piezo.update(self.instruments['z_piezo']['settings'])

        sweep_voltages = np.linspace(self.settings['piezo_min_voltage'],
                                     self.settings['piezo_max_voltage'],
                                     self.settings['num_sweep_points'])

        self.data['sweep_voltages'] = sweep_voltages
        self.data['focus_function_result'] = []

        filename_image = None
        if self.settings['save'] or self.settings['save_images']:
            # create and save images
            filename_image = '{:s}\\image\\'.format(self.filename())
            if not os.path.exists(filename_image):
                os.makedirs(filename_image)

        for index, voltage in enumerate(sweep_voltages):

            if self._abort:
                self.log('Leaving focusing loop')
                break

            # set the voltage on the piezo
            z_piezo.voltage = float(voltage)
            self.log('Voltage set to {:.3f}'.format(voltage))

            # take a galvo scan
            self.scripts['take_image'].run()
            current_image = self.scripts['take_image'].data['image_data']
            self.log('Took image.')

            # calculate focusing function for this sweep
            if self.settings['focusing_optimizer'] == 'mean':
                self.data['focus_function_result'].append(np.mean(current_image))

            elif self.settings['focusing_optimizer'] == 'standard_deviation':
                self.data['focus_function_result'].append(np.std(current_image))

            # update progress bar
            progress = 99.0 * (np.where(sweep_voltages == voltage)[0]+1) / float(self.settings['num_sweep_points'])
            self.updateProgress.emit(progress)

            # save image if the user requests it
            if self.settings['save_images']:
                self.scripts['take_image'].save_image_to_disk('{:s}\\image_{:03d}.jpg'.format(filename_image, index))

        # fit the data and set piezo to focus spot
        gaussian = lambda x, noise, amp, center, width: noise + amp * np.exp(-1.0 * (np.square((x-center))/(2*(width**2))))

        noise_guess = np.min(self.data['focus_function_result'])
        amplitude_guess = np.max(self.data['focus_function_result']) - noise_guess
        center_guess = np.mean(self.data['sweep_voltages'])
        width_guess = 0.8

        reasonable_params = [noise_guess, amplitude_guess, center_guess, width_guess]

        try:
            p2, success = sp.optimize.curve_fit(gaussian, self.data['sweep_voltages'],
                                                self.data['focus_function_result'], p0=reasonable_params,
                                                bounds=([0, [np.inf, np.inf, 100., 100.]]), max_nfev=2000)

            self.log('Found fit parameters: ' + str(p2))

            if p2[2] > self.settings['piezo_max_voltage']:
                z_piezo.voltage = self.settings['piezo_max_voltage']
                self.log('Best fit found center to be above max sweep range, setting voltage to max, {0} V'.format(
                    self.settings['piezo_max_voltage']))
            elif p2[2] < self.settings['piezo_min_voltage']:
                z_piezo.voltage = self.settings['piezo_min_voltage']
                self.log('Best fit found center to be below min sweep range, setting voltage to min, {0} V'.format(
                    self.settings['piezo_min_voltage']))
            else:
                z_piezo.voltage = float(p2[2])
        except(ValueError):
            p2 = [0, 0, 0, 0]
            average_voltage = np.mean(self.data['sweep_voltages'])
            self.log('Could not converge to fit parameters, setting piezo to middle of sweep range, {0} V'.format(average_voltage))
            z_piezo.voltage = float(average_voltage)

        self.data['focusing_fit_parameters'] = p2

        # check to see if data should be saved and save it
        if self.settings['save']:
            self.log('Saving...')
            self.save()
            self.save_data()
            self.save_log()
            self.log('Finished saving.')

            self.save_image_to_disk('{:s}\\autofocus.jpg'.format(filename_image))

        # update progress bar to show fit, reset _abort if it was triggered
        self.updateProgress.emit(100.0)

        self._abort = False

    def plot(self, axis1, axis2 = None):
        # plot current focusing data
        axis1.plot(self.data['sweep_voltages'][0:len(self.data['focus_function_result'])],
                   self.data['focus_function_result'])


        # plot best fit
        if 'focusing_fit_parameters' in self.data.keys() and np.all(self.data['focusing_fit_parameters']):
            gaussian = lambda x, params: params[0] + params[1] * np.exp(-1.0 * (np.square(x - params[2]) / (2 * params[3]) ** 2))

            fit_domain = np.linspace(self.settings['piezo_min_voltage'], self.settings['piezo_max_voltage'], 100)
            fit = gaussian(fit_domain, self.data['focusing_fit_parameters'])

            axis1.plot(self.data['sweep_voltages'], self.data['focus_function_result'], 'b',
                       fit_domain, fit, 'r')
            axis1.legend(['data', 'best_fit'])


        # format plot
        axis1.set_xlim([self.data['sweep_voltages'][0], self.data['sweep_voltages'][-1]])
        axis1.set_xlabel('Piezo Voltage [V]')

        if self.settings['focusing_optimizer'] == 'mean':
            ylabel = 'Image Mean [kcounts]'

        elif self.settings['focusing_optimizer'] == 'standard_deviation':
            ylabel = 'Image Standard Deviation [kcounts]'

        axis1.set_ylabel(ylabel)
        axis1.set_title('Autofocusing Routine')

        if axis2:
            self.scripts['take_image'].plot(axis2)


    def stop(self):
        self._abort = True


if __name__ == '__main__':
    #scripts, loaded_failed, instruments = Script.load_and_append({"af": 'AutoFocus'})
    #print(scripts, loaded_failed, instruments)
    print(np.array([0, 0, 0, 0]) == [0, 0, 0, 0])