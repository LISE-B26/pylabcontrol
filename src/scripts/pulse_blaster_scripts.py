from src.core import Parameter, Script
from src.instruments import DAQ, B26PulseBlaster, MicrowaveGenerator, Pulse
from src.scripts import ExecutePulseBlasterSequence
from src.scripts import FindMaxCounts2D
from PyQt4.QtCore import pyqtSlot
import numpy as np
from src.plotting.plots_1d import plot_esr, plot_pulses, update_pulse_plot, plot_1d_simple, update_1d_simple
from src.data_processing.fit_functions import fit_rabi_decay, cose_with_decay

class PulsedESR(ExecutePulseBlasterSequence):
    """
This script applies a microwave pulse at fixed power and durations for varying frequencies
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('tau_mw', 200, float, 'the time duration of the microwaves (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('num_averages', 1000000, int, 'number of averages'),
        Parameter('reset_time', 1000000, int, 'time with laser on at the beginning to reset state'),
        Parameter('freq_start', 2.82e9, float, 'start frequency of scan in Hz'),
        Parameter('freq_stop', 2.92e9, float, 'end frequency of scan in Hz'),
        Parameter('freq_points', 100, int, 'number of frequencies in scan in Hz'),
        Parameter('power_mode', 'absolute', ['absolute', 'scaling'], 'Switches between absolute power (in dBm) and scaling power'),
        Parameter('new_tau_mw', 200, float, 'New time to use to scale the power while in scaling mode'),
        Parameter('max_mw_power', -2, float, 'Set a maximum safe microwave power to prevent burning out components')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}

    def _function(self):
        if self.settings['power_mode'] is 'scaling':
            self.settings['mw_power'] = self._get_scaled_power(self.settings['new_tau_mw'], self.settings['tau_mw'], self.settings['mw_power'])
            self.settings['tau_mw'] = self.settings['new_tau_mw']
            assert self.settings['mw_power'] < self.settings['max_mw_power']

        self.instruments['mw_gen']['instance'].update({'modulation_type': 'IQ'})
        self.instruments['mw_gen']['instance'].update({'amplitude': self.settings['mw_power']})
        self.instruments['mw_gen']['instance'].update({'enable_output': True})

        assert self.settings['freq_start'] < self.settings['freq_stop']

        self.data = {'mw_frequencies': np.linspace(self.settings['freq_start'], self.settings['freq_stop'],
                                                   self.settings['freq_points']), 'esr_counts': []}

        for i, mw_frequency in enumerate(self.data['mw_frequencies']):
            self._loop_count = i
            self.instruments['mw_gen']['instance'].update({'frequency': float(mw_frequency)})
            super(PulsedESR, self)._function(self.data)
            self.data['esr_counts'].append(self.data['counts'])

    def _get_scaled_power(self, new_tau_mw, tau_mw, mw_power_dBm):
        power_linear = 10 ** (mw_power_dBm / 10.0)
        new_power_linear = power_linear * (tau_mw / new_tau_mw) ** 2  # want sqrt(power)*pi_time to be constant
        new_power_dBm = 10 * np.log10(new_power_linear)
        return new_power_dBm

    def _calc_progress(self):
        progress = int(100. * (self._loop_count) / self.settings['freq_points'])
        return progress

    def _plot(self, axes_list):
        '''
        Plot 1: self.data['tau'], the list of times specified for a given experiment, verses self.data['counts'], the data
        received for each time
        Plot 2: the pulse sequence performed at the current time (or if plotted statically, the last pulse sequence
        performed

        Args:
            axes_list: list of axes to write plots to (uses first 2)

        '''
        mw_frequencies = self.data['mw_frequencies']
        esr_counts = self.data['esr_counts']
        axis1 = axes_list[0]
        if not esr_counts == []:
            counts = esr_counts
            plot_esr(axis1, mw_frequencies[0:len(counts)], counts)
            axis1.hold(False)
        axis2 = axes_list[1]
        plot_pulses(axis2, self.pulse_sequences[0])

    def _update_plot(self, axes_list):
        mw_frequencies = self.data['mw_frequencies']
        esr_counts = self.data['esr_counts']
        axis1 = axes_list[0]
        if not esr_counts == []:
            counts = esr_counts
            plot_esr(axis1, mw_frequencies[0:len(counts)], counts)
            axis1.hold(False)
            # axis2 = axes_list[1]
            # update_pulse_plot(axis2, self.pulse_sequences[0])

    def _create_pulse_sequences(self):

        '''

        Returns: pulse_sequences, num_averages, tau_list
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
            meas_time: the width (in ns) of the daq measurement

        '''

        reset_time = self.settings['reset_time']
        tau = self.settings['tau_mw']
        pulse_sequences = [[Pulse('laser', 0, reset_time),
                            Pulse('microwave_i', reset_time, tau),
                            Pulse('laser', reset_time + tau, self.settings['meas_time']),
                            Pulse('apd_readout', reset_time + tau, self.settings['meas_time'])
                            ]]

        tau_list = [tau]
        end_time_max = 0
        for pulse_sequence in pulse_sequences:
            for pulse in pulse_sequence:
                end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        for pulse_sequence in pulse_sequences:
            pulse_sequence.append(Pulse('laser', end_time_max + 1850, 15))

        return pulse_sequences, self.settings['num_averages'], tau_list, self.settings['meas_time']


class Rabi(ExecutePulseBlasterSequence):
    """
