from src.core import Parameter, Script
from PyQt4.QtCore import pyqtSlot, pyqtSignal
from copy import deepcopy
from matplotlib import patches
from src.plotting.plots_2d import plot_fluorescence_new, update_fluorescence
import random
import os
import psutil
import numpy as np
import Queue
import datetime
try:
    from src.instruments import DummyInstrument
except:
    print('WARNING script_dummy')

class ScriptMinimalDummy(Script):
    # COMMENT_ME
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.

    _DEFAULT_SETTINGS = [
        Parameter('execution_time', 0.1, float, 'execution time of script (s)')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, name=None, settings=None, log_function = None, data_path = None):
        """
        Example of a script
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_function= log_function, data_path = data_path)


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        import time
        time.sleep(self.settings['execution_time'])


class ScriptDummy(Script):
    # COMMENT_ME
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.

    _DEFAULT_SETTINGS = [
        Parameter('count', 3, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float),
        Parameter('point2',
                  [Parameter('x', 0.1, float, 'x-coordinate'),
                  Parameter('y', 0.1, float, 'y-coordinate')
                  ]),
        Parameter('plot_style', 'main', ['main', 'aux', '2D', 'two'])
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, name=None, settings=None, log_function = None, data_path = None):
        """
        Example of a script
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_function= log_function, data_path = data_path)



    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        # some generic function
        import time
        import random
        self.data['random data'] = None
        self.data['image data'] = None
        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']

        data = []
        self.log('I ({:s}) am a test function counting to {:d} and creating random values'.format(self.name, count))
        for i in range(count):
            time.sleep(wait_time)
            self.log('{:s} count {:02d}'.format(self.name, i))
            data.append(random.random())
            self.data = {'random data': data}
            self.progress = 100. * (i + 1) / count
            self.updateProgress.emit(self.progress)


        self.data = {'random data':data}


        # create image data
        Nx = int(np.sqrt(len(self.data['random data'])))
        img = np.array(self.data['random data'][0:Nx ** 2])
        img = img.reshape((Nx, Nx))
        self.data.update({'image data': img})

        # if self.settings['save']:
        #     self.save_data()
        #     self.save_b26()
        #     self.save_log()

    def _plot(self, axes_list):
        #COMMENT_ME

        plot_type = self.settings['plot_style']

        # self.log('PLOTTING {:s}'.format(plot_type))
        if plot_type in ('main', 'two'):
            if not self.data['random data'] is None:
                axes_list[0].plot(self.data['random data'])
                axes_list[0].hold(False)
        if plot_type in ('aux', 'two', '2D'):
            if not self.data['random data'] is None:
                axes_list[1].plot(self.data['random data'])
                axes_list[1].hold(False)
        if plot_type == '2D':
            if not self.data['image data'] is None:
                plot_fluorescence_new(self.data['image data'], [-1,1,1,-1], axes_list[0])


    def _update(self, axes_list):
        """
        For better performance we do not recreate image plots but rather update the data
        Args:
            axes_list:

        Returns:

        """
        plot_type = self.settings['plot_style']
        if plot_type == '2D':
            # we expect exactely one image in the axes object (see ScriptDummy.plot)
            implot = axes_list[1].get_images()[0]
            # now update the data
            implot.set_data(self.data['random data'])
            update_fluorescence(self.data['random data'], axes_list[1])

        else:
            # fall back to default behaviour
            Script._update(self, axes_list)

