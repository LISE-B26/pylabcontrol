from unittest import TestCase

from src.core import Instrument, Parameter, Script


class TestInstrument(TestCase):

    def test_loading_and_saving(self):
        from src.core.read_write_functions import load_b26_file

        filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\XYX.b26"

        scripts, loaded_failed, instruments = Script.load_and_append({"some script": 'ScriptDummyWithInstrument'})

        script = scripts['some script']
        script.save(filename)

        data = load_b26_file(filename)
        scripts = {}
        instruments = {}
        scripts, scripts_failed, instruments_2 = Script.load_and_append(data['scripts'], scripts, instruments)
