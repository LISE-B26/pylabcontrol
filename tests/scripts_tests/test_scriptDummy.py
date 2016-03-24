from unittest import TestCase
from src.scripts import ScriptDummy

class TestScriptDummy(TestCase):


    def setUp(self):
        self.script = ScriptDummy()

    def test_init(self):
        # print(self.script.settings)
        self.script.run()


        self.script.update({'count': 10})


        self.assertEqual(self.script.settings, {'count': 10, 'wait_time': 0.1, 'name': 'this is a counter'})
        print(self.script.settings)
