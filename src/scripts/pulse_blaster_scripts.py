from src.core import Parameter, Script
from PyQt4.QtCore import pyqtSignal, QThread
from src.instruments import DAQ
from src.instruments import B26PulseBlaster, Pulse
import numpy as np


# NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
class Rabi(Script, QThread):
    """
This script applies a microwave pulse at fixed power for varying durations to measure Rabi Oscillations
    """
    _DEFAULT_SETTINGS = Parameter([
        Parameter('mw_power', -45.0, float, 'microwave power in dB'),
        Parameter('time_step', 5, [5, 10, 20, 50, 100], 'time step increment of rabi pulse duration (in ns)'),
        Parameter('time', 200, float, 'total time of rabi oscillations (in ns)'),
        Parameter('meas_time', 300, float, 'measurement time after rabi sequence (in ns)'),
        Parameter('number_avrgs', 1000000, int, 'number of averages (should be less than a million)'),
        Parameter('reset_time', 1000000, int, 'time with laser on at the beginning to reset state')
    ])

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {}
    updateProgress = pyqtSignal(int)

    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):

        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)
        QThread.__init__(self)
        
    def _function(self):
        # First point cannot be earlier than 15 ns
        gate_delays = range(max(self.settings['time_step'], 15), self.settings['time'], self.settings['time_step'])

        self.data = {'delays': gate_delays, 'counts': np.zeros(len(gate_delays))}

        def test_single_delay(num_loops, delay):
            reset_time = self.settings['reset_time']
            self.pulse_collection = [Pulse('laser', 0, reset_time),
                                     Pulse('microwave_i', reset_time, delay),
                                     Pulse('laser', delay + reset_time, self.settings['meas_time'] * 2),
                                     Pulse('apd_readout', delay + reset_time, self.settings['meas_time'])]

            self.instruments['daq']['instance'].gated_DI_init('ctr0', int(num_loops))

            self.instruments['PB']['instance'].program_pb(self.pulse_collection,
                                                          num_loops=num_loops)
            self.instruments['daq']['instance'].gated_DI_run()
            self.instruments['PB']['instance'].start_pulse_seq()
            result_array, _ = self.instruments['daq']['instance'].gated_DI_read(
                timeout=5)  # thread waits on DAQ getting the right number of gates
            # for i in range(0,99):
            #     print(result_array[i])
            # clean up APD tasks
            result = np.sum(result_array)
            self.instruments['daq']['instance'].gated_DI_stop()
            return result

        delay_data = np.zeros(len(gate_delays))

        for index, delay in enumerate(gate_delays):
            if self._abort:
                break
            delay_data[index] = delay_data[index] + test_single_delay(self.settings['numer_avrgs'], delay)
            self.data['counts'][index] = delay_data[index]
            self.updateProgress.emit(50)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

        # send 100 to signal that script is finished
        self.updateProgress.emit(100)



    def _plot(self, axes_list, axes_colorbar=None):
        pass
    def get_axes_layout(self, figure_list):
        pass
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