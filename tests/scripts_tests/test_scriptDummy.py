from unittest import TestCase
from src.scripts import ScriptDummy

class TestScriptDummy(TestCase):

    def test_init(self):
    # def setUp(self):
        self.script = ScriptDummy()
