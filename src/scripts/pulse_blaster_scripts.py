from src.core import Parameter, Script
from PyQt4.QtCore import pyqtSignal, QThread
from src.instruments import DAQ, B26PulseBlaster, MicrowaveGenerator, Pulse
from src.scripts import ExecutePulseBlasterSequence


# NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
class Rabi(ExecutePulseBlasterSequence):
    """
This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
    """
    _DEFAULT_SETTINGS = Parameter([
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('time_step', 5, [5, 10, 20, 50, 100], 'time step increment of rabi pulse duration (in ns)'),
        Parameter('time', 200, float, 'total time of rabi oscillations (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('num_averages', 1000000, int, 'number of averages'),
        Parameter('reset_time', 1000000, int, 'time with laser on at the beginning to reset state')
    ])

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster, 'mw_gen': MicrowaveGenerator}

    _SCRIPTS = {}
    updateProgress = pyqtSignal(int)

    def _function(self):
        self.instruments['mw_gen']['instance'].update({'amplitude': self.settings['mw_power']})
        self.instruments['mw_gen']['instance'].update[{'modulation_type': 'IQ'}]
        super(Rabi, self)._function()

    def _create_pulse_sequences(self):
        '''

        Returns: pulse_sequences, num_averages, tau_list
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences


        '''
        pulse_sequences = []
        tau_list = range(max(15, self.settings['time_step']), self.settings['time'], self.settings['time_step'])
        reset_time = self.settings['reset_time']
        for tau in tau_list:
            pulse_sequences.append([Pulse('laser', 0, reset_time),
                                    Pulse('microwave_i', reset_time, tau),
                                    Pulse('laser', reset_time+tau, self.settings['meas_time']),
                                    Pulse('apd_readout', reset_time+tau, self.settings['meas_time'])
                                    ])
        return pulse_sequences, self.settings['num_averages'], tau_list


# NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!

class OptimizeRabi(Script, QThread):
    """
This script runs a Rabi script, fits the result to a sin wave to retrieve the Rabi oscillation frequency.
Then it increases the power of the microwave pulse such that the time for a Rabi-oscilation is a multiple of 5ns.
After that it again runs a the Rabi script with the optimized microwave power to double check.
    """
    _DEFAULT_SETTINGS = Parameter([
        # Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        # Parameter('time_step', 5, [5, 10, 20, 50, 100], 'time step increment of rabi pulse duration (in ns)'),
        # Parameter('time', 15, float, 'total time of rabi oscillations (in ns)'),
        # Parameter('measurement_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        # Parameter('number_avrgs', 1E3, int, 'number of averages (should be less than a million)')
    ])

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {'rabi':Rabi}
    updateProgress = pyqtSignal(int)

    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)
        QThread.__init__(self)

    def _function(self):
        pass

    def _plot(self, axes_list, axes_colorbar=None):
        pass

    def get_axes_layout(self, figure_list):
        pass
# NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
class CalibrateMeasurementWindow(Script, QThread):
    """
This script find the optimal duration of the measurment window.
It applies a pi-pulse and measured the fluorescence counts after for a varying time duration.
    """
    _DEFAULT_SETTINGS = Parameter([
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('pi_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('meas_time_step', 5, [5, 10, 20, 50, 100], 'time step increment of measurement duration (in ns)'),
        Parameter('meas_time_min', 15, float, 'min time of measurement duration (in ns)'),
        Parameter('meas_time_max', 15, float, 'max time of measurement duration (in ns)'),
        Parameter('number_avrgs', 1E3, int, 'number of averages (should be less than a million)')
    ])

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {}
    updateProgress = pyqtSignal(int)

    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)
        QThread.__init__(self)

    def _function(self):
        pass

    def _plot(self, axes_list, axes_colorbar=None):
        pass

    def get_axes_layout(self, figure_list):
        pass
# NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
class CPMG(Script, QThread):
    """
This script runs a CPMG pulse sequence.
    """
    _DEFAULT_SETTINGS = Parameter([
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('pi_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('number_of_pulse_blocks', 1, range(1,17), 'number of alternating x-y-x-y-y-x-y-x pulses'),
        Parameter('delay_time', 5, float, 'free evolution time in between pulses (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after CPMG sequence (in ns)'),
        Parameter('number_avrgs', 1E3, int, 'number of averages (should be less than a million)')
    ])

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {}
    updateProgress = pyqtSignal(int)


    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)
        QThread.__init__(self)


    def _function(self):
        pass


    def _plot(self, axes_list, axes_colorbar=None):
        pass


    def get_axes_layout(self, figure_list):
        pass
# NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
class HahnEcho(Script, QThread):
    """
This script runs a Hahn-echo sequence for different number of pi pulse. Without pi-pulse this is a Ramsey sequence.
    """
    _DEFAULT_SETTINGS = Parameter([
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('pi_pulse_time', 50, float, 'time duration of pi-pulse (in ns)'),
        Parameter('number_of__pi_pulses', 1, range(1,17), 'number of pi pulses'),
        Parameter('delay_time', 5, float, 'free evolution time in between pulses (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after CPMG sequence (in ns)'),
        Parameter('number_avrgs', 1E3, int, 'number of averages (should be less than a million)')
    ])

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {}
    updateProgress = pyqtSignal(int)


    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)
        QThread.__init__(self)


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