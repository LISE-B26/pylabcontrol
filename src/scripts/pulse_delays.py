from src.core.scripts import Script
from src.core import Parameter
from src.instruments import DAQ, B26PulseBlaster, Pulse
from collections import deque

from PySide.QtCore import Signal, QThread
from src.plotting.plots_1d import plot_delay_counts
import numpy as np


class PulseDelays(Script, QThread):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('save', False, bool, 'Save data?'),
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

        self.data = {'counts': deque(), 'delays': deque()}

        gate_delays = range(self.settings['min_delay'], self.settings['max_delay'], self.settings['delay_interval_step_size'])

        reset_time = self.settings['reset_time']

        for delay in gate_delays:
            print('loop ' + str(delay))
            if self._abort:
                break

            #define PB pulses
            pulse_collection = [Pulse('laser', reset_time, self.settings['count_source_pulse_width']),
                                Pulse('apd_readout', delay + reset_time, self.settings['measurement_gate_pulse_width'])
                                ]

            self.instruments['daq']['instance'].gated_DI_init('ctr0', self.settings['num_averages'])
            self.instruments['PB']['instance'].program_pb(pulse_collection, num_loops=self.settings['num_averages'] + 1)
            self.instruments['daq']['instance'].gated_DI_run()
            self.instruments['PB']['instance'].start_pulse_seq()
            result_array = self.instruments['daq']['instance'].gated_DI_read(
                timeout=5)  # thread waits on DAQ getting the right number of gates
            result = np.sum(result_array)
            self.data['counts'].append(result)
            self.data['delays'].append(delay)
            # clean up APD tasks
            self.instruments['daq']['instance'].gated_DI_stop()

            self.updateProgress.emit(50)


        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

        # send 100 to signal that script is finished
        self.updateProgress.emit(100)

    def plot(self, figure_list):
        super(PulseDelays, self).plot([figure_list[0]])

    def _plot(self, axes_list):
        data = self.data['counts']
        axis = axes_list[0]
        if data:
            plot_delay_counts()

    def stop(self):
        self._abort = True

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'PulseDelays': 'PulseDelays'}, script, instr)

    print(script)
    print(failed)
    print(instr)