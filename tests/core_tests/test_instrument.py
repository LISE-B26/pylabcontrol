from copy import deepcopy
from unittest import TestCase

from src.core.instruments import Instrument, Parameter


class TestInstrument(TestCase):
    def test_init(self):
        '''
        initiallize instance in all possible ways
        :return:
        '''

        p0 = Parameter('test1', 0, int, 'test parameter (int)')
        print('p0', p0, p0.valid_values)
        p1 = Parameter('test2_1', 'string', str, 'test parameter (str)')
        print('p1', p1, p1.valid_values)
        p2 = Parameter('test2_2', 0.0, float, 'test parameter (float)')
        print('p2', p2, p2.valid_values)
        p12 = Parameter('test2', Parameter([p1,p2]))
        print('p12', p12, p12.valid_values)

        p12 = Parameter('test2', [p1,p2])
        print('p12', p12, p12.valid_values)

        # pall = Parameter([p0, p12])

        # print(pall)
        # Parameter([
        #             Parameter('test1', 0, int, 'test parameter (int)'),
        #             Parameter('test2' ,
        #                       [Parameter('test2_1', 'string', str, 'test parameter (str)'),
        #                        Parameter('test2_2', 0.0, float, 'test parameter (float)')
        #                        ])
        #         ])


        # test = Instrument()
        # print(test.as_dict())
        # test = Instrument('test inst', Parameter('test1', 2))
        # test = Instrument('test inst', {'test1':0, 'test2':{'test2_1':'aa'}})

    def tTest_update(self):
        '''
        test all possible ways to update a parameter
        :return:
        '''
        test = Instrument()
        test.update_parameters(Parameter('test1', 2))
        test.update_parameters(Parameter('test1', 10))
        test.update_parameters({'test1':1000})

        # test update of a part of a subdict
        test = Instrument()
        parameter_start = deepcopy(test.parameters)

        # we update with the original value, but only one entry
        value = get_elemet('test2',parameter_start).as_dict()['test2']['test2_1']
        test.update_parameters({'test2':{'test2_1':value}})
        parameter_end = test.parameters

        for x1, x2 in zip(parameter_start, parameter_end):
            self.assertEquals(x1,x2)

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






