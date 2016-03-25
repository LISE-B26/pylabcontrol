from unittest import TestCase
from src.scripts import ZISweeper
from src.instruments import ZIHF2
class TestZISweeper(TestCase):

    def test_init(self):
        zihf2 = ZIHF2()

        sweep = ZISweeper(zihf2)
