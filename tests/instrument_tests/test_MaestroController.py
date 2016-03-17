from unittest import TestCase
from src.instruments.maestro import MaestroController


class TestMaestroController(TestCase):
    def test_init(self):
        test = MaestroController()
        print(test)

