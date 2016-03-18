from unittest import TestCase

from src.core import Instrument, Parameter, Script_new


class TestInstrument(TestCase):
    def test_init(self):
        '''
        initiallize instance in all possible ways
        :return:
        '''


        test = Script_new()

        print(test)

        test.run()

        #
        #
        # test = Instrument('test inst', {'test1':2020})
        # self.assertEqual(test.parameters, {'test1': 2020, 'test2': {'test2_1': 'string', 'test2_2': 0.0}})
        # test = Instrument('test inst', { 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
        # self.assertEqual(test.parameters, {'test1': 0, 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
        # test = Instrument('test inst', { 'test2': {'test2_1': 'new string'}})
        # self.assertEqual(test.parameters, {'test1': 0, 'test2': {'test2_1': 'new string', 'test2_2': 0.0}})
