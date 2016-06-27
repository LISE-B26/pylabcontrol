from src.core import Instrument, Parameter
import threading
import random, time

class DummyInstrument(Instrument):
    '''
    Dummy instrument
    a implementation of a dummy instrument
    '''

    _DEFAULT_SETTINGS = Parameter([
        Parameter('test1', 0, int, 'some int parameter'),
        Parameter('output probe2', 0, int, 'return value of probe 2 (int)'),
        Parameter('test2',
                  [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                   Parameter('test2_2', 0.0, float, 'test parameter (float)')
                   ])
    ])

    _PROBES = {'value1': 'this is some value from the instrument',
               'value2': 'this is another',
               'internal': 'gives the internal state variable',
               'deep_internal': 'gives another internal state variable'
               }

    def __init__(self, name =  None, settings = None):

        super(DummyInstrument, self).__init__(name, settings)
        self._internal_state = None
        self._internal_state_deep = None


    def update(self, settings):
        '''
        updates the internal dictionary and sends changed values to instrument
        Args:
            settings: parameters to be set
        # mabe in the future:
        # Returns: boolean that is true if update successful

        '''
        Instrument.update(self, settings)

        for key, value in settings.iteritems():
            if key == 'test1':
                self._internal_state = value



    def read_probes(self, key):
        """
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        """
        assert key in self._PROBES.keys()

        import random
        if key == 'value1':
            value = random.random()
        elif key == 'value2':
            value = self.settings['output probe2']
        elif key == 'internal':
            value = self._internal_state
        elif key == 'deep_internal':
            value = self._internal_state_deep

        return value

    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected


class DummyInstrumentThreaded(threading.Thread, Instrument):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('update frequency', 2.0, float, 'update frequency of signal in Hz'),
        Parameter('signal_range',
                  [Parameter('min', 0.0, float, 'minimum output signal (float)'),
                   Parameter('max', 0.0, float, 'maximum output signal (float)')
                   ])
    ])

    _PROBES = {'output': 'this is some random output signal (float)'
               }

    def __init__(self, name =  None, settings = None):

        threading.Thread.__init__(self)
        Instrument.__init__(self, name, settings)
        self._is_connected = True
        self.start()

    def run(self):
        dt = 1./self.settings['update frequency']
        while self._is_connected:
            self._output = random.random()
            time.sleep(dt)

    def read_probes(self, key):
        """
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        """
        assert key in self._PROBES.keys()

        if key == 'output':
            value = self._output

        return value

    @property
    def is_connected(self):
        '''
        check if instrument is active and connected and return True in that case
        :return: bool
        '''
        return self._is_connected

if __name__ == '__main__':

    d = DummyInstrumentThreaded()
    for i in range(15):
        time.sleep(0.1)
        print(d.read_probes('output'))