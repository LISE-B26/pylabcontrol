from unittest import TestCase

from b26_toolkit.src.instruments import PressureGauge


class TestPressureGauge(TestCase):

    def setUp(self):
        self.gauge = PressureGauge()

    def tearDown(self):
        self.gauge.__del__()

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


    def test_read_probes(self):
        pressure = self.gauge.read_probes('pressure')
        self.assertTrue(isinstance(pressure, float) and pressure > 0)

        units = self.gauge.read_probes('units')
        possible_units = ['mbar/bar', 'Torr', 'Pascal', 'Micron']
        self.assertTrue(units in possible_units)


        model = self.gauge.read_probes('model')
        self.assertEqual(model, 'FRG70x')


