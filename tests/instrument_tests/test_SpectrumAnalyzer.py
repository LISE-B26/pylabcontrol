from unittest import TestCase

from src.instruments import SpectrumAnalyzer


class TestAGC100(TestCase):
    def setUp(self):
        spec_anal = SpectrumAnalyzer()

    def test_default_params(self):