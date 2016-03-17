from unittest import TestCase
from src.instruments import MaestroBeamBlock, MaestroController

class TestMaestroBeamBlock(TestCase):

    def test_init(self):
        maestro = MaestroController()
        print(maestro)
        test = MaestroBeamBlock(maestro)
