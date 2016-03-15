from unittest import TestCase

from instruments import Instrument, Parameter, get_elemet


class TestInstrument(TestCase):
    def test_init(self):
        '''
        initiallize instance in all possible ways
        :return:
        '''

        test = Instrument()
        print(test.as_dict())
        test = Instrument('test inst', Parameter('test1', 2))
        test = Instrument('test inst', {'test1':0, 'test2':{'test2_1':'aa'}})

    def test_update(self):
        '''
        test all possible ways to update a parameter
        :return:
        '''

        test = Instrument()

        test.update_parameters(Parameter('test1', 10))
        test.update_parameters({'test1':1000})

        test.update_parameters(Parameter('test1', 2))
        test.update_parameters({'test2':{'test2_1':'aa'}})

        print(test)

    def test_QString(self):
        from PyQt4 import QtCore
        test = Instrument()

        test.update_parameters(Parameter('test1', QtCore.QString(unicode('10'))))
        print('test.parameters')
        print(test.parameters)

        test.update_parameters({'test1': QtCore.QString(unicode('10'))} )
        print('test.parameters 2')
        print(test.parameters)



    def test_dynamic_setter(self):
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






