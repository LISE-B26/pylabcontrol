from copy import deepcopy
from unittest import TestCase

from src.core import Instrument, Parameter


class TestInstrument(TestCase):
    def test_init(self):
        '''
        initiallize instance in all possible ways
        :return:
        '''


        test = Instrument()


        test = Instrument('test inst', {'test1':2020})
        self.assertEqual(test.parameters, {'test1': 2020, 'test2': {'test2_1': 'string', 'test2_2': 0.0}})
        test = Instrument('test inst', { 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
        self.assertEqual(test.parameters, {'test1': 0, 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
        print(test.parameters)

        # test = Instrument('test inst', {'test1':0, 'test2':{'test2_1':'aa'}})

    def test_update(self):
        '''
        test all possible ways to update a parameter
        :return:
        '''
        test = Instrument()

        test.parameters['test1'] = 222
        self.assertEqual(test.parameters, {'test1': 222, 'test2': {'test2_1': 'string', 'test2_2': 0.0}})

        test.parameters.update( {'test1':200})
        self.assertEqual(test.parameters, {'test1': 200, 'test2': {'test2_1': 'string', 'test2_2': 0.0}})

        test.parameters.update({ 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})

        self.assertEqual(test.parameters, {'test1': 200, 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
        print(test.parameters)

    def test_tes(self):
        test = Instrument('my inst')

        with self.assertRaises(AssertionError):
            # request variable that is not in values
            test.test4

        a = test.value1
        self.assertEqual(a, None)

    def Ttest_QString(self):
        from PyQt4 import QtCore
        test = Instrument()

        test.update_parameters(Parameter('test1', QtCore.QString(unicode('10'))))

        test.update_parameters({'test1': QtCore.QString(unicode('10'))} )



    def Ttest_dynamic_setter(self):
        test = Instrument()
        new_val = 30
        #test.test1 = 30
        test.update_parameters(Parameter('test1', 30))
        if get_elemet('test1', test.parameters).value != test.test1:
            #print(test.parameters)
            self.fail('setter function doesn\'t work')



