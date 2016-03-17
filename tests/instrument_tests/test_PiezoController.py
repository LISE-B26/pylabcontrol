from unittest import TestCase
from src.instruments import piezo_controller as PC

class TestPiezoController(TestCase):
    def setUp(self):
        self.piezo = PC.PiezoController('meep')

    # with repeated calls to setup, can't rely on garbage collecting to trigger del, do it manually
    def tearDown(self):
        self.piezo.__del__()

    def test_setting(self):
        self.piezo.axis = 'y'
        self.piezo.voltage = 5
        self.assertAlmostEqual(self.piezo.voltage, 5, places=0) # need to round, actually ~5.1

    # got in previous test, but check that getter probably returns actual state and not just internal state
    def test_getting(self):
        self.piezo.axis = 'y'
        self.assertAlmostEqual(self.piezo.voltage, 5, places=0) # need to round, actually ~5.1