class ScriptDummyCounter(Script):
    """
    legacy script: now QT signals are not used anymorein scripts
    """
    _DEFAULT_SETTINGS = [
        Parameter('count', 10, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_function= log_function, data_path = data_path)

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

        self.log('I ({:s}) am a test function counting to {:d}...'.format(self.name, count))


        data = []
        for i in range(count):
            time.sleep(wait_time)
            self.progress = 100 * (i + 1) / count
            self.updateProgress.emit(self.progress)
            data.append(random.random())

        self.data = {'random data': data}

class ScriptDummyWithInstrument(Script):
    # COMMENT_ME

    _DEFAULT_SETTINGS = [
        Parameter('count', 0, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ]

    _INSTRUMENTS = {
        'dummy_instrument' : DummyInstrument
    }
    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that makes use of an instrument
        Args:
            instruments: instruments the script will make use of
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        # call init of superclass
        Script.__init__(self, name, settings, instruments, log_function= log_function, data_path = data_path)
    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in _DEFAULT_SETTINGS
        for this dummy example we just implement a counter
        """

        import time

        data = []
        # update instrument
        self.instruments['dummy_instrument'].update(self.instruments['dummy_instrument']['settings'])

        instrument = self.instruments['dummy_instrument']['instance']
        count = self.settings['count']
        name = self.settings['name']
        wait_time = self.settings['wait_time']


        self.log('I ({:s}) am a test function counting to {:d}...'.format(self.name, count))
        for i in range(count):

            self.log('signal from dummy instrument {:s}: {:0.3f}'.format(name, instrument.value1))
            time.sleep(wait_time)
            data.append(instrument.value1)

        self.data = {'data':data}
        # if self.settings['save']:
        #     self.save_data()
        #     self.save_b26()
        #     self.save_log()

class ScriptDummyWithSubScript(Script):

    _DEFAULT_SETTINGS = [
        Parameter('repetitions', 0, int, 'times the subscript will be executed')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {'sub_script':ScriptDummy, 'sub_script_instr':ScriptDummyWithInstrument,
                'sub_script_with_sign': ScriptDummyCounter}


    def __init__(self, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that makes use of an instrument
        Args:
            scripts: suscript that will be excecuted by this script
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        # call init of superclass
        Script.__init__(self, name, settings, scripts = scripts, log_function= log_function, data_path = data_path)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in _DEFAULT_SETTINGS
        for this dummy example we just implement a counter
        """
        self.counter = 0

        script = self.scripts['sub_script']

        N = self.settings['repetitions']

        data = np.zeros([self.settings['repetitions'], self.scripts['sub_script'].settings['count']])

        self.log('I ({:s}) am a test function runnning suscript {:s} {:d} times'.format(self.name, script.name, N))
        for i in range(N):
            self.log('run number {:d} / {:d}'.format(i+1, N))
            script.run()

            data[i] = deepcopy(script.data['random data'])

        self.data = {'data' : data}

        self.log('run subscript which emits signals (sub_script_with_sign)')
        self.scripts['sub_script_with_sign'].run()


    def _plot(self, axes_list):

        if self._current_subscript_stage['current_subscript'] == self.scripts['sub_script']:
            self.scripts['sub_script']._plot(axes_list)
        else:
            if 'data' in self.data:
                for data_set in self.data['data']:
                    axes_list[0].plot(data_set)
                    axes_list[0].hold(False)

class ScriptDummyWithNestedSubScript(Script):
    # COMMENT_ME

    _DEFAULT_SETTINGS = [
        Parameter('repetitions', 0, int, 'times the subscript will be executed')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {'sub_script':ScriptDummy, 'sub_sub_script':ScriptDummyWithSubScript}

    def __init__(self, scripts, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that makes use of an instrument
        Args:
            scripts: suscript that will be excecuted by this script
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        # call init of superclass
        Script.__init__(self, name, settings, scripts = scripts, log_function= log_function, data_path = data_path)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in _DEFAULT_SETTINGS
        for this dummy example we just implement a counter
        """

        import time

        script = self.scripts['sub_script']

        N = self.settings['repetitions']


        data = np.zeros([self.settings['repetitions'], self.scripts['sub_script'].settings['count']])
        self.data = {'data': data}
        self.log('I ({:s}) am a test function runnning suscript {:s} {:d} times'.format(self.name, script.name, N))
        for i in range(N):
            self.log('run number {:d} / {:d}'.format(i+1, N))
            script.run()

            data[i] = deepcopy(script.data['random data'])

        self.data = {'data' : data}
        print(' === now I am running a nested subscript ========')
        print(' ================================================')
        self.scripts['sub_sub_script'].run()

    def _plot(self, axes_list):
        if self._current_subscript_stage['current_subscript'] == self.scripts['sub_sub_script']:
            self.scripts['sub_sub_script']._plot(axes_list)
        for data_set in self.data['data']:
            axes_list[0].plot(data_set)
            axes_list[0].hold(False)

class ScriptDummyPlotMemoryTest(Script):
    # COMMENT_ME

    _DEFAULT_SETTINGS = [
        Parameter('datasize', 10, int, 'number of datapoints'),
        Parameter('repetition rate (s)', 0.1, float, 'time in between iterations'),
        Parameter('data_type', 'line', ['line', '2D'], 'data visualization mode')
    ]

    _INSTRUMENTS = {}
    _SCRIPTS = {}
    def __init__(self, scripts = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that makes use of an instrument
        Args:
            scripts: suscript that will be excecuted by this script
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        # call init of superclass
        Script.__init__(self, name, settings, scripts = scripts, log_function= log_function, data_path = data_path)

        self.data = {'data': [], 'memory': Queue.Queue(maxsize=5)}


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in _DEFAULT_SETTINGS
        for this dummy example we just implement a counter
        """
        self._abort = False
        import time
        memory = []
        timestep = self.settings['repetition rate (s)']

        while self._abort == False:
            data = [random.random() for _ in range(self.settings['datasize'])]
            # todo: use queue!!
            process = psutil.Process(os.getpid())
            memory.append(int(process.memory_info().rss))
            self.data = {'data' : data, 'memory':memory}
            self.progress = 50
            self.updateProgress.emit(self.progress)
            self.msleep(1000*timestep)


    def _plot(self, axes_list):

        if self.settings['data_type'] == 'line':
            axes_list[0].plot(self.data['data'])
            axes_list[0].hold(False)
        elif self.settings['data_type'] == '2D':
            Nx = int(np.sqrt(len(self.data['data'])))
            img = np.array(self.data['data'][0:Nx**2])
            img = img.reshape((Nx, Nx))
            plot_fluorescence_new(img, [-1,1,1,-1], axes_list[0])

        axes_list[1].plot(np.array(self.data['memory'])/1000)

    #todo: implement _plot_update
class ScriptDummySaveData(Script):
    """
This Dummy script is used to test saving of data, it takes a data set as input and save it with the internal save function of the Script class
    """

    _DEFAULT_SETTINGS = []

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, name=None, settings=None, log_function = None, data = None, data_path = None):
        """
        Example of a script
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_function= log_function, data_path = data_path)
        if data is None:
            self.data = {}
        else:
            self.data = data

    def set_data(self, data):
        self.data = data

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        if self.data == {}:
            print('no data. Please asign a data set using {:s}.set_data(data)'.format(self.name))

        else:
            self.save_data()

if __name__ == '__main__':
    import numpy as np


    s = ScriptDummyCounter()
    print(s)