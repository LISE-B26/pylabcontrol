from src.core import Parameter, Script
from src.instruments import DAQ, B26PulseBlaster, MicrowaveGenerator, Pulse
from src.scripts.exec_pulse_blaster_sequence import ExecutePulseBlasterSequence

import numpy as np
from src.plotting.plots_1d import plot_esr, plot_pulses, update_pulse_plot, plot_1d_simple, update_1d_simple
from src.data_processing.fit_functions import fit_rabi_decay


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
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}

    def _function(self):
        #COMMENT_ME
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

    def _calc_progress(self):
        #COMMENT_ME
        # todo: change to _calc_progress(self, index):
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
        Parameter('time_step', 5, [5, 10, 20, 50, 100, 200, 500, 1000, 10000, 100000, 500000],
                  'time step increment of rabi pulse duration (in ns)'),
        Parameter('time', 200, float, 'total time of rabi oscillations (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('delay_init_mw', 0, int, 'delay between initialization and mw (in ns)'),
        Parameter('delay_mw_readout', 0, int, 'delay between mw and readout (in ns)'),
        Parameter('num_averages', 1000000, int, 'number of averages'),
        Parameter('reset_time', 10000, int, 'time with laser on at the beginning to reset state'),
        Parameter('skip_invalid_sequences', False, bool, 'Skips any sequences with <15ns commands')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}

    def _function(self):
        #COMMENT_ME
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
                                    Pulse('apd_readout', reset_time - self.settings['meas_time'],
                                          self.settings['meas_time']),
                                    Pulse('microwave_i', reset_time + self.settings['delay_init_mw'], tau),
                                    Pulse('laser', reset_time + self.settings['delay_init_mw'] + tau + self.settings[
                                        'delay_mw_readout'], self.settings['meas_time']),
                                    Pulse('apd_readout',
                                          reset_time + self.settings['delay_init_mw'] + tau + self.settings[
                                              'delay_mw_readout'], self.settings['meas_time'])
                                    ])

        end_time_max = 0
        for pulse_sequence in pulse_sequences:
            for pulse in pulse_sequence:
                end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        for pulse_sequence in pulse_sequences:
            pulse_sequence.append(Pulse('laser', end_time_max + 1850, 15))

        return pulse_sequences, self.settings['num_averages'], tau_list, self.settings['meas_time']



    #TODO: Test if the following code will add 'Rabi' as a title to main plot in GUI and add a legend
    def _plot(self, axislist):
        #COMMENT_ME
        super(Rabi, self)._plot(axislist)
        axislist[0].set_title('Rabi')
        axislist[0].legend(labels=('Ref Fluorescence', 'Rabi Data'), fontsize=8)


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
        #COMMENT_ME
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
        Parameter('mw_frequency', 2.87e9, float, 'microwave frequency in Hz'),
        Parameter('mw_switch_extra_time', 15, int, 'Time to add before and after microwave switch is turned on'),
        Parameter('pi_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('number_of_pulse_blocks', 1, range(1,17), 'number of alternating x-y-x-y-y-x-y-x pulses'),
        Parameter('delay_time_step', 5, [5, 10, 20, 50, 100, 200, 500, 1000, 10000, 100000],
                  'time step increment of time between pulses (in ns)'),
        Parameter('min_delay_time', 100, float, 'minimum time between pulses (in ns)'),
        Parameter('max_delay_time', 1000, float, 'maximum time between pulses (in ns)'),
        Parameter('delay_init_mw', 0, int, 'delay between initialization and mw (in ns)'),
        Parameter('delay_mw_readout', 0, int, 'delay between mw and readout (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after CPMG sequence (in ns)'),
        Parameter('number_avrgs', 1000, int, 'number of averages (should be less than a million)'),
        Parameter('reset_time', 10000, int, 'time with laser on at the beginning to reset state'),
        Parameter('skip_invalid_sequences', False, bool, 'Skips any sequences with <15ns commands')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}
    _SCRIPTS = {}

    def _function(self):
        self.instruments['mw_gen']['instance'].update({'modulation_type': 'IQ'})
        self.instruments['mw_gen']['instance'].update({'amplitude': self.settings['mw_power']})
        self.instruments['mw_gen']['instance'].update({'frequency': self.settings['mw_frequency']})
        super(CPMG, self)._function()

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
        tau_list = range(int(max(15, self.settings['min_delay_time'])), int(self.settings['max_delay_time'] + 15),
                         self.settings['delay_time_step'])
        reset_time = self.settings['reset_time']
        pi_time = self.settings['pi_pulse_time']
        pi_half_time = pi_time/2.0
        for tau in tau_list:

            pulse_sequence = []

            #initialize and pi/2 pulse
            pulse_sequence.extend([Pulse('laser', 0, reset_time),
                                    Pulse('apd_readout', reset_time - self.settings['meas_time'],
                                          self.settings['meas_time']),
                                   Pulse('microwave_i', reset_time + self.settings['delay_init_mw'], pi_half_time)
                                   ])

            #CPMG xyxyyxyx loops added number_of_pulse_blocks times
            section_begin_time = reset_time + self.settings['delay_init_mw'] - tau/2 #for the first pulse, only wait tau/2
            for i in range(0, self.settings['number_of_pulse_blocks']):
                pulse_sequence.extend([Pulse('microwave_i', section_begin_time + tau - pi_half_time, pi_time),
                                       Pulse('microwave_q', section_begin_time + 2*tau - pi_half_time, pi_time),
                                       Pulse('microwave_i', section_begin_time + 3*tau - pi_half_time, pi_time),
                                       Pulse('microwave_q', section_begin_time + 4*tau - pi_half_time, pi_time),
                                       Pulse('microwave_q', section_begin_time + 5*tau - pi_half_time, pi_time),
                                       Pulse('microwave_i', section_begin_time + 6*tau - pi_half_time, pi_time),
                                       Pulse('microwave_q', section_begin_time + 7*tau - pi_half_time, pi_time),
                                       Pulse('microwave_i', section_begin_time + 8*tau - pi_half_time, pi_time)
                                      ])
                section_begin_time += 8*tau

            #pi/2 and readout
            pulse_sequence.extend([Pulse('microwave_i', section_begin_time + tau/2, pi_half_time),
                                   Pulse('laser', section_begin_time + tau/2 + pi_half_time + self.settings['delay_mw_readout'], self.settings['meas_time']),
                                   Pulse('apd_readout',section_begin_time + tau / 2 + pi_half_time + self.settings['delay_mw_readout'], self.settings['meas_time'])])

            pulse_sequences.append(pulse_sequence)


        # end_time_max = 0
        # for pulse_sequence in pulse_sequences:
        #     for pulse in pulse_sequence:
        #         end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        # for pulse_sequence in pulse_sequences:
        #     pulse_sequence.append(Pulse('laser', end_time_max + 1850, 15))

        return pulse_sequences, self.settings['num_averages'], tau_list, self.settings['meas_time']

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


