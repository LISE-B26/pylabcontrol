from src.core import Instrument, Parameter



class DummyInstrument(Instrument):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('test1', 0, int, 'some int parameter'),
        Parameter('output probe2', 0, int, 'return value of probe 2 (int)'),
        Parameter('test2',
                  [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                   Parameter('test2_2', 0.0, float, 'test parameter (float)')
                   ])
    ])

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


    @property
    def _probes(self):
        """

        Returns: a dictionary that contains the values that can be read from the instrument
        the key is the name of the value and the value of the dictionary is an info

        """
        return {'value1': 'this is some value from the instrument',
                'value2': 'this is another',
                'internal' : 'gives the internal state variable',
                'deep_internal' : 'gives another internal state variable'
                }

    def read_probes(self, key):
        """
        requestes value from the instrument and returns it
        Args:
            key: name of requested value

        Returns: reads values from instrument

        """
        assert key in self._probes.keys()

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


if __name__ == '__main__':


    test = DummyInstrument()
    print(test.test1)
    print(test._settings)