This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('mw_frequency', 2.87e9, float, 'microwave frequency in Hz'),
        Parameter('time_step', 5, [5, 10, 20, 50, 100, 200, 500, 1000, 10000, 100000],
                  'time step increment of rabi pulse duration (in ns)'),
        Parameter('time', 200, float, 'total time of rabi oscillations (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('num_averages', 1000000, int, 'number of averages'),
        Parameter('reset_time', 10000, int, 'time with laser on at the beginning to reset state'),
        Parameter('skip_invalid_sequences', False, bool, 'Skips any sequences with <15ns commands')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}

    def _function(self):
        self.instruments['mw_gen']['instance'].update({'modulation_type': 'IQ'})
        self.instruments['mw_gen']['instance'].update({'amplitude': self.settings['mw_power']})
        self.instruments['mw_gen']['instance'].update({'frequency': self.settings['mw_frequency']})
        super(Rabi, self)._function()

    def _create_pulse_sequences(self):
        '''

        Returns: pulse_sequences, num_averages, tau_list
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
            meas_time: the width (in ns) of the daq measurement

        '''
        pulse_sequences = []
        tau_list = range(int(max(15, self.settings['time_step'])), int(self.settings['time'] + 15),
                         self.settings['time_step'])
        reset_time = self.settings['reset_time']
        for tau in tau_list:
            pulse_sequences.append([Pulse('laser', 0, reset_time),
                                    Pulse('microwave_i', reset_time + 200, tau),
                                    Pulse('laser', reset_time + tau + 300, self.settings['meas_time']),
                                    Pulse('apd_readout', reset_time + tau + 300, self.settings['meas_time'])
                                    ])

        end_time_max = 0
        for pulse_sequence in pulse_sequences:
            for pulse in pulse_sequence:
                end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        for pulse_sequence in pulse_sequences:
            pulse_sequence.append(Pulse('laser', end_time_max + 1850, 15))

        return pulse_sequences, self.settings['num_averages'], tau_list, self.settings['meas_time']

    def _calc_progress(self):
        return 50

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


