from unittest import TestCase
from copy import deepcopy
from src.core.instruments import Parameter
from PyQt4 import QtCore
class TestParameter(TestCase):



    def  test_parameter_single(self):
        # init
        p0 = Parameter('param', 0)

        self.assertEquals(p0,{'param':0})
        self.assertEquals(p0['param'],0)

        p0 = Parameter({'param':  1})

        self.assertEquals(p0,1)

        #update
        p0 = 2

        self.assertEquals(p0,2)

        p0.value = 3

        self.assertEquals(p0,3)

        p0 = {'param':  4}

        self.assertEquals(p0,4)

        with self.assertRaises(ValueError):
            p1 = Parameter('param1', 0, [0, 1, 2, 3])
            p1.value = 5


    def  test_parameter_multi(self):
        # init
        p1 = Parameter('param1', 1)
        p2 = Parameter('param2', 2)
        p0 = Parameter('param0', [p1, p2])

        self.assertEquals(p0 , {'param1':1, 'param2':2})


        #update
        p0['param1'] = 3
        self.assertEquals(p0 , {'param1':3, 'param2':2})
        self.assertEquals(p0['param1'] , 3)
        self.assertEquals(p0['param1'].value , 3)

        p0.update({'param1':4})
        self.assertEquals(p0 , {'param1':4, 'param2':2})

        p0.update(Parameter('param2', 7))
        self.assertEquals(p0 , {'param1':4, 'param2':7})

        p0.update('param2', 8)
        self.assertEquals(p0 , {'param1':4, 'param2':8})

        p0 = {'param1':5, 'param2':6}
        self.assertEquals(p0 , {'param1':5, 'param2':6})

        self.assertEquals(p0['param1'] ,5)
        self.assertEquals(p0['param2'] ,6)


        with self.assertRaises(IndexError):
            print(p0['param3'])

        with self.assertRaises(IndexError):
            p0.update({'param3', 2})

        with self.assertRaises(ValueError):
            Parameter('param', [1, p2])

        with self.assertRaises(ValueError):
            p3 = Parameter('param3', 3)

        with self.assertRaises(ValueError):
            p0.update('param2', p3)

        with self.assertRaises(ValueError):
            p0.value = [1, 2]

        with self.assertRaises(ValueError):
            px1 = Parameter('param1', [0, 1])
            px1.value = [p1, p2]

        with self.assertRaises(ValueError):
            p1 = Parameter('param1', 1)
            p2 = Parameter('param2', 2)
            p3 = Parameter('param3', 3)
            p0 = Parameter('param0', [p1, p2])

            p0.update([p1,p3])

        p1 = Parameter('param1', 1)
        p2 = Parameter('param2', 2)
        p3 = Parameter('param2', 3)
        p0 = Parameter('param0', [p1, p2])

        p0.update([p1,p3])

        p1 = Parameter('param1', [0, 1])
        p1.value = [0,1,2,3]

        self.assertEquals(p1.value, [0,1,2,3])




    def test_QString(self):
        p1 = Parameter('param1', 0)

        value_from_gui = QtCore.QString('1')

        p1.value = value_from_gui

        self.assertEquals(p1.value, 1)


        p1 = Parameter('param1', [0,1,2,3])

        value_from_gui = QtCore.QString('[1,2,3,4,5]')

        p1.value = value_from_gui

        self.assertEquals(p1.value, [1,2,3,4,5])