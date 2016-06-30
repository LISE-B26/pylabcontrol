from src.core.scripts import Script
from src.core import Parameter
from src.instruments import Pulse
from src.scripts import ExecutePulseBlasterSequence

from PySide.QtCore import Signal, QThread
import numpy as np

AVERAGES_PER_SCAN = 1000000  # 1E6


class PulseDelays(ExecutePulseBlasterSequence):
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

    def _create_pulse_sequences(self):
        pulse_sequences = []
        gate_delays = range(self.settings['min_delay'], self.settings['max_delay'], self.settings['delay_interval_step_size'])
        reset_time = self.settings['reset_time']
        for delay in gate_delays:
            pulse_sequences.append([Pulse('laser', reset_time, self.settings['count_source_pulse_width']),
                                    Pulse('apd_readout', delay + reset_time,
                                           self.settings['measurement_gate_pulse_width'])
                                    ])
        return pulse_sequences, self.settings['num_averages'], gate_delays


if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'PulseDelays': 'PulseDelays'}, script, instr)

    print(script)
    print('failed', failed)
    print(instr)