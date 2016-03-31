from src.core import Parameter, Script
# from PyQt4 import QtCore
from src.instruments import DummyInstrument
# from PyQt4 import QtCore
from PySide.QtCore import Signal, QThread

class ScriptDummy(Script):
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    # updateProgress = QtCore.Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'C:\Users\Experiment\Desktop\\tmp_data', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('count', 0, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, name=None, settings=None, log_output = None):
        """
        Example of a script
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_output = log_output)


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time
        import random

        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']

        data = []
        self.log('I am a test function counting to {:d} and creating random values'.format(count))
        for i in range(count):
            time.sleep(wait_time)
            self.log('count {:02d}'.format(i))
            data.append(random.random())

        self.data = {'random data':data}

        if self.settings['save']:
            self.save()

# class ScriptDummyWithQtSignal(Script, QtCore.QThread):
class ScriptDummyWithQtSignal(Script, QThread):
    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('count', 10, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(int)
    def __init__(self, name = None, settings = None, log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_output = log_output)
        # QtCore.QThread.__init__(self)
        QThread.__init__(self)


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time
        import random

        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']

        self.log('I am a test function counting to {:d}...'.format(count))


        data = []
        for i in range(count):
            time.sleep(wait_time)
            progress = int(100* (i+1) / count)
            self.updateProgress.emit(progress)

            data.append(random.random())

        self.data = {'random data': data}

class ScriptDummyWithInstrument(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('count', 0, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ])

    _INSTRUMENTS = {
        'dummy_instrument' : DummyInstrument
    }
    _SCRIPTS = {}

    def __init__(self, instruments,  name = None, settings = None, log_output = None):
        """
        Example of a script that makes use of an instrument
        Args:
            instruments: instruments the script will make use of
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        # call init of superclass
        Script.__init__(self, name, settings, instruments, log_output = log_output)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in _DEFAULT_SETTINGS
        for this dummy example we just implement a counter
        """

        import time

        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']


        self.log('I am a test function counting to {:d}...'.format(count))
        for i in range(count):

            self.log('signal from dummy instrument {:s}: {:0.3f}'.format(name, self.instruments['dummy_instrument'].value1))
            time.sleep(wait_time)



class ScriptDummyWithSubScript(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('repetitions', 0, int, 'times the subscript will be executed')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {'sub_script':ScriptDummy}

    def __init__(self, scripts,  name = None, settings = None, log_output = None):
        """
        Example of a script that makes use of an instrument
        Args:
            scripts: suscript that will be excecuted by this script
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        # call init of superclass
        Script.__init__(self, name, settings, scripts = scripts, log_output = log_output)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in _DEFAULT_SETTINGS
        for this dummy example we just implement a counter
        """

        import time

        script = self.scripts['sub_script']

        N = self.settings['repetitions']

        self.log('I am a test function runnning suscript {:s} {:d} times'.format(script.name, N))
        for i in range(N):
            self.log('run number {:d} / {:d}'.format(i+1, N))
            script.run()