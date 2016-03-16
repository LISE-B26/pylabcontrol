from unittest import TestCase

from src.core.instruments import Parameter

class TestParameter(TestCase):

    def Ttest_init(self):
        # initiate Paremater in all possible ways
        p1 = Parameter('param', 0.0)
        p2 = Parameter('param', 0, int, 'test int')
        p3 = Parameter('param', 0.0, (int, float), 'test tupple')
        p4 = Parameter('param', 0.0, [0.0, 0.1], 'test list')

        p_nested = Parameter('param nested', p1, None, 'test list')
        p_nested = Parameter('param nested', p4, [p1,p4], 'test list')

        p_dict = Parameter({'param dict': 0 })
        p_dict_nested = Parameter({'param dict': {'sub param dict': 1 } })



    def test_update(self):
        # update Parameter
        p1 = Parameter('param', 0)
        p1.value = 0.1
        p1.value = '2'


        p1 = Parameter('param', 0)
        p2 = Parameter('param2', 2)

        p3 = Parameter('par 3', [p1, p2])
        p4 = Parameter('param4', 4)

        p3.value = p1

        p3.value = [p4,p1]



        # this should give an error
        # with self.assertRaises(TypeError):
        #     p3.value = [p4,p1]
        # # p3.value = p1
        # print(p3.value)

        # if value is a parameter, the is should also be able to accept dictionaries and cast them into parameter objects
        # p1 = Parameter('param', 0)
        # p2 = Parameter('param2', p1)
        # p4 = Parameter('param4', 4)
        # p2.value = {'param4' : 4}
        #
        #
        # print(p2)
        # self.fail()




    def Ttest_casting(self):
        '''
        test all possible ways to update a parameter
        :return:
        '''
        p1 = Parameter('param', 0)
        p2 = Parameter('param2', 2)
        p3 = Parameter('par 3', [p1, p2])

        print(p1.as_dict())
        print(p3.as_dict())
        print(p3)

        parameters = {'param1': 'value1', 'param2': 'value2'}
        parameters = [{'param1':'value1'}, {'param2':'value2'}]
        parameters = [Parameter('param1', 'value1'), Parameter('param2', 'value2')]