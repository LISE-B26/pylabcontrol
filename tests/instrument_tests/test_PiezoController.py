from unittest import TestCase
from src.instruments import piezo_controller as PC
import random

class TestPiezoController(TestCase):
    def setUp(self):
        self.piezo = PC.PiezoController('meep')

    # with repeated calls to setup, can't rely on garbage collecting to trigger del, do it manually
    def tearDown(self):
        self.piezo.__del__()

    def test01_setting(self):
        #self.pos = random.randint(5,15)
        self.piezo.update({'axis': 'y'})
        self.piezo.update({'voltage': 10})
        self.assertAlmostEqual(self.piezo.voltage, 10, places=0) # need to round, actually ~5.1

    # got in previous test, but check that getter probably returns actual state and not just internal state since new
    # Piezocontroller object created for new test
    def test02_getting(self):
        self.piezo.update({'axis': 'y'})
        self.assertAlmostEqual(self.piezo.voltage, 10, places=0) # need to round, actually ~5.1

    def test03_connected(self):
        self.assertTrue(self.piezo.is_connected)