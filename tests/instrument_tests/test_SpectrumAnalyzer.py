from unittest import TestCase

from src.instruments import SpectrumAnalyzer


class TestSpectrumAnalyzer(TestCase):
    def setUp(self):
        self.spec_anal = SpectrumAnalyzer()

    def test_default_params(self):
        default_params = self.spec_anal._parameters_default
        self.assertEqual(len(default_params), 3)

    def test_is_connected(self):
        self.assertTrue(self.spec_anal.is_connected())

    def test_start_freq_setting(self):
        self.spec_anal.start_frequency = 1e9