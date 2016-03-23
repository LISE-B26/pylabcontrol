from unittest import TestCase

from src.instruments import SpectrumAnalyzer


class TestSpectrumAnalyzer(TestCase):
    def setUp(self):
        self.spec_anal = SpectrumAnalyzer()

    def test_is_connected(self):
        self.assertTrue(self.spec_anal.is_connected())

    def test_start_freq_setting_and_getting(self):
        freq = 10000
        self.spec_anal.start_frequency = freq
        self.assertEqual(freq, self.spec_anal.start_frequency)

    def test_stop_freq_setting_and_getting(self):
        freq = 100000
        self.spec_anal.stop_frequency = freq
        self.assertEqual(freq, self.spec_anal.stop_frequency)

    def get_trace(self):
        print(self.spec_anal.trace)