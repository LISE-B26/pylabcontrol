from src.core import Parameter, Script
from PyQt4 import QtCore
from src.instruments import DummyInstrument

class ScriptDummy(Script):
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(int)

    def __init__(self, name = None, settings = None):
        super(ScriptDummy, self).__init__(name, settings)

    @property
    def _settings_default(self):
        '''
        returns the default settings of the script
        settings contain Parameters, Instruments and Scripts
        :return:
        '''
        settings_default = Parameter([
            Parameter('count', 0, int),
            Parameter('name', 'this is a counter'),
            Parameter('wait_time', 0.1, float)
        ])
        return settings_default

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time

        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']

        print('I am a test function counting to {:i}...'.format(count))
        for i in range(count):
            time.sleep(wait_time)
            print(i)


class ScriptDummyWithInstrument(Script):
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(int)

    def __init__(self, dummy_instrument,  name = None, settings = None):

        assert isinstance(dummy_instrument, DummyInstrument)

        self._instrument = dummy_instrument
        super(ScriptDummy, self).__init__(name, settings)

    @property
    def _settings_default(self):
        '''
        returns the default settings of the script
        settings contain Parameters, Instruments and Scripts
        :return:
        '''
        settings_default = Parameter([
            Parameter('count', 0, int),
            Parameter('name', 'this is a counter'),
            Parameter('wait_time', 0.1, float)
        ])
        return settings_default

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time

        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']



        print('I am a test function counting to {:i}...'.format(count))
        for i in range(count):
            self._instrument.
            'output probe2'

            time.sleep(wait_time)
            print(i)