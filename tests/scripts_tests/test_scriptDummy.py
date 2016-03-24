from unittest import TestCase
from src.scripts import ScriptDummy

class TestScriptDummy(TestCase):


    def setUp(self):
        self.script = ScriptDummy()

    def test_init(self):
        # print(self.script.settings)
        self.script.run()
