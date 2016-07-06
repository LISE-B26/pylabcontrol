from src.core import Parameter, Script
from src.instruments import DAQ, B26PulseBlaster, MicrowaveGenerator, Pulse
from src.scripts import ExecutePulseBlasterSequence

import numpy as np


class Rabi(ExecutePulseBlasterSequence):
    """
This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('mw_frequency', 2.87e9, float, 'microwave frequency in Hz'),
        Parameter('time_step', 5, [5, 10, 20, 50, 100, 200, 500, 1000, 10000],
                  'time step increment of rabi pulse duration (in ns)'),
        Parameter('time', 200, float, 'total time of rabi oscillations (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('num_averages', 1000000, int, 'number of averages'),
        Parameter('reset_time', 1000000, int, 'time with laser on at the beginning to reset state')
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
                                    Pulse('microwave_i', reset_time, tau),
                                    Pulse('laser', reset_time + tau + 600, self.settings['meas_time']),
                                    Pulse('apd_readout', reset_time + tau + 600, self.settings['meas_time'])
                                    ])

        end_time_max = 0
        for pulse_sequence in pulse_sequences:
            for pulse in pulse_sequence:
                end_time_max = max(end_time_max, pulse.start_time + pulse.duration)
        for pulse_sequence in pulse_sequences:
            pulse_sequence.append(Pulse('laser', end_time_max + 1850, 15))

        return pulse_sequences, self.settings['num_averages'], tau_list, self.settings['meas_time']

class Rabi_Power_Sweep(ExecutePulseBlasterSequence):
    """
This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
    """
    _DEFAULT_SETTINGS = [
        Parameter('min_mw_power', -45.0, float, 'minimum microwave power in dB'),
        Parameter('max_mw_power', -45.0, float, 'maximum microwave power in dB'),
        Parameter('mw_power_step', 1.0, float, 'power to step by in dB')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}
    _SCRIPTS = {'Rabi': Rabi}

    def _function(self):
        mw_power_values = np.arange(self.settings['min_mw_power'], self.settings['max_mw_power'],
                                    self.settings['mw_power_step'])
        for power in mw_power_values:
            self.scripts['Rabi'].settings['mw_power'] = power
            self.scripts['Rabi'].settings['tag'] = str(power) + 'dB'
            self.scripts['Rabi'].run()



class Rabi_Troubleshoot(ExecutePulseBlasterSequence):
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
        super(Rabi_Troubleshoot, self)._function()

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
            pulse_sequences.append([Pulse('laser', 0, reset_time + max(tau + self.settings['meas_time'],
                                                                       self.settings['delay_until_mw'] + self.settings[
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


class OptimizeRabi(ExecutePulseBlasterSequence):
    """
This script runs a Rabi script, fits the result to a sin wave to retrieve the Rabi oscillation frequency.
Then it increases the power of the microwave pulse such that the time for a Rabi-oscilation is a multiple of 5ns.
After that it again runs a the Rabi script with the optimized microwave power to double check.
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('time_step', 5, [5, 10, 20, 50, 100], 'time step increment of rabi pulse duration (in ns)'),
        Parameter('time', 15, float, 'total time of rabi oscillations (in ns)'),
        Parameter('measurement_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('number_avrgs', 1000, int, 'number of averages (should be less than a million)')
    ]

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {'rabi':Rabi}

    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)

    def _function(self):
        pass

    def _plot(self, axes_list, axes_colorbar=None):
        pass

    def get_axes_layout(self, figure_list):
        pass


class CalibrateMeasurementWindow(ExecutePulseBlasterSequence):
    """
This script find the optimal duration of the measurment window.
It applies a pi-pulse and measured the fluorescence counts after for a varying time duration.
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('pi_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('meas_time_step', 5, [5, 10, 20, 50, 100], 'time step increment of measurement duration (in ns)'),
        Parameter('meas_time_min', 15, float, 'min time of measurement duration (in ns)'),
        Parameter('meas_time_max', 15, float, 'max time of measurement duration (in ns)'),
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
This script runs a Hahn-echo sequence for different number of pi pulse. Without pi-pulse this is a Ramsey sequence.
    """
    _DEFAULT_SETTINGS = [
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('pi_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('number_of__pi_pulses', 1, range(1,17), 'number of pi pulses'),
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

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'Rabi': 'Rabi'}, script, instr)

    print(script)
    print('failed', failed)
    print(instr)