from unittest import TestCase

from b26_toolkit.src.instruments import ZIHF2
from src.scripts import ZISweeper


class TestZISweeper(TestCase):

    def test_init(self):
        zihf2 = ZIHF2()

        sweep = ZISweeper(zihf2)
