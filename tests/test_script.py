
# This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
#
# PyLabControl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyLabControl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.


from unittest import TestCase

from PyLabControl.src.core import Script
from PyLabControl.src.scripts.script_dummy import ScriptDummy

class TestInstrument(TestCase):

    def test_loading_and_saving(self):
        from PyLabControl.src.core.read_write_functions import load_b26_file

        filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\XYX.b26"

        scripts, loaded_failed, instruments = Script.load_and_append({"some script": 'ScriptDummyWithInstrument'})

        script = scripts['some script']
        script.save_b26(filename)

        data = load_b26_file(filename)
        scripts = {}
        instruments = {}
        scripts, scripts_failed, instruments_2 = Script.load_and_append(data['scripts'], scripts, instruments)


    def test_save_data(self):


        import numpy as np

        data = {'array-1': 2, 'array-2': 3, 'array-3': 'd'}
        name = 'arrays_0D'
        script_save = ScriptDummySaveData(name=name, settings={'tag': name}, data=data)
        script_save.run()

        data = {'array0': [0., 1., 2., 3.], 'array1': [4., 5., 6., 7.]}
        name = '1D_arrays_same_length'
        script_save = ScriptDummySaveData(name=name, settings={'tag': name}, data=data)
        script_save.run()

        data = {'array0': [0., 1., 2., 3.], 'array1': [4., 5., 6., 7., 8.]}
        name = '1D_arrays_diff_length'
        script_save = ScriptDummySaveData(name=name, settings={'tag': name}, data=data)
        script_save.run()

        data = {'array0': np.array([0., 1., 2., 3.]), 'array1': [4., 5., 6., 7., 8.]}
        name = '1D_arrays_diff_length_np'
        script_save = ScriptDummySaveData(name=name, settings={'tag': name}, data=data)
        script_save.run()

        data = {'array-0D': 2, 'array-1D': [4., 5., 6., 7., 8.], 'array-2D_np': np.array([[4., 5.], [5., 6.], [7., 8.]]),
                'array-2D': [[14., 15.], [15., 16.], [17., 18.]]}
        name = 'arrays_diff_dim'
        print(data['array-2D'], np.shape(data['array-2D']))
        script_save = ScriptDummySaveData(name=name, settings={'tag': name}, data=data)
        script_save.run()


    def test_load_and_append(self):

        # script_info = {'info': 'Enter docstring here',
        #                'scripts': {'ScriptDummy': {'info': '\nExample Script that has all different types of parameters (integer, str, fload, point, list of parameters). Plots 1D and 2D data.\n    ',
        #                                                                            'settings': {'count': 3, 'name': 'this is a counter', 'wait_time': 0.1, 'point2': {'y': 0.1, 'x': 0.1}, 'tag': 'scriptdummy', 'path': '', 'save': False, 'plot_style': 'main'},
        #                                                                            'class': 'ScriptDummy',
        #                                                                            'filepath': '/Users/rettentulla/PycharmProjects/PyLabControl/src/scripts/script_dummy.py'}},
        #                'class': 'dynamic_script_iterator0',
        #                'settings': {'script_order': {'ScriptDummy': 0},'run_all_first': True, 'script_execution_freq': {'ScriptDummy': 1}},
        #                'package': 'b26_toolkit'}
        # module, script_class_name, script_settings, script_instruments, script_sub_scripts, script_doc, package = Script.get_script_information(script_info)
        # print('module, script_class_name', module, script_class_name)
        # print('script_settings', script_settings)
        # print('script_instruments, script_sub_scripts, script_doc, package', script_instruments, script_sub_scripts, script_doc, package)

        script_dict = {'DefaultName': {'info': 'Enter docstring here', 'scripts': {'ScriptDummy': {'info': '\nExample Script that has all different types of parameters (integer, str, fload, point, list of parameters). Plots 1D and 2D data.\n    ', 'settings': {'count': 3, 'name': 'this is a counter', 'wait_time': 0.1, 'point2': {'y': 0.1, 'x': 0.1}, 'tag': 'scriptdummy', 'path': '', 'save': False, 'plot_style': 'main'}, 'class': 'ScriptDummy', 'filepath': '/Users/rettentulla/PycharmProjects/PyLabControl/src/scripts/script_dummy.py'}},
                                       'class': 'ScriptIterator', 'settings': {'script_order': {'ScriptDummy': 0},
                                                                               'iterator_type': 'Iter test'}, 'package': 'b26_toolkit'}}

        scripts = {}
        instruments = {}

        scripts, loaded_failed, instruments = Script.load_and_append(
            script_dict=script_dict,
            scripts=scripts,
            instruments=instruments, raise_errors = True)

        print('scripts', scripts)
        print('loaded_failed',loaded_failed)
        print('instruments', instruments)