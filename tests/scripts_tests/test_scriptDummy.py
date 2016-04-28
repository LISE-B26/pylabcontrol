from unittest import TestCase
from src.scripts import ScriptDummy, ScriptDummyWithSubScript, ScriptDummyWithInstrument
from src.instruments import DummyInstrument
class TestScriptDummy(TestCase):


    def setUp(self):
        self.script = ScriptDummy('main scripts')
        self.script_with_sub = ScriptDummyWithSubScript({'sub_script':self.script}, 'script with d')

        self.inst = DummyInstrument()
        self.script_with_inst = ScriptDummyWithInstrument({'dummy_instrument':self.inst}, 'script with inst')

    def test_init(self):
        self.script.run()


        self.script.update({'count': 10})


        self.assertEqual(self.script.settings['count'],10)

    def test_to_dict(self):

        self.assertEqual(self.script.settings,self.script.to_dict()[self.script.name]['settings'])
        s = self.script_with_sub
        print('script name', s.name)
        for key, val in s.to_dict()[s.name].iteritems():
            print(key, val)
        print('----------------------')
        print(self.inst.to_dict())

    def test_with_inst(self):
        instr = {}
        script_with_inst = ScriptDummyWithInstrument(instr)