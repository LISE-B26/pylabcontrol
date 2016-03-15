from unittest import TestCase

from instruments import Maestro_BeamBlock, Maestro_Controller
class TestMaestro_Controller(TestCase):
    def test_init(self):
        test = Maestro_Controller()
        print(test)