class Rabi_Power_Sweep_Single_Tau(ExecutePulseBlasterSequence):
    """
This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
    """
    _DEFAULT_SETTINGS = [
        Parameter('min_mw_power', -45.0, float, 'minimum microwave power in dB'),
        Parameter('max_mw_power', -45.0, float, 'maximum microwave power in dB'),
        Parameter('mw_power_step', 1.0, float, 'power to step by in dB'),
        Parameter('mw_frequency', 2.87e9, float, 'microwave frequency in Hz'),
        Parameter('mw_time', 200, float, 'total time of rabi oscillations (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('num_averages', 1000000, int, 'number of averages'),
        Parameter('reset_time', 10000, int, 'time with laser on at the beginning to reset state'),
        Parameter('skip_invalid_sequences', False, bool, 'Skips any sequences with <15ns commands')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}

    def _function(self):
        self.instruments['mw_gen']['instance'].update({'modulation_type': 'IQ'})
        self.instruments['mw_gen']['instance'].update({'frequency': self.settings['mw_frequency']})
        mw_power_values = np.arange(self.settings['min_mw_power'],
                                    self.settings['max_mw_power'] + self.settings['mw_power_step'],
                                    self.settings['mw_power_step'])

        print(mw_power_values)
        self.data = {'mw_power_values': mw_power_values, 'counts_for_mw': np.zeros(len(mw_power_values))}
        for index, power in enumerate(mw_power_values):
            self.instruments['mw_gen']['instance'].update({'amplitude': float(power)})
            super(Rabi_Power_Sweep_Single_Tau, self)._function(self.data)
            self.data['counts_for_mw'][index] = self.data['counts'][0]

    def _create_pulse_sequences(self):
        '''

        Returns: pulse_sequences, num_averages, tau_list
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
            meas_time: the width (in ns) of the daq measurement

        '''
        pulse_sequences = []
        reset_time = self.settings['reset_time']
        mw_time = self.settings['mw_time']
        pulse_sequences.append([Pulse('laser', 0, reset_time),
                                Pulse('microwave_i', reset_time + 200, mw_time),
                                Pulse('laser', reset_time + mw_time + 300, self.settings['meas_time']),
                                Pulse('apd_readout', reset_time + mw_time + 300, self.settings['meas_time'])
                                ])

        end_time_max = 0
        for pulse_sequence in pulse_sequences:
            for pulse in pulse_sequence:
                end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        for pulse_sequence in pulse_sequences:
            pulse_sequence.append(Pulse('laser', end_time_max + 1850, 15))

        return pulse_sequences, self.settings['num_averages'], [mw_time], self.settings['meas_time']

    def _plot(self, axes_list):
        '''
        Plot 1: self.data['tau'], the list of times specified for a given experiment, verses self.data['counts'], the data
        received for each time
        Plot 2: the pulse sequence performed at the current time (or if plotted statically, the last pulse sequence
        performed

        Args:
            axes_list: list of axes to write plots to (uses first 2)

        '''
        counts = self.data['counts_for_mw']
        x_data = self.data['mw_power_values']
        axis1 = axes_list[0]
        if not counts == []:
            plot_1d_simple(axis1, x_data, [counts], x_label='microwave power (dBm)')
        axis2 = axes_list[1]
        plot_pulses(axis2, self.pulse_sequences[self.sequence_index])

    def _update_plot(self, axes_list):
        '''
        Updates plots specified in _plot above
        Args:
            axes_list: list of axes to write plots to (uses first 2)

        '''
        counts = self.data['counts_for_mw']
        x_data = self.data['mw_power_values']
        axis1 = axes_list[0]
        if not counts == []:
            update_1d_simple(axis1, x_data, [counts])
        axis2 = axes_list[1]
        update_pulse_plot(axis2, self.pulse_sequences[self.sequence_index])


# class Pulsed_ESR(ExecutePulseBlasterSequence):
#     """
# This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
#     """
#     _DEFAULT_SETTINGS = [
#         Parameter('mw_power', -45.0, float, 'microwave power in dB'),
#         Parameter('mw_frequency', 2.87e9, float, 'microwave frequency in Hz'),
#         Parameter('delay_until_mw', 100, float, 'total time of rabi oscillations (in ns)'),
#         Parameter('mw_duration', 200, float, 'total time of rabi oscillations (in ns)'),
#         Parameter('time_step', 15, float,
#                   'time step increment of rabi pulse duration (in ns)'),
#         Parameter('time', 400, float, 'total time of rabi oscillations (in ns)'),
#         Parameter('meas_time', 15, float, 'measurement time after rabi sequence (in ns)'),
#         Parameter('num_averages', 1000000, int, 'number of averages'),
#         Parameter('reset_time', 1000000, int, 'time with laser on at the beginning to reset state')
#     ]
#
#     _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}
#
#     def _function(self):
#         self.instruments['mw_gen']['instance'].update({'modulation_type': 'IQ'})
#         self.instruments['mw_gen']['instance'].update({'amplitude': self.settings['mw_power']})
#         self.instruments['mw_gen']['instance'].update({'frequency': self.settings['mw_frequency']})
#         super(Pulsed_ESR, self)._function()
#
#     def _create_pulse_sequences(self):
#         '''
#
#         Returns: pulse_sequences, num_averages, tau_list
#             pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
#             scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
#             sequence must have the same number of daq read pulses
#             num_averages: the number of times to repeat each pulse sequence
#             tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
#             meas_time: the width (in ns) of the daq measurement
#
#         '''
#         pulse_sequences = []
#         tau_list = range(int(max(15, self.settings['time_step'])), int(self.settings['time'] + 15),
#                          int(self.settings['time_step']))
#         reset_time = self.settings['reset_time']
#         for tau in tau_list:
#             pulse_sequences.append([Pulse('laser', 0, reset_time + max(tau + self.settings['meas_time'],
#                                                                        self.settings['delay_until_mw'] + self.settings[
#                                                                            'mw_duration'])),
#                                     Pulse('microwave_i', reset_time + self.settings['delay_until_mw'],
#                                           self.settings['mw_duration']),
#                                     Pulse('apd_readout', reset_time + tau, self.settings['meas_time'])
#                                     ])
#         end_time_max = 0
#         for pulse_sequence in pulse_sequences:
#             for pulse in pulse_sequence:
#                 end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
#         for pulse_sequence in pulse_sequences:
#             pulse_sequence[0] = Pulse('laser', 0, end_time_max)
#
#         return pulse_sequences, self.settings['num_averages'], tau_list, self.settings['meas_time']

class Pulsed_ESR_Pulsed_Laser(ExecutePulseBlasterSequence):
    """
This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('mw_frequency', 2.87e9, float, 'microwave frequency in Hz'),
        Parameter('delay_until_mw', 100, float, 'total time of rabi oscillations (in ns)'),
        Parameter('mw_duration', 200, float, 'total time of rabi oscillations (in ns)'),
        Parameter('time_step', 15, float,
                  'time step increment of rabi pulse duration (in ns)'),
        Parameter('time', 400, float, 'total time of rabi oscillations (in ns)'),
        Parameter('meas_time', 15, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('num_averages', 1000000, int, 'number of averages'),
        Parameter('reset_time', 1000000, int, 'time with laser on at the beginning to reset state')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}

    def _function(self):
        self.instruments['mw_gen']['instance'].update({'modulation_type': 'IQ'})
        self.instruments['mw_gen']['instance'].update({'amplitude': self.settings['mw_power']})
        self.instruments['mw_gen']['instance'].update({'frequency': self.settings['mw_frequency']})
        super(Pulsed_ESR_Pulsed_Laser, self)._function()

    def _create_pulse_sequences(self):
        '''

        Returns: pulse_sequences, num_averages, tau_list
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
            meas_time: the width (in ns) of the daq measurement

        '''
        pulse_sequences = []
        tau_list = range(int(max(15, self.settings['time_step'])), int(self.settings['time'] + 15),
                         int(self.settings['time_step']))
        reset_time = self.settings['reset_time']
        for tau in tau_list:
            if tau < self.settings['delay_until_mw']:
                pulse_sequences.append([Pulse('laser', 0, reset_time),
                                        Pulse('microwave_i', reset_time + self.settings['delay_until_mw'],
                                              self.settings['mw_duration']),
                                        Pulse('apd_readout', reset_time + tau, self.settings['meas_time'])
                                        ])
            else:
                pulse_sequences.append([Pulse('laser', 0, reset_time + max(tau + self.settings['meas_time'],
                                                                           self.settings['delay_until_mw'] +
                                                                           self.settings[
                                                                               'mw_duration'])),
                                        Pulse('microwave_i', reset_time + self.settings['delay_until_mw'],
                                              self.settings['mw_duration']),
                                        Pulse('apd_readout', reset_time + tau, self.settings['meas_time'])
                                        ])
        end_time_max = 0
        for pulse_sequence in pulse_sequences:
            for pulse in pulse_sequence:
                end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        for pulse_sequence in pulse_sequences:
            pulse_sequence[0] = Pulse('laser', 0, end_time_max)

        return pulse_sequences, self.settings['num_averages'], tau_list, self.settings['meas_time']


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

    _SCRIPTS = {'rabi':Rabi}

    def __init__(self, instruments=None, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)

    def _function(self):
        self.data = {'old_power': None, 'new_power': None, 'old_time': None, 'new_time': None, 'old_fit_params': None, 'new_fit_params': None}
        self.scripts['rabi'].run()
        power_dBm = self.scripts['rabi'].settings['mw_power']
        self.data['old_power'] = power_dBm
        rabi_tau = self.scripts['rabi'].data['tau']
        rabi_counts = self.scripts['rabi'].data['counts']
        fit_params = fit_rabi_decay(rabi_tau, rabi_counts)
        radial_freq = fit_params[1]
        self.data['old_fit_params'] = fit_params
        pi_time = 1 / (2 * (radial_freq / (2 * np.pi)))  # gives pi_time in nanoseconds
        self.data['old_time'] = pi_time
        rounded_pi_time = ((np.ceil(pi_time / 5.0) * 5.0))  # rounds up to nearest 5 ns
        self.data['new_time'] = rounded_pi_time
        power_linear = 10.0 ** (power_dBm / 10.0)
        rounded_power_linear = power_linear * (pi_time / rounded_pi_time) ** 2  # want sqrt(power)*pi_time to be constant
        rounded_power_dBm = 10.0 * np.log10(rounded_power_linear)
        self.data['new_power'] = rounded_power_dBm
        print('New Power', rounded_power_dBm)
        assert (rounded_power_dBm < -2)
        self.scripts['rabi'].settings['mw_power'] = rounded_power_dBm
        self.scripts['rabi'].run()
        rabi_counts = self.scripts['rabi'].data['counts']
        fit_params = fit_rabi_decay(rabi_tau, rabi_counts)
        radial_freq = fit_params[1]
        self.data['new_fit_params'] = fit_params
        new_pi_time = 1 / (2 * (radial_freq /(2 * np.pi)))  # gives pi_time in nanoseconds
        error = abs(new_pi_time - rounded_pi_time)
        #replace following statement with self.log
        print('new_time', rounded_pi_time)
        print('new_power', rounded_power_dBm)
        if error > self.settings['tolerance']:
            print('Optimization FAILED. Error is ' + str(error) + ' ns.')
        else:
            print('Optimization SUCCESS. Error is ' + str(error) + ' ns.')

    def _plot(self, axes_list):
        self.scripts['rabi']._plot(axes_list)
        axis = axes_list[0]
        if self.data['new_fit_params'] is not None:
            axis.plot(self.scripts['rabi'].data['tau'], self.data['new_fit_params'], 'k', lw = 3)
        elif self.data['old_fit_params'] is not None:
            axis.plot(self.scripts['rabi'].data['tau'], self.data['old_fit_params'], 'k', lw = 3)

    def _update_plot(self, axes_list):
        self.scripts['rabi']._update_plot(axes_list)
        axis = axes_list[0]
        if self.data['new_fit_params'] is not None:
            axis.plot(self.scripts['rabi'].data['tau'], self.data['new_fit_params'], 'k', lw=3)
        elif self.data['old_fit_params'] is not None:
            axis.plot(self.scripts['rabi'].data['tau'], self.data['old_fit_params'], 'k', lw=3)


class CalibrateMeasurementWindow(ExecutePulseBlasterSequence):
    """
This script find the optimal duration of the measurment window.
It applies a pi-pulse and measured the fluorescence counts after for a varying time duration.
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('mw_frequency', 2.87e9, float, 'microwave frequency in Hz'),
        Parameter('pi_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('meas_time_step', 5, [5, 10, 20, 50, 100], 'time step increment of measurement duration (in ns)'),
        Parameter('meas_time_min', 15, float, 'min time of measurement duration (in ns)'),
        Parameter('meas_time_max', 15, float, 'max time of measurement duration (in ns)'),
        Parameter('reset_time', 10000, int, 'time with laser on at the beginning to reset state'),
        Parameter('skip_invalid_sequences', False, bool, 'Skips any sequences with <15ns commands'),
        Parameter('num_averages', 100000, int, 'number of averages')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}

    def _function(self):
        self.instruments['mw_gen']['instance'].update({'modulation_type': 'IQ'})
        self.instruments['mw_gen']['instance'].update({'amplitude': self.settings['mw_power']})
        self.instruments['mw_gen']['instance'].update({'frequency': self.settings['mw_frequency']})
        super(CalibrateMeasurementWindow, self)._function()

    def _create_pulse_sequences(self):
        '''

        Returns: pulse_sequences, num_averages, tau_list
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
            meas_time: the width (in ns) of the daq measurement

        '''
        pulse_sequences = []
        tau_list = range(int(max(15, self.settings['meas_time_min'])), int(self.settings['meas_time_max'] + 15),
                         self.settings['meas_time_step'])
        reset_time = self.settings['reset_time']
        pi_pulse_time = self.settings['pi_pulse_time']
        for tau in tau_list:
            cycle_time = reset_time + pi_pulse_time + 300 + tau
            pulse_sequences.append([Pulse('laser', 0, reset_time),
                                    Pulse('microwave_i', reset_time + 200, pi_pulse_time),
                                    Pulse('laser', reset_time + pi_pulse_time + 300, tau),
                                    Pulse('apd_readout', reset_time + pi_pulse_time + 300, tau),
                                    Pulse('laser', cycle_time, reset_time),
                                    Pulse('laser', cycle_time + reset_time + pi_pulse_time + 300, tau),
                                    Pulse('apd_readout', cycle_time + reset_time + pi_pulse_time + 300, tau),
                                    ])

        end_time_max = 0
        for pulse_sequence in pulse_sequences:
            for pulse in pulse_sequence:
                end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        for pulse_sequence in pulse_sequences:
            pulse_sequence.append(Pulse('laser', end_time_max + 1850, 15))

        return pulse_sequences, self.settings['num_averages'], tau_list, max(tau_list)

    # don't normalize for this measurement
    def _normalize_to_kCounts(self, signal, gate_width=1, num_averages=1):
        return signal

    def _plot(self, axes_list):
        '''
        Plot 1: self.data['tau'], the list of times specified for a given experiment, verses self.data['counts'], the data
        received for each time
        Plot 2: the pulse sequence performed at the current time (or if plotted statically, the last pulse sequence
        performed

        Args:
            axes_list: list of axes to write plots to (uses first 2)

        '''
        [counts_0, counts_1] = zip(*self.data['counts'])
        x_data = self.data['tau']
        axis1 = axes_list[0]
        axis2 = axes_list[1]
        if not counts_0 == []:
            plot_1d_simple(axis1, x_data, [counts_0, counts_1], y_label='Counts (unnormalized)')
            contrast = (((np.array(counts_1) - np.array(counts_0)) / np.array(counts_1)) * 100).tolist()
            contrast = [x if not np.isnan(x) else 0.0 for x in
                        contrast]  # replaces nan with zeros for points not yet reached
            plot_1d_simple(axis2, x_data, [contrast], y_label='Contrast (%)')
        axis3 = axes_list[2]
        plot_pulses(axis3, self.pulse_sequences[self.sequence_index])

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
        figure1 = figure_list[0]
        figure2 = figure_list[1]
        if self._plot_refresh is True:
            figure1.clf()
            axes1 = figure1.add_subplot(211)
            axes2 = figure1.add_subplot(212)
            figure2.clf()
            axes3 = figure2.add_subplot(111)
        else:
            axes1 = figure1.axes[0]
            axes2 = figure1.axes[1]
            axes3 = figure2.axes[0]

        return [axes1, axes2, axes3]

    def _update_plot(self, axes_list):
        '''
        Updates plots specified in _plot above
        Args:
            axes_list: list of axes to write plots to (uses first 2)

        '''
        [counts_0, counts_1] = zip(*self.data['counts'])
        x_data = self.data['tau']
        axis1 = axes_list[0]
        axis2 = axes_list[1]
        if not counts_0 == []:
            update_1d_simple(axis1, x_data, [counts_0, counts_1])
            contrast = (((np.array(counts_1) - np.array(counts_0)) / np.array(counts_1)) * 100).tolist()
            contrast = [x if not np.isnan(x) else 0.0 for x in
                        contrast]  # replaces nan with zeros for points not  yet reached
            update_1d_simple(axis2, x_data, [contrast])
        axis3 = axes_list[2]
        update_pulse_plot(axis3, self.pulse_sequences[self.sequence_index])

class CPMG(ExecutePulseBlasterSequence):
    """
This script runs a CPMG pulse sequence.
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('pi_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('number_of_pulse_blocks', 1, range(1,17), 'number of alternating x-y-x-y-y-x-y-x pulses'),
        Parameter('delay_time', 5, float, 'free evolution time in between pulses (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after CPMG sequence (in ns)'),
        Parameter('number_avrgs', 1000, int, 'number of averages (should be less than a million)')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {}


    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)


    def _function(self):
        pass

    def _plot(self, axes_list, axes_colorbar=None):
        pass


    def get_axes_layout(self, figure_list):
        pass


class HahnEcho(ExecutePulseBlasterSequence):
    """
This script runs a Hahn-echo sequence for different number of pi pulses. Without pi-pulse this is a Ramsey sequence.
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('pi_half_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('number_of__pi_pulses', 0, range(0,17), 'number of pi pulses'),
        Parameter('tau', [
            Parameter('min', 15, float, 'min value for tau, the free evolution time in between pulses (in ns)'),
            Parameter('max', 30, float, 'max value for tau, the free evolution time in between pulses (in ns)'),
            Parameter('step', 5, float, 'step size for tau, the free evolution time in between pulses (in ns)'),
        ]),
        Parameter('meas_time', 300, float, 'measurement time after CPMG sequence (in ns)'),
        Parameter('number_avrgs', 1000, int, 'number of averages (should be less than a million)'),
        Parameter('reset_time', 1000, int, 'time duration of the green laser to reset the spin state'),
        Parameter('mw_delay_time', 1000, int, 'time delay  duration of the green laser to reset the spin state')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {}


    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)


    # def _function(self):
    #     pass
    #
    #
    # def _plot(self, axes_list, axes_colorbar=None):
    #     pass
    #
    #
    # def get_axes_layout(self, figure_list):
    #     pass

    def _create_pulse_sequences(self):
        '''
        creates the pulse sequence for the Hahn echo /
        Returns: pulse_sequences, num_averages, tau_list
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
            meas_time: the width (in ns) of the daq measurement

        '''
        pulse_sequences = []

        tau_list = range(int(max(15,self.settings['tau']['min'])), int(self.settings['tau']['max']),int(self.settings['tau']['step']))
        reset_time = self.settings['reset_time']
        mw_delay_time = self.settings['mw_delay_time']
        pi_half_pulse_time = self.settings['pi_half_pulse_time']
        meas_time  = self.settings['meas_time']
        number_of__pi_pulses =  self.settings['number_of__pi_pulses']

        for tau in tau_list:
            if number_of__pi_pulses == 0:
                pulse_sequences.append([Pulse('laser', 0, reset_time),
                                        Pulse('microwave_i', reset_time+ mw_delay_time, pi_half_pulse_time),
                                        Pulse('microwave_i', reset_time + mw_delay_time+ pi_half_pulse_time + tau, pi_half_pulse_time),
                                        Pulse('laser', reset_time + mw_delay_time+ pi_half_pulse_time + tau + pi_half_pulse_time, meas_time),
                                        Pulse('apd_readout', reset_time + mw_delay_time+ pi_half_pulse_time + tau + pi_half_pulse_time, meas_time)
                                        ])
            else:
                pulse_sequences.append([Pulse('laser', 0, reset_time),
                                        Pulse('microwave_i', reset_time + mw_delay_time, pi_half_pulse_time),
                                        Pulse('microwave_i', reset_time + mw_delay_time + pi_half_pulse_time + tau,2*pi_half_pulse_time),
                                        Pulse('microwave_i', reset_time + mw_delay_time + 3*pi_half_pulse_time + 2*tau,pi_half_pulse_time),
                                        Pulse('laser', reset_time + mw_delay_time + 4*pi_half_pulse_time + 2*tau, meas_time),
                                        Pulse('apd_readout',reset_time + mw_delay_time + 4*pi_half_pulse_time + 2*tau, meas_time)
                                        ])
        # TEMPORATTY: THIS IS TO SEE IF THE OVERALL TIME OF A SEQUENCE SHOULD ALWAYS BE THE SAME
        # IF WE WANT TO KEEP THIS ADD ADDITIONAL PARAMETER TO THE SCRIPT SETTINGS
        # end_time_max = 0
        # for pulse_sequence in pulse_sequences:
        #     for pulse in pulse_sequence:
        #         end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        # for pulse_sequence in pulse_sequences:
        #     pulse_sequence.append(Pulse('laser', end_time_max + 1850, 15))

        return pulse_sequences, self.settings['num_averages'], [tau], self.settings['meas_time']

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'CalibrateMeasurementWindow': 'CalibrateMeasurementWindow'}, script, instr)

    print(script)
    print('failed', failed)
    print(instr)