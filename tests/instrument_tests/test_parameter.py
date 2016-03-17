from unittest import TestCase
from copy import deepcopy
from src.core.instruments import Parameter
from PyQt4 import QtCore
class TestParameter(TestCase):



    def  test_parameter_single(self):
        # init

        p0 = Parameter('param', 0, int, 'integer')
        p0 = Parameter('param', 0.0, float, 'float')
        p0 = Parameter('param', '0', str, 'string')
        p0 = Parameter('param', 0, [0,1,2,3], 'list')


        p0 = Parameter('param', 0)
        self.assertEqual(p0.valid_values['param'], int)
        p0 = Parameter('param', 0.0)
        self.assertEqual(p0.valid_values['param'], float)
        p0 = Parameter('param', '0')
        self.assertEqual(p0.valid_values['param'], str)
        p0 = Parameter('param', [0,1,2,3])
        self.assertEqual(p0.valid_values['param'], list)


        p0 = Parameter('param', 0, int, 'integer')
        self.assertEquals(p0,{'param':0})
        self.assertEquals(p0['param'],0)

        p0 = Parameter({'param':  1})
        self.assertEquals(p0,{'param':1})

        #update

        p0.update({'param':2})
        self.assertEquals(p0,{'param':2})


        with self.assertRaises(AssertionError):
            Parameter('param1', 0, [ 1, 2, 3])

        with self.assertRaises(AssertionError):
            Parameter('pa',2.2, int, 'type is int but value is float!')


        p0 = Parameter('param', [0,1,2,3])
        p0.update({'param':[0,5]})

        with self.assertRaises(AssertionError):
            p0.update({'param':0})


    def  test_parameter_multi(self):


        # init
        p1 = Parameter('param1', 1)
        p2 = Parameter('param2', 2)
        p0 = Parameter('param0', [p1, p2])

        self.assertEquals(p0 , {'param0': {'param1':1, 'param2':2}})


        #update
        p0['param0'] = {'param1':3}
        self.assertEquals(p0 , {'param0': {'param1':3, 'param2':2}})
        self.assertEquals(p0['param0'] , {'param1':3, 'param2':2})
        self.assertEquals(p0['param0']['param1'] , 3)

        with self.assertRaises(KeyError):
            p0.update({'param1':4})


        p0['param0'].update(Parameter('param2', 7))
        self.assertEquals(p0['param0'], {'param1':3, 'param2':7})

        p0['param0'].update({'param2': 8})
        self.assertEquals(p0['param0'] , {'param1':3, 'param2':8})

        p0['param0'] = {'param1':5, 'param2':6}
        self.assertEquals(p0['param0'] , {'param1':5, 'param2':6})

        self.assertEquals(p0['param0']['param1'] ,5)
        self.assertEquals(p0['param0']['param2'] ,6)


        with self.assertRaises(KeyError):
            print(p0['param3'])


        p1 = Parameter('param1', 1)
        p2 = Parameter('param2', 2)
        p0 = Parameter('param0', [p1, p2])

        with self.assertRaises(AssertionError):
            p0['param0'] = [0,1] # asign list of different type



            p1 = Parameter('param1', 1)
            p2 = Parameter('param2', 2)
            p3 = Parameter('param2', 3)
            p0 = Parameter('param0', [p1, p2])


            p0['param0'] = [p1,p3]


        with self.assertRaises(AssertionError):
            p1 = Parameter('param1', 1)
            p2 = Parameter('param2', 2)
            p3 = Parameter('param3', 3)
            p0 = Parameter('param0', [p1, p2])

            p0['param0'] = [p1,p3]



        with self.assertRaises(AssertionError):
            p1 = Parameter('param1', 1)
            p2 = Parameter('param2', 2)
            p3 = Parameter('param2', 's')
            p0 = Parameter('param0', [p1, p2])

            p0['param0'] = [p1,p3]


    def  test_parameter_multi_v2(self):
        '''
        test for next generation parameter object
        Args:
            self:

        Returns:

        '''



        p0 = Parameter({'p1' : 1, 'p2' : 2})

        with self.assertRaises(KeyError):
            p0['param0'].update({'param3': 2})

        p0 = Parameter('p0', 0)
        with self.assertRaises(ValueError):
            Parameter('param', [1, p0]) # list values that are of a different type

        p1 = Parameter('p1', [1,2]) # list values
        with self.assertRaises(ValueError):
            p1['p1'] =  [1, p0] # list values that are of a different type

        with self.assertRaises(ValueError):
            p3 = Parameter('param3', 3)

    # def test_QString(self):
    #     p1 = Parameter('param1', 0)
    #
    #     value_from_gui = QtCore.QString('1')
    #
    #     p1.value = value_from_gui
    #
    #     self.assertEquals(p1.value, 1)
    #
    #
    #     p1 = Parameter('param1', [0,1,2,3])
    #
    #     value_from_gui = QtCore.QString('[1,2,3,4,5]')
    #
    #     p1.value = value_from_gui
    #
    #     self.assertEquals(p1.value, [1,2,3,4,5])