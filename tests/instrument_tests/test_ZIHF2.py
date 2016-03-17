from unittest import TestCase

from src.instruments import ZIHF2


class TestZIHF2(TestCase):
    def test_init(self):
        test = ZIHF2('my zi')
        test = ZIHF2('my ZI', {'freq':1.})
    def test_update_request(self):

        test = ZIHF2()
        test.update({'sigins':
                                    {'diff': False,
                                     'ac': True,
                                     'imp50': 1,
                                     'range': 10,
                                     'channel': 0}
                                })

        self.assertEqual(test.parameters['sigins'], {'diff': False,
                                     'ac': True,
                                     'imp50': 1,
                                     'range': 10,
                                     'channel': 0}
                                )


        test.update({'freq':  100.})
        self.assertEqual(test.freq, 100.)

        self.assertEqual(test.freq, 100.)
        test.parameters['freq'] = 101.
