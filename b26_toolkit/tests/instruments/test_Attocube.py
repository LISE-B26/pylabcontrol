import random
from unittest import TestCase

from b26_toolkit.src.instruments import attocube as AC


class TestPiezoController(TestCase):
    def setUp(self):
        self.attocube = AC.Attocube('meep')

    def test01_connected(self):
        self.assertTrue(self.attocube.is_connected)

    def test02_setting(self):
        voltage = random.randint(5,15)
        self.attocube.update({'x': {'voltage': voltage}})
        self.assertEqual(self.attocube.x_voltage, voltage) # need to round, actually ~5.1

    def test03_getting(self):
        self.assertFalse(self.attocube.z_cap == 0) # need to round, actually ~5.1