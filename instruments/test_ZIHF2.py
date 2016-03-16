from unittest import TestCase
from instruments import ZIHF2, Parameter, get_elemet

class TestZIHF2(TestCase):
    def test_init(self):
        test = ZIHF2()
        # test = ZIHF2('ZI inst',{'sigins': {'diff': True, 'ac': False, 'imp50': 1, 'range': 10, 'channel': 0}})
        print([p.as_dict() for p in test.parameters_default])

        # values get over-written i

        test = ZIHF2('test',[p.as_dict() for p in test.parameters_default])
        print(test)
    # def test_update(self):
    #     '''
    #     test all possible ways to update a parameter
    #     :return:
    #     '''

        # test = ZIHF2()
        # test2 = ZIHF2()
        # test.update_parameters(test2.parameters_default)
        #
        # for x1, x2 in zip(test.parameters, test2.parameters):
        #     self.assertEquals(x1.as_dict(),x2.as_dict())
        #
        # test.update_parameters({'sigins':
        #                             {'diff': False,
        #                              'ac': True,
        #                              'imp50': 1,
        #                              'range': 10,
        #                              'channel': 0}
        #                         })
        #
        # for x1, x2 in zip(test.parameters, test2.parameters):
        #     self.assertEquals(x1.as_dict(),x2.as_dict())
        #
        # test.update_parameters(Parameter('freq', 100))
        # test.update_parameters({'freq':1000.})
        #




        # self.assertEquals(
        #     get_elemet('freq',test.parameters),
        #     get_elemet('freq',test2.parameters)
        # )
        # print(test)
    def test_update2(self):
        '''
        test all possible ways to update a parameter
        :return:
        '''

        test = ZIHF2()
        test.update_parameters({'sigins':
                                    {'diff': False,
                                     'ac': True,
                                     'imp50': 1,
                                     'range': 10,
                                     'channel': 0}
                                })






        # self.assertEquals(
        #     get_elemet('freq',test.parameters),
        #     get_elemet('freq',test2.parameters)
        # )
