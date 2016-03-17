from unittest import TestCase

from src.instruments import SpectrumAnalyzer


class TestAGC100(TestCase):
    def setUp(self):
        spec_anal = SpectrumAnalyzer()

    def test_default_params(self):
        default_params = self.spec_analyzer.parameters_default
        self.assertEqual(len(default_params), 3)

    def test_is_connected(self):
        self.assertTrue(self.spec_anal.is_connected())