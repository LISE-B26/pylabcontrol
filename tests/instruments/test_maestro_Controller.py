from unittest import TestCase

from src.core.instruments import Maestro_Controller
class TestMaestro_Controller(TestCase):
    def test_init(self):
        test = Maestro_Controller()
        print(test)

