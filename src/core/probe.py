from src.core import Instrument
from collections import deque
class Probe(object):


    def __init__(self, instrument, probe_name, name = None, info = None, buffer_length = 100):
        """
        creates a probe...
        Args:
            name (optinal):  name of script, if not provided take name of function
            settings (optinal): a Parameter object that contains all the information needed in the script
        """



        assert isinstance(instrument, Instrument)
        assert isinstance(probe_name, str)
        assert probe_name in instrument._probes


        if name is None:
            name = probe_name
        assert isinstance(name, str)

        if info is None:
            info = ''
        assert isinstance(info, str)

        self.name = name
        self.info = info
        self.instrument = instrument
        self.probe_name = probe_name

        self.buffer = deque(maxlen = buffer_length)


    @property
    def value(self):
        """
        reads the value from the instrument
        """

        value = getattr(self.instrument, self.probe_name)
        self.buffer.append(value)

        return value

    def __str__(self):
        output_string = '{:s} (class type: {:s})\n'.format(self.name, self.__class__.__name__)
        return output_string
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        assert isinstance(value, str)
        self._name = value


if __name__ == '__main__':
    from src.core import load_instruments
    instruments = {'inst_dummy': 'DummyInstrument'}

    instrument = load_instruments(instruments)['inst_dummy']

    p = Probe(instrument, 'value1', 'random')

    print(instruments['inst_dummy'])

    print(p.name)
    print(p.value)
    print(p.value)



