from unittest import TestCase
from src.instruments import microwave_generator as MG

class TestPiezoController(TestCase):
    def setUp(self):
        self.microwave = MG.MicrowaveGenerator('meep')

    def test_getting_internal(self):
        self.assertEqual()

    def test_setting_and_getting(self):
        self.microwave.Freq = 3000000000
        self.assertEqual(self.microwave.Freq, 3000000000) # need to round, actually ~5.1