from src.core import Parameter, Script
from PyQt4 import QtCore
from src.instruments import DummyInstrument

from PySide.QtCore import Signal, QThread

class ScriptDummy(Script):
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    # updateProgress = QtCore.Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('count', 0, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ])

    def __init__(self, name=None, settings=None):
        Script.__init__(self, name, settings)


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

        print('I am a test function counting to {:d}...'.format(count))
        for i in range(count):
            time.sleep(wait_time)
            print(i)

class ScriptDummyWithQtSignal(Script, QThread):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('count', 0, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ])

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(int)

    def __init__(self, name = None, settings = None):
        Script.__init__(self, name, settings)
        QThread.__init__(self)


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

        print('I am a test function counting to {:d}...'.format(count))



        for i in range(count):
            time.sleep(wait_time)
            progress = int(100* (i+1) / count)
            self.updateProgress.emit(progress)

            print('progress', progress)

class ScriptDummyWithInstrument(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('count', 0, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ])

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    # updateProgress = QtCore.Signal(int)

    def __init__(self, dummy_instrument,  name = None, settings = None):
        """
        Example of a script that makes use of an instrument
        Args:
            dummy_instrument:
            name:
            settings:
        """

        # check if we get the right instrument
        assert isinstance(dummy_instrument, DummyInstrument)
        # save reference to instrument
        self._instrument = dummy_instrument
        # call init of superclass
        Script.__init__(self, name, settings)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in _DEFAULT_SETTINGS
        for this dummy example we just implement a counter
        """

        import time

        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']



        print('I am a test function counting to {:d}...'.format(count))
        for i in range(count):

            print('signal from dummy instrument {:s}: {:0.3f}'.format(name, self._instrument.value1))
            time.sleep(wait_time)
