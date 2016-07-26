from unittest import TestCase

from b26_toolkit.src.instruments import SpectrumAnalyzer


class TestSpectrumAnalyzer(TestCase):
    def setUp(self):
        self.spec_anal = SpectrumAnalyzer()

    def test_is_connected(self):
        self.assertTrue(self.spec_anal.is_connected())

    def test_start_freq_setting_and_getting(self):
        freq = 10000
        self.spec_anal.start_frequency = freq
        self.assertEqual(freq, self.spec_anal.start_frequency)
        with self.assertRaises(AssertionError):
            self.spec_anal.start_frequency = -10.0
        with self.assertRaises(AssertionError):
            self.spec_anal.start_frequency = 3e10

    def test_stop_freq_setting_and_getting(self):
        freq = 100000
        self.spec_anal.stop_frequency = freq
        self.assertEqual(freq, self.spec_anal.stop_frequency)
        with self.assertRaises(AssertionError):
            self.spec_anal.stop_frequency = -10.0
        with self.assertRaises(AssertionError):
            self.spec_anal.stop_frequency = 3e10

    def test_output(self):
        self.spec_anal.mode = 'TrackingGenerator'

        self.spec_anal.output_on = False
        self.assertFalse(self.spec_anal.output_on)

        self.spec_anal.output_on = True
        self.assertTrue(self.spec_anal.output_on)

        self.spec_anal.output_power = -1.0
        self.assertEqual(self.spec_anal.output_power, -1.0)

    def get_trace(self):
        print(self.spec_anal.trace)