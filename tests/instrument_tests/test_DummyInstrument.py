from unittest import TestCase

from src.core import Parameter
from src.instruments import DummyInstrument


class TestInstrument(TestCase):
    def test_init(self):
        '''
        initiallize instance in all possible ways
        :return:
        '''


        test = DummyInstrument()


        test = DummyInstrument('test inst', {'test1':2020})
        self.assertEqual(test.parameters, {'test1': 2020, 'test2': {'test2_1': 'string', 'test2_2': 0.0}, 'output probe2': 0})
        test = DummyInstrument('test inst', { 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
        self.assertEqual(test.parameters, {'test1': 0, 'test2': {'test2_1': 'new string', 'test2_2': 0.2}, 'output probe2': 0})
        test = DummyInstrument('test inst', { 'test2': {'test2_1': 'new string'}})
        self.assertEqual(test.parameters, {'test1': 0, 'test2': {'test2_1': 'new string', 'test2_2': 0.0}, 'output probe2': 0})

    def test_update(self):
        '''
        test all possible ways to update a parameter
        :return:
        '''
        test = DummyInstrument()

        test.parameters['test1'] = 222
        self.assertEqual(test.parameters, {'test1': 222, 'test2': {'test2_1': 'string', 'test2_2': 0.0}, 'output probe2': 0})

        test.parameters.update( {'test1':200})
        self.assertEqual(test.parameters, {'test1': 200, 'test2': {'test2_1': 'string', 'test2_2': 0.0}, 'output probe2': 0})

        test.parameters.update({ 'test2': {'test2_1': 'new string', 'test2_2': 0.2}})
        self.assertEqual(test.parameters, {'test1': 200, 'test2': {'test2_1': 'new string', 'test2_2': 0.2}, 'output probe2': 0})

        test.parameters['test2']['test2_1'] = 'hello'
        self.assertEqual(test.parameters, {'test1': 200, 'test2': {'test2_1': 'hello', 'test2_2': 0.2}, 'output probe2': 0})


        print(test.parameters['test2'])

        print(test.parameters)

        print(type(test.parameters))
        print(type(test.parameters['test2']))

    def test_tes(self):
        test = DummyInstrument('my inst')

        with self.assertRaises(AssertionError):
            # request variable that is not in values
            test.test4

        a = test.value1
        self.assertIsInstance(a, float)

        # test1 parameter sets the internal state variable
        test.test1 = 9
        self.assertEqual(9, test._internal_state)


        test._internal_state = 11
        self.assertEqual(11, test.internal)

        # following tests are still failing to update internal state
        test.parameters.update({'test1':8})
        self.assertEqual(test.parameters, {'test1': 8, 'test2': {'test2_1': 'string', 'test2_2': 0.0}, 'output probe2': 0})
        self.assertEqual(8, test._internal_state)
        print(test._internal_state)

        test.parameters['test1'] = 10
        self.assertEqual(test.parameters, {'test1': 10, 'test2': {'test2_1': 'string', 'test2_2': 0.0}, 'output probe2': 0})
        print(test.parameters)
        self.assertEqual(10, test._internal_state)
