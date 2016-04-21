from unittest import TestCase
from src.core import instantiate_instruments, Probe

class TestProbe(TestCase):

    def test_init(self):
        from src.core import instantiate_instruments
        instruments = {'inst_dummy': 'DummyInstrument'}

        instrument = instantiate_instruments(instruments)['inst_dummy']

        p = Probe(instrument, 'value1', 'random')

        print(instruments['inst_dummy'])

        print(p.name)
        print(p.value)
        print(p.value)
