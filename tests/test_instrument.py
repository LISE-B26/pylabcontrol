
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

from pylabcontrol.core import Instrument, Parameter


class TestInstrument(TestCase):
    # def test_init(self):
    #     '''
    #     initiallize instance in all possible ways
    #     :return:
    #     '''
    #
    #
    #     test = Instrument()
    #
    #
    #     test = Instrument('test inst', {'test1':2020})
    #     self.assertEqual(test.settings, {'test1': 2020, 'test2': {'test2_1': 'string', 'test2_2': 0.0}})
    #     test = Instrument('test inst', { 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
    #     self.assertEqual(test.settings, {'test1': 0, 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
    #     test = Instrument('test inst', { 'test2': {'test2_1': 'new string'}})
    #     self.assertEqual(test.settings, {'test1': 0, 'test2': {'test2_1': 'new string', 'test2_2': 0.0}})
    #
    # def test_update(self):
    #     '''
    #     test all possible ways to update a parameter
    #     :return:
    #     '''
    #     test = Instrument()
    #
    #     test.settings['test1'] = 222
    #     self.assertEqual(test.settings, {'test1': 222, 'test2': {'test2_1': 'string', 'test2_2': 0.0}})
    #
    #     test.settings.update({'test1':200})
    #     self.assertEqual(test.settings, {'test1': 200, 'test2': {'test2_1': 'string', 'test2_2': 0.0}})
    #
    #     test.settings.update({'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
    #     self.assertEqual(test.settings, {'test1': 200, 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
    #
    #     test.settings['test2']['test2_1'] = 'hello'
    #     self.assertEqual(test.settings, {'test1': 200, 'test2': {'test2_1': 'hello', 'test2_2': 0.2}})
    #
    #
    #     print(test.settings['test2'])
    #
    #     print(test.settings)
    #
    #     print(type(test.settings))
    #     print(type(test.settings['test2']))
    #
    # def test_tes(self):
    #     test = Instrument('my inst')
    #
    #     with self.assertRaises(AssertionError):
    #         # request variable that is not in values
    #         test.test4
    #
    #     a = test.value1
    #     self.assertEqual(a, None)
    #
    # def Ttest_QString(self):
    #     from PyQt4 import QtCore
    #     test = Instrument()
    #
    #     test.update_parameters(Parameter('test1', QtCore.QString(unicode('10'))))
    #
    #     test.update_parameters({'test1': QtCore.QString(unicode('10'))} )
    #
    #
    #
    # def Ttest_dynamic_setter(self):
    #     test = Instrument()
    #     new_val = 30
    #     #test.test1 = 30
    #     test.update_parameters(Parameter('test1', 30))
    #     if get_elemet('test1', test.settings).value != test.test1:
    #         #print(test.parameters)
    #         self.fail('setter function doesn\'t work')

    def test_loading_and_saving(self):

        from src.core.read_write_functions import load_b26_file
        filename = "Z:\Lab\Cantilever\Measurements\\__tmp\\XX.b26"
        data = load_b26_file(filename)
        inst = {}
        instruments, instruments_failed = Instrument.load_and_append(data['instruments'], instruments=inst)

