
# This file is part of pylabcontrol, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
#
# pylabcontrol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pylabcontrol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pylabcontrol.  If not, see <http://www.gnu.org/licenses/>.


from unittest import TestCase

from pylabcontrol.core import Script, Instrument
from pylabcontrol.scripts.example_scripts import ExampleScript

class TestInstrument(TestCase):


    def test_loading_and_saving(self):
        from pylabcontrol.core.read_write_functions import load_b26_file

        filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\XYX.b26"

        scripts, loaded_failed, instruments = Script.load_and_append({"some script": 'ScriptDummyWithInstrument'})

        script = scripts['some script']
        script.save_b26(filename)

        data = load_b26_file(filename)
        scripts = {}
        instruments = {}
        scripts, scripts_failed, instruments_2 = Script.load_and_append(data['scripts'], scripts, instruments)


    def test_load_and_append(self):

        filepath = 'C:\\Users\\Experiment\\PycharmProjects\\pylabcontrol\\pylabcontrol\\scripts\\example_scripts.py'
        script_dict = {'DefaultName': {'info': 'Enter docstring here', 'scripts': {'ScriptDummy': {'info': '\nExample Script that has all different types of parameters (integer, str, fload, point, list of parameters). Plots 1D and 2D data.\n    ',
                                                                                                   'settings': {'count': 3, 'name': 'this is a counter', 'wait_time': 0.1, 'point2': {'y': 0.1, 'x': 0.1}, 'tag': 'scriptdummy', 'path': '', 'save': False, 'plot_style': 'main'},
                                                                                                   'class': 'ScriptDummy',
                                                                                                   'filepath': filepath}},
                                       'class': 'ScriptIterator',
                                       'settings': {'script_order': {'ScriptDummy': 0},
                                        'iterator_type': 'Loop'},
                                       'package': 'b26_toolkit'}}

        scripts = {}
        instruments = {}

        scripts, loaded_failed, instruments = Script.load_and_append(
            script_dict=script_dict,
            scripts=scripts,
            instruments=instruments, raise_errors = True)

        print(('scripts', scripts))
        print(('loaded_failed',loaded_failed))
        print(('instruments', instruments))
        print('----x')
        print((scripts['DefaultName'].__class__.__name__))

        print('----x')
        print((scripts['DefaultName'].__class__.__name__.split('.')[0], script_dict['DefaultName']['package']))
        assert scripts['DefaultName'].__class__.__name__.split('.')[0] == script_dict['DefaultName']['package']


        print((type(scripts['DefaultName'].__module__)))


        module, script_class_name, script_settings, script_instruments, script_sub_scripts, script_doc, package = Script.get_script_information(
            script_dict['DefaultName'])


        print(module)
        print(script_class_name)

    def test_get_module_1(self):
        filepath = 'C:\\Users\\Experiment\\PycharmProjects\\pylabcontrol\\pylabcontrol\\scripts\\example_scripts.py'
        print(' ===== start test_get_module_1 =======')
        script_info ={'info': 'Enter docstring here', 'scripts': {'ScriptDummy': {'info': '\nExample Script that has all different types of parameters (integer, str, fload, point, list of parameters). Plots 1D and 2D data.\n    ', 'settings': {'count': 3, 'name': 'this is a counter', 'wait_time': 0.1, 'point2': {'y': 0.1, 'x': 0.1}, 'tag': 'scriptdummy', 'path': '', 'save': False, 'plot_style': 'main'}, 'class': 'ScriptDummy',
                                                                                  'filepath': filepath}},
                                       'class': 'ScriptIterator', 'settings': {'script_order': {'ScriptDummy': 0},
                                                                               'iterator_type': 'Iter test'}, 'package': 'b26_toolkit'}



        module, script_class_name, script_settings, script_instruments, script_sub_scripts, script_doc, package = Script.get_script_information(
            script_info)

        print(('script_class_name', script_class_name))
        print(('module', module))
        print(('package', package))
        assert script_class_name == 'ScriptIterator'

        print(' ===== end test_get_module_1 ========')

    def test_load_and_append_from_file(self):

        from pylabcontrol.core.read_write_functions import load_b26_file
        filename = 'C:\\Users\Experiment\PycharmProjects\\user_data\pythonlab_config_lev_test.b26'


        in_data = load_b26_file(filename)

        instruments = in_data['instruments'] if 'instruments' in in_data else {}
        scripts = in_data['scripts'] if 'scripts' in in_data else {}
        probes = in_data['probes'] if 'probes' in in_data else {}

        script_info = list(scripts.values())[0]

        module, script_class_name, script_settings, script_instruments, script_sub_scripts, script_doc, package = Script.get_script_information(script_info)

        print(('module', module.__name__.split('.')[0]))
        print(('script_class_name', script_class_name))

        print(('package', script_info['package']))
        assert module.__name__.split('.')[0] == script_info['package']



        instruments_loaded, failed = Instrument.load_and_append(instruments)
        if len(failed) > 0:
            print(('WARNING! Following instruments could not be loaded: ', failed))
        print('========================================================================\n\n')
        scripts_loaded, failed, instruments_loaded = Script.load_and_append(
            script_dict=scripts,
            instruments=instruments_loaded)