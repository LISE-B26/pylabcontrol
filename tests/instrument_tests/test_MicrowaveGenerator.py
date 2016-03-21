from unittest import TestCase
from src.instruments import microwave_generator as MG

class TestPiezoController(TestCase):
    def setUp(self):
        self.microwave = MG.MicrowaveGenerator('meep')

    def test_connected(self):
        self.assertEqual(self.microwave.is_connected, True)

    def test_setting_and_getting(self):
        self.microwave.update({'FREQ': 2870000000.0})
        self.assertEqual(self.microwave.FREQ, 2.87e9)