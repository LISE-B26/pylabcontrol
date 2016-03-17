from copy import deepcopy
from unittest import TestCase

from src.core.instruments import Instrument, Parameter


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

        print(test.parameters)

        with self.assertRaises(AssertionError):
            # request variable that is not in values
            test.test4

        a = test.value1
        self.assertEqual(a, None)

    def Ttest_QString(self):
        from PyQt4 import QtCore
        test = Instrument()

        test.update_parameters(Parameter('test1', QtCore.QString(unicode('10'))))
        print('test.parameters')
        print(test.parameters)

        test.update_parameters({'test1': QtCore.QString(unicode('10'))} )
        print('test.parameters 2')
        print(test.parameters)



    def Ttest_dynamic_setter(self):
        test = Instrument()
        new_val = 30
        print(test.parameters)
        #test.test1 = 30
        test.update_parameters(Parameter('test1', 30))
        print(test.parameters)
        if get_elemet('test1', test.parameters).value != test.test1:
            #print(test.parameters)
            self.fail('setter function doesn\'t work')
    #
    # # def test_update_2(self):
    # #     '''
    # #     test all possible ways to update a parameter
    # #     :return:
    # #     '''
    # #     from PyQt4 import QtCore
    # #     test = Instrument()
    # #
    # #     test.update_parameters(Parameter('test1', QtCore.QString(unicode('10'))))
    # #     print('test.parameters')
    # #     print(test.parameters)
    # #
    # #     test.update_parameters({'test1': QtCore.QString(unicode('10'))} )
    # #     print('test.parameters 2')
    # #     print(test.parameters)
    # #
    # #     self.fail('setter ')






