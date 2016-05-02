from unittest import TestCase
from src.instruments import microwave_generator as MG
import random

class TestMicrowaveGenerator(TestCase):
    def setUp(self):
        self.microwave = MG.MicrowaveGenerator('meep')

    def test_connected(self):
        self.assertEqual(self.microwave.is_connected, True)

    def test_setting_and_getting(self):
        freq = float(random.randint(2e9, 3e9))
        self.microwave.update({'frequency': freq})
        self.assertEqual(self.microwave.frequency, freq)


    def test_init(self):
        "init with settings"
        mw = MG.MicrowaveGenerator(settings={'enable_modulation': True, 'frequency': 3000000000.0, 'dev_width': 32000000.0,
                                          'pulse_modulation_function': 'External', 'phase': 0, 'port': 27,
                                          'modulation_type': 'FM', 'enable_output': False, 'GPIB_num': 0,
                                          'amplitude': -60, 'modulation_function': 'External'})
