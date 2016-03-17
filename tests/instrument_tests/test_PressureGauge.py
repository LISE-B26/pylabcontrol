from unittest import TestCase

from src.instruments import PressureGauge


class TestAGC100(TestCase):

    def setUp(self):
        self.gauge = PressureGauge()

    def tearDown(self):
        self.gauge.__del__()

    def test_parameters_default(self):
        param_list = self.gauge.parameters_default
        self.assertTrue(len(param_list) == 3)  # only has 2 parameters

    def test_get_pressure(self):
        pressure = self.gauge.pressure
        self.assertTrue(isinstance(pressure, float) and pressure > 0)

    def test_get_gauge_model(self):
        model = self.gauge.model
        self.assertEqual(model, 'FRG70x')

    def test_get_units(self):
        units = self.gauge.units
        possible_units = ['mbar/bar', 'Torr', 'Pascal', 'Micron']
        self.assertTrue(units in possible_units)

    def test_is_connected(self):
        self.assertTrue(self.gauge.is_connected())

    def test_probe_list(self):
        probes = self.gauge.PROBES
        self.assertEqual(probes, ['pressure', 'units'])