class T1(ExecutePulseBlasterSequence):
    """
This script measures the relaxation time of an NV center
    """
    _DEFAULT_SETTINGS = [
        Parameter('time_step', 1000, int, 'time step increment of rabi pulse duration (ns)'),
        Parameter('max_time', 200, float, 'total time of rabi oscillations (ns)'),
        Parameter('meas_time', 300, float, 'measurement time of fluorescence counts (ns)'),
        Parameter('num_averages', 1000000, int, 'number of averages'),
        Parameter('nv_reset_time', 3000, int, 'time with laser on at the beginning to reset state (ns)'),
        Parameter('ref_meas_off_time', 100, int,
                  'laser off time before taking reference measurement at the end of init (ns)'),
        Parameter('skip_invalid_sequences', True, bool, 'Skips any sequences with <15 ns commands')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    def _create_pulse_sequences(self):
        """
        Returns: pulse_sequences, num_averages, tau_list
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
            meas_time: the width (in ns) of the daq measurement

        """

        pulse_sequences = []
        if self.settings['time_step'] % 5 != 0:
            raise AttributeError('given time_step is not a multiple of 5')

        tau_list = range(0, int(self.settings['max_time'] + self.settings['time_step']), self.settings['time_step'])
        reset_time = self.settings['nv_reset_time']

        # reduce the initialization time by 15 ns to avoid touching DAQ pulses
        # (they are problematic because the DAQ expects two pulse but get only one because they get merged by the pulse blaster)
        for tau in tau_list:
            pulse_sequences.append(
                [Pulse('laser', 0, reset_time - self.settings['ref_meas_off_time'] - 15 - self.settings['meas_time']),
                 Pulse('apd_readout', reset_time - 15 - self.settings['meas_time'], self.settings['meas_time']),
                 Pulse('laser', reset_time - 15 - self.settings['meas_time'], self.settings['meas_time']),
                 Pulse('apd_readout', reset_time + tau, self.settings['meas_time']),
                 Pulse('laser', reset_time + tau, self.settings['meas_time']),
                 ])
        """
        # The following would ensure that each pulse sequence in pulse_sequences takes the same total time
        end_time_max = 0
        for pulse_sequence in pulse_sequences:
            for pulse in np.flatten(pulse_sequences):
                end_time_max = max(end_time_max, pulse.start_time + pulse.duration)

        for pulse_sequence in pulse_sequences:
            pulse_sequence.append(Pulse('laser', end_time_max + 1000, 15))

        """

        return pulse_sequences, self.settings['num_averages'], tau_list, self.settings['meas_time']

    def _plot(self, axislist):
        super(T1, self)._plot(axislist)
        axislist[0].set_title('T1')
        axislist[0].legend(labels=('T1 data', 'Ref Fluorescence'), fontsize=8)



if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'CalibrateMeasurementWindow': 'CalibrateMeasurementWindow'}, script, instr)

    print(script)
    print('failed', failed)
    print(instr)