"""

This is just a temporary file which contains derived script using the pulse blaster

In the future those scripts will be created dynamically




"""

from src.core import Parameter, Script

from src.scripts.pulse_blaster_scripts import Rabi
from src.scripts import FindMaxCounts2D
import numpy as np
from PyQt4.QtCore import pyqtSlot
from copy import deepcopy


class Rabi_Power_Sweep(Script):
    """
This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
    """
    _DEFAULT_SETTINGS = [
        Parameter('min_mw_power', -45.0, float, 'minimum microwave power in dB'),
        Parameter('max_mw_power', -45.0, float, 'maximum microwave power in dB'),
        Parameter('mw_power_step', 1.0, float, 'power to step by in dB')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {'Rabi': Rabi, 'Find_NV': FindMaxCounts2D}

    def __init__(self, instruments=None, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        """
        Standard script initialization
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)

    def _function(self):
        mw_power_values = np.arange(self.settings['min_mw_power'],
                                    self.settings['max_mw_power'] + self.settings['mw_power_step'],
                                    self.settings['mw_power_step'])
        self.data = {'mw_power_values': mw_power_values, 'NV_points': []}
        tag = self.settings['tag']
        for power in mw_power_values:
            if self._abort:
                break
            self.scripts['Find_NV'].run()
            nv_location = self.scripts['Find_NV'].data['maximum_point']
            # reset initial point for longer time tracking
            self.scripts['Find_NV'].settings['initial_point']['x'] = nv_location[0]
            self.scripts['Find_NV'].settings['initial_point']['y'] = nv_location[1]
            if self.settings['save']:
                self.settings['tag'] = tag + '_image_' + str(power) + 'dB'
                self.save_image_to_disk()
            self.data['NV_points'].append(nv_location)  # made an array to allow saving
            self.scripts['Rabi'].settings['mw_power'] = float(power)  # power is a numpy float, needs to be cast
            self.scripts['Rabi'].settings['tag'] = str(power) + 'dB'
            self.scripts['Rabi'].run()
        if self.settings['save']:
            self.settings['tag'] = tag
            self.save_b26()
            self.save_data()
            self.save_log()

    def plot(self, figure_list):
        if self._current_subscript_stage['current_subscript'] == self.scripts['Find_NV']:
            self.scripts['Find_NV'].plot(figure_list)
        else:  # also plot Rabi if no current subscript
            self.scripts['Rabi'].plot(figure_list)


class Rabi_Loop(Script):
    """
This script repeats the Rabi script N times and refocuses on the NV between every iteration
    """
    _DEFAULT_SETTINGS = [
        Parameter('N', 1, int, 'number of repetitions of loop')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {'Rabi': Rabi, 'Find_NV': FindMaxCounts2D}

    def __init__(self, instruments=None, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        """
        Standard script initialization
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)

    @pyqtSlot(int)
    def _receive_signal(self, progress):
        """
        this function takes care of signals emitted by the subscripts
        the default behaviour is that it just reemits the signal
        Args:
            progress: progress of subscript
        """
        self.progress = 100. * (float(self.index) + float(progress) / 100.) / self.settings['N']
        self.updateProgress.emit(int(self.progress))

    def _function(self):

        self.data = {'counts_init': [], 'counts_final': [], 'NV_points': []}
        tag = self.settings['tag']
        for index in range(self.settings['N']):
            self.index = index
            if self._abort:
                break
            self.scripts['Find_NV'].run()
            nv_location = self.scripts['Find_NV'].data['maximum_point']
            # reset initial point for longer time tracking
            self.scripts['Find_NV'].settings['initial_point'] = nv_location

            self.data['NV_points'].append([nv_location['x'], nv_location['y']])  # made an array to allow saving
            self.scripts['Rabi'].run()

            self.data['counts_init'].append(deepcopy(self.scripts['Rabi'].data['counts'][:, 0]))
            self.data['counts_final'].append(deepcopy(self.scripts['Rabi'].data['counts'][:, 1]))

            if index == 0:
                self.data['tau'] = self.scripts['Rabi'].data['tau']

        if self.settings['save']:
            self.settings['tag'] = tag
            self.save_b26()
            self.save_data()
            self.save_log()

    def plot(self, figure_list):
        if self._current_subscript_stage['current_subscript'] == self.scripts['Find_NV']:
            self.scripts['Find_NV'].plot(figure_list)
        else:  # also plot Rabi if no current subscript
            self.scripts['Rabi'].plot(figure_list)


class RoundPiPulseTime(Script):
    """
This script runs a Rabi script, fits the result to a sin wave to retrieve the Rabi oscillation frequency.
Then it increases the power of the microwave pulse such that the time for a Rabi-oscilation is a multiple of 5ns.
After that it again runs a the Rabi script with the optimized microwave power to double check.
    """
    _DEFAULT_SETTINGS = [
        Parameter('tolerance', 1, float, 'tolerance in ns for new pi pulse')
    ]

    _INSTRUMENTS = {}

    _SCRIPTS = {'rabi': Rabi}

    def __init__(self, instruments=None, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)

    def _function(self):

        # first run
        self.data = {'old_power': None, 'new_power': None, 'old_time': None, 'new_time': None, 'old_fit_params': None,
                     'new_fit_params': None}
        self.scripts['rabi'].run()

        # fit data to decaying oscillations
        power_dBm = self.scripts['rabi'].settings['mw_power']
        self.data['old_power'] = power_dBm
        rabi_tau = self.scripts['rabi'].data['tau']
        rabi_counts = self.scripts['rabi'].data['counts']
        fit_params = fit_rabi_decay(rabi_tau, rabi_counts)
        radial_freq = fit_params[1]
        self.data['old_fit_params'] = fit_params

        # calculate the target pi-pulse time and power given the fit
        pi_time = 1 / (2 * (radial_freq / (2 * np.pi)))  # gives pi_time in nanoseconds
        self.data['old_time'] = pi_time
        rounded_pi_time = ((np.ceil(pi_time / 5.0) * 5.0))  # rounds up to nearest 5 ns
        self.data['new_time'] = rounded_pi_time
        power_linear = 10.0 ** (power_dBm / 10.0)
        rounded_power_linear = power_linear * (
                                              pi_time / rounded_pi_time) ** 2  # want sqrt(power)*pi_time to be constant
        rounded_power_dBm = 10.0 * np.log10(rounded_power_linear)
        self.data['new_power'] = rounded_power_dBm

        print(rounded_power_dBm)
        assert (rounded_power_dBm < -2)

        # run again to veryfy that esimates are correct
        self.scripts['rabi'].settings['mw_power'] = float(rounded_power_dBm)
        self.scripts['rabi'].run()

        # fit new data
        rabi_counts = self.scripts['rabi'].data['counts']
        fit_params = fit_rabi_decay(rabi_tau, rabi_counts)
        radial_freq = fit_params[1]
        self.data['new_fit_params'] = fit_params
        new_pi_time = 1 / (2 * (radial_freq / (2 * np.pi)))  # gives pi_time in nanoseconds
        error = abs(new_pi_time - rounded_pi_time)
        print('new_time', rounded_pi_time)
        print('new_power', rounded_power_dBm)
        if error > self.settings['tolerance']:
            print('Optimization FAILED. Error is ' + str(error) + ' ns.')
        else:
            print('Optimization SUCCESS. Error is ' + str(error) + ' ns.')

    def plot(self, figure_list):
        self.scripts['rabi'].plot(figure_list)
