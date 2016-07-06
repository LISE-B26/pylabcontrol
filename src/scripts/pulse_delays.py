from src.core.scripts import Script
from src.core import Parameter
from src.instruments import Pulse
from src.scripts import ExecutePulseBlasterSequence
import numpy as np

AVERAGES_PER_SCAN = 1000000  # 1E6


class PulseDelays(ExecutePulseBlasterSequence):
    _DEFAULT_SETTINGS = [
        Parameter('count_source_pulse_width', 10000, int, 'How long to pulse the count source (in ns)'),
        Parameter('measurement_gate_pulse_width', 15, int, 'How long to have the DAQ acquire data (in ns)'),
        Parameter('min_delay', 0, int, 'minimum delay over which to scan'),
        Parameter('max_delay', 1000, int, 'maximum delay over which to scan'),
        Parameter('delay_interval_step_size', 15, int, 'Amount delay is increased for each new run'),
        Parameter('num_averages', 1000, int, 'number of times to average for each delay'),
        Parameter('reset_time', 10000, int, 'How long to wait for laser to turn off and reach steady state')
    ]

    def _create_pulse_sequences(self):
        '''
        Creates a pulse sequence with no pulses for a reset time, then the laser on for a count_source_pulse_width time.
        The daq measurement window is then swept across the laser pulse window to measure counts from min_delay
        (can be negative) to max_delay, which are both defined with the laser on at 0.

        Returns: pulse_sequences, num_averages, tau_list, measurement_gate_width
            pulse_sequences: a list of pulse sequences, each corresponding to a different time 'tau' that is to be
            scanned over. Each pulse sequence is a list of pulse objects containing the desired pulses. Each pulse
            sequence must have the same number of daq read pulses
            num_averages: the number of times to repeat each pulse sequence
            tau_list: the list of times tau, with each value corresponding to a pulse sequence in pulse_sequences
            measurement_gate_width: the width (in ns) of the daq measurement


        '''
        pulse_sequences = []
        gate_delays = range(self.settings['min_delay'], self.settings['max_delay'], self.settings['delay_interval_step_size'])
        reset_time = self.settings['reset_time']
        for delay in gate_delays:
            pulse_sequences.append([Pulse('laser', reset_time, self.settings['count_source_pulse_width']),
                                    Pulse('apd_readout', delay + reset_time,
                                           self.settings['measurement_gate_pulse_width'])
                                    ])
        return pulse_sequences, self.settings['num_averages'], gate_delays, self.settings[
            'measurement_gate_pulse_width']


if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'PulseDelays': 'PulseDelays'}, script, instr)

    print(script)
    print('failed', failed)
    print(instr)

