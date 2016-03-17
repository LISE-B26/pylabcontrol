from unittest import TestCase
from src.instruments import MaestroController


class TestMaestroController(TestCase):
    def test_init(self):
        test = MaestroController()
        print(test)

