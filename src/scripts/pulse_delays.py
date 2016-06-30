from src.core.scripts import Script
from src.core import Parameter
from src.instruments import DAQ, B26PulseBlaster, Pulse
from collections import deque

from PySide.QtCore import Signal, QThread
from src.plotting.plots_1d import plot_delay_counts, plot_pulses, update_pulse_plot
import numpy as np


class PulseDelays(Script, QThread):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('save', False, bool, 'Save data?'),
        Parameter('path', '', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('count_source_pulse_width', 10000, int, 'How long to pulse the count source (in ns)'),
        Parameter('measurement_gate_pulse_width', 15, int, 'How long to have the DAQ acquire data (in ns)'),
        Parameter('min_delay', 0, int, 'minimum delay over which to scan'),
        Parameter('max_delay', 1000, int, 'maximum delay over which to scan'),
        Parameter('delay_interval_step_size', 15, int, 'Amount delay is increased for each new run'),
        Parameter('num_averages', 1000, int, 'number of times to average for each delay'),
        Parameter('reset_time', 10000, int, 'How long to wait for laser to turn off and reach steady state')
    ])

    _INSTRUMENTS = {'daq': DAQ, 'PB': B26PulseBlaster}

    _SCRIPTS = {}
    updateProgress = Signal(int)

    def __init__(self, instruments, scripts=None, name=None, settings=None, log_function=None, data_path=None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings=settings, scripts=scripts, instruments=instruments,
                        log_function=log_function, data_path=data_path)
        QThread.__init__(self)
        count_source = 'laser'
        measurement_gate = 'apd_readout'

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self._abort = False

        gate_delays = range(self.settings['min_delay'], self.settings['max_delay'], self.settings['delay_interval_step_size'])

        self.data = {'counts': [], 'delays': gate_delays}

        reset_time = self.settings['reset_time']

        total_time = self.settings['measurement_gate_pulse_width'] * self.settings['num_averages']
        normalization = 10E6 / total_time

        (num_1E6_avg_pb_programs, remainder) = divmod(self.settings['num_averages'], 1E6)

        delay_data = np.zeros(len(gate_delays))

        def test_single_delay(num_loops, delay):
            self.pulse_collection = [Pulse('laser', reset_time, self.settings['count_source_pulse_width']),
                                     Pulse('apd_readout', delay + reset_time,
                                           self.settings['measurement_gate_pulse_width'])
                                     ]

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

            self.pulse_collection = [Pulse('laser', reset_time, self.settings['count_source_pulse_width']),
                                     Pulse('apd_readout', delay + reset_time,
                                           self.settings['measurement_gate_pulse_width'])
                                     ]
            # self.updateProgress.emit(int(99 * (index + 1.0) / len(gate_delays)))
            self.updateProgress.emit(50)
            return result

        for average_loop in range(int(num_1E6_avg_pb_programs)):
            print('loop ' + str(average_loop))
            if self._abort:
                break

            for index, delay in enumerate(gate_delays):
                delay_data[index] = delay_data[index] + (test_single_delay(1E6, delay))
                self.data['counts'] = delay_data

        if remainder != 0:
            for index, delay in enumerate(gate_delays):
                delay_data[index] = delay_data[index] + test_single_delay(remainder, delay)
                self.data['counts'] = delay_data

        self.updateProgress.emit(50)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

        # send 100 to signal that script is finished
        self.updateProgress.emit(100)

    def _plot(self, axes_list):
        counts = self.data['counts']
        delays = self.data['delays']
        axis1 = axes_list[0]
        if not counts == []:
            plot_delay_counts(axis1, delays, counts)
        axis2 = axes_list[1]
        plot_pulses(axis2, self.pulse_collection)

    def _update_plot(self, axes_list):
        counts = self.data['counts']
        delays = self.data['delays']
        axis1 = axes_list[0]
        if not counts == []:
            plot_delay_counts(axis1, delays, counts)
        axis2 = axes_list[1]
        update_pulse_plot(axis2, self.pulse_collection)


    def stop(self):
        self._abort = True

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'PulseDelays': 'PulseDelays'}, script, instr)

    print(script)
    print(failed)
    print(instr)