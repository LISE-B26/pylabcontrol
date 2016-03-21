from unittest import TestCase
from src.instruments import attocube as AC

class TestPiezoController(TestCase):
    def setUp(self):
        self.attocube = AC.Attocube('meep')

    def test01_connected(self):
        self.assertTrue(self.attocube.is_connected)

    def test02_setting(self):
        self.attocube.update({'x': {'voltage': 10}})
        self.assertEqual(self.attocube.x_voltage, 10) # need to round, actually ~5.1

    # got in previous test, but check that getter probably returns actual state and not just internal state
    def test03_getting(self):
        self.assertFalse(self.attocube.z_cap == 0) # need to round, actually ~5.1