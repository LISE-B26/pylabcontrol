from unittest import TestCase
from src.instruments import dcservo_kinesis_dll as DC

class TestTDC001(TestCase):
    def setUp(self):
        self.servo = DC.TDC001()

    def tearDown(self):
        self.servo.__del__()

    def test_connect(self):
        self.assertEquals(self.servo.is_connected, True)

    def test_move(self):
        self.servo.goto_home()
        self.servo.update({'position': 3})
        self.assertAlmostEqual(self.servo.position, 3, places=0)

    def test_vel(self):
        self.servo.update({'velocity': 2.5})
        self.assertEquals(self.servo.velocity, 2.5)