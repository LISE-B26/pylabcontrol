from unittest import TestCase
from hardware_modules.instruments import Instrument, Parameter, get_elemet

class TestInstrument(TestCase):
    def test_init(self):
        '''
        initiallize instance in all possible ways
        :return:
        '''

        test = Instrument()
        test = Instrument('test inst', Parameter('test1', 2))
        test = Instrument('test inst', {'test1':0, 'test2':{'test2_1':'aa'}})

    def test_update(self):
        '''
        test all possible ways to update a parameter
        :return:
        '''

        test = Instrument()

        test.update_parameters(Parameter('test1', 10))
        test.update_parameters({'test1':0})

        new_val = 30
        test.test1 = 30
        if get_elemet('test1', test.parameters).value != test.test1:
            print(test.parameters)
            self.fail('setter function doesn\'t work')




