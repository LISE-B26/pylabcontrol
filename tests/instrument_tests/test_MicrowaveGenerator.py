from unittest import TestCase
from src.instruments import microwave_generator as MG
import random

class TestMicrowaveGenerator(TestCase):
    def setUp(self):
        self.microwave = MG.MicrowaveGenerator('meep')

    def test_connected(self):
        self.assertEqual(self.microwave.is_connected, True)

    def test_setting_and_getting(self):
        freq = random.randint(2e9, 3e9)
        self.microwave.update({'FREQ': freq})
        self.assertEqual(self.microwave.FREQ, freq)