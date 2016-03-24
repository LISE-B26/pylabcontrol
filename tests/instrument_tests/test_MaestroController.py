from unittest import TestCase
from src.instruments import MaestroController


class TestMaestroController(TestCase):
    def test_init(self):
        test = MaestroController()

        print(test.settings)


        print(test)

        print(test.is_connected)

        test.set_target(0,1000)

