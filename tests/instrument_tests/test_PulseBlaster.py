from unittest import TestCase
from src.instruments import B26PulseBlaster
from collections import namedtuple


class TestPulseBlaster(TestCase):

    def setUp(self):
        self.pb = B26PulseBlaster()

        self.Pulse = namedtuple('Pulse', ('instrument_name', 'start_time', 'duration'))

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

        self.pb.update({'laser': {'delay_time': delay['laser']},
                        'microwave_switch': {'delay_time': delay['microwave_switch']},
                        'microwave_p': {'delay_time': delay['microwave_p']},
                        'apd_readout':{'delay_time': delay['apd_readout']},
                        'microwave_q':{'delay_time': delay['microwave_q']}})

        global_shift = 500

        physical_pulse_seq = self.pb.create_physical_pulse_seq(self.pulses)

        for ideal_pulse, physical_pulse in zip(self.pulses, physical_pulse_seq):
            self.assertEqual(ideal_pulse.start_time - delay[ideal_pulse.instrument_name] + global_shift,
                             physical_pulse.start_time)


