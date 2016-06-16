from unittest import TestCase
from src.instruments import B26PulseBlaster
from collections import namedtuple
from src.core import Pulse
import numpy as np


class TestPulseBlaster(TestCase):

    def setUp(self):
        self.pb = B26PulseBlaster()

        self.Pulse = namedtuple('Pulse', ('channel_id', 'start_time', 'duration'))

        self.pulses = [self.Pulse('laser', 0, 1E3),
                       self.Pulse('microwave_switch', 1.5E3, 100),
                       self.Pulse('microwave_p', 1.5E3, 100),
                       self.Pulse('microwave_switch', 1750, 100),
                       self.Pulse('microwave_q', 1750, 100),
                       self.Pulse('laser', 2E3, 1E3),
                       self.Pulse('apd_readout', 2E3, 10)]

    def tearDown(self):
        pass

    def test_adding_delays(self):
        delay = {}
        delay['laser'] = 500
        delay['microwave_switch'] = 10
        delay['microwave_p'] = 10
        delay['apd_readout'] = 15
        delay['microwave_q'] = 10

        def test_delays(delay, pulses):
            self.pb.update({'laser': {'delay_time': delay['laser']},
                            'microwave_switch': {'delay_time': delay['microwave_switch']},
                            'microwave_p': {'delay_time': delay['microwave_p']},
                            'apd_readout':{'delay_time': delay['apd_readout']},
                            'microwave_q':{'delay_time': delay['microwave_q']}})

            previous_start_time = np.min([pulse.start_time for pulse in pulses])
            earliest_pulse_time = np.min([pulse.start_time - delay[pulse.channel_id] for pulse in pulses])
            global_shift = -1.0 * np.min([0, earliest_pulse_time]) + previous_start_time

            physical_pulse_seq = self.pb.create_physical_pulse_seq(pulses)

            for ideal_pulse, physical_pulse in zip(pulses, physical_pulse_seq):
                self.assertEqual(ideal_pulse.start_time - delay[ideal_pulse.channel_id] + global_shift,
                                 physical_pulse.start_time)


        test_delays(delay, self.pulses)

        for i in range(10):
            num_pulses = 12
            pulses = []
            instrument_choices = ['laser', 'microwave_switch', 'microwave_q', 'microwave_p', 'apd_readout']
            while len(pulses) < num_pulses:
                new_pulse = self.Pulse(np.random.choice(instrument_choices), np.random.randint(0,2000), np.random.randint(0,2000))

                pulses.append(new_pulse)

            for instrument in instrument_choices:
                delay[instrument] = np.random.randint(0,2000)

            test_delays(delay, pulses)

    def test_overlapping_pulses_finding(self):
        self.assertFalse(B26PulseBlaster.find_overlapping_pulses(self.pulses))

        pulses = [self.Pulse('laser', 0, 1E3),
                  self.Pulse('microwave_switch', 1.5E3, 100),
                  self.Pulse('microwave_p', 1.5E3, 100),
                  self.Pulse('microwave_switch', 1750, 100),
                  self.Pulse('microwave_q', 1750, 100),
                  self.Pulse('laser', 0.5E3, 1E3),
                  self.Pulse('apd_readout', 2E3, 10)]

        self.assertEqual(B26PulseBlaster.find_overlapping_pulses(pulses), [(pulses[0], pulses[5])])

        for i in range(10):
            num_pulses = 12
            pulses = []
            instrument_choices = ['laser', 'microwave_switch', 'microwave_q', 'microwave_p', 'apd_readout']
            for j in range(num_pulses):
                new_pulse = self.Pulse(channel_id=np.random.choice(instrument_choices),
                                       start_time=np.random.randint(0, 2000),
                                       duration=np.random.randint(0, 2000))

                pulses.append(new_pulse)

            overlapping_pulses = B26PulseBlaster.find_overlapping_pulses(pulses)
            if len(overlapping_pulses) > 0:
                for pulse_1, pulse_2 in overlapping_pulses:
                    self.assertTrue(pulse_1 in pulses)
                    self.assertTrue(pulse_2 in pulses)
                    self.assertTrue(pulse_1.start_time < pulse_2.start_time + pulse_2.duration)
                    self.assertTrue(pulse_2.start_time < pulse_1.start_time + pulse_1.duration)
