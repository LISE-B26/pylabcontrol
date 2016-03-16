from unittest import TestCase

from src.instruments import PressureGauge


class TestAGC100(TestCase):
    def test_parameters_default(self):
        param_list = self.gauge.parameters_default()
        self.assertTrue(len(param_list) == 2) # only has 2 parameters

    def test_get_pressure(self):
        self.fail()

    def test_get_gauge_model(self):
        self.fail()

    def test_get_units(self):
        self.fail()

    def test_is_connected(self):
        self.fail()

    def setUp(self):
        self.gauge = PressureGauge()