from unittest import TestCase
from src.instruments import NI7845RReadAnalogIO

class TestNI7845RReadAnalogIO(TestCase):
    def test_init(self):
        fpga = NI7845RReadAnalogIO()
