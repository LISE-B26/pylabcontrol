"""
    This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
    Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell


    PyLabControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyLabControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.

"""

from unittest import TestCase

from src.core import Script
from src.scripts.script_dummy import ScriptDummySaveData

class TestInstrument(TestCase):

    def test_loading_and_saving(self):
        from src.core.read_write_functions import load_b26_file

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