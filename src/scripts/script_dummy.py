from src.core import Parameter, Script

from copy import deepcopy
from matplotlib import patches
from src.plotting.plots_2d import plot_fluorescence
import random
# from PyQt4 import QtCore
import numpy as np
import os
import psutil

import Queue

try:
    from src.instruments import DummyInstrument
except:
    print('WARNING script_dummy')
# from PySide.QtCore import Signal, QThread
from PyQt4.QtCore import pyqtSignal, QThread

class ScriptDummy(Script):
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    # updateProgress = QtCore.Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:\Lab\Cantilever\Measurements\__tmp', str, 'path for data',),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', False, bool, 'save data on/off'),
        Parameter('count', 3, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float),
        Parameter('point2',
                  [Parameter('x', 0.1, float, 'x-coordinate'),
                  Parameter('y', 0.1, float, 'y-coordinate')
                  ]),
        Parameter('plot_style', 'main', ['main', 'aux', '2D', 'two'])
    ])

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
        # self._plot_type = 'main'
        self.data['random data'] = []


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


        # create image data
        Nx = int(np.sqrt(len(self.data['random data'])))
        img = np.array(self.data['random data'][0:Nx ** 2])
        img = img.reshape((Nx, Nx))
        self.data.update({'image data': img})

        if self.settings['save']:
            self.save_data()
            self.save_b26()
            self.save_log()


    def _plot(self, axes_list):

        plot_type = self.settings['plot_style']


        if plot_type == 'main':
            axes_list[0].plot(self.data['random data'])
            axes_list[0].hold(False)
        elif plot_type == 'aux':
            axes_list[1].plot(self.data['random data'])
            axes_list[1].hold(False)
            self.log('PLOTTING aux')
        elif plot_type == 'two':
            axes_list[0].plot(self.data['random data'])
            axes_list[1].plot(self.data['random data'])
            axes_list[0].hold(False)
            axes_list[1].hold(False)
            self.log('PLOTTING aux')

        elif plot_type == '2D':
            plot_fluorescence(self.data['image data'], [-1,1,1,-1], axes_list[0])
            axes_list[1].plot(self.data['random data'])

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

        else:
            # fall back to default behaviour
            Script._update(self, axes_list)

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
    updateProgress = pyqtSignal(int)
    def __init__(self, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_function= log_function, data_path = data_path)
        # QtCore.QThread.__init__(self)
        QThread.__init__(self)
        self._plot_type = 'main'


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
        Parameter('path', 'Z:\Lab\Cantilever\Measurements\__tmp', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('count', 0, int),
        Parameter('name', 'this is a counter'),
        Parameter('wait_time', 0.1, float)
    ])

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
        self._plot_type = 'main'
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


        self.log('I am a test function counting to {:d}...'.format(count))
        for i in range(count):

            self.log('signal from dummy instrument {:s}: {:0.3f}'.format(name, instrument.value1))
            time.sleep(wait_time)
            data.append(instrument.value1)

        self.data = {'data':data}
        if self.settings['save']:
            self.save_data()
            self.save_b26()
            self.save_log()


class ScriptDummyWithSubScript(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('repetitions', 0, int, 'times the subscript will be executed')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {'sub_script':ScriptDummy, 'sub_script_instr':ScriptDummyWithInstrument}

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

        print([self.settings['repetitions'], self.scripts['sub_script'].settings['count']])

        data = np.zeros([self.settings['repetitions'], self.scripts['sub_script'].settings['count']])

        self.log('I am a test function runnning suscript {:s} {:d} times'.format(script.name, N))
        for i in range(N):
            self.log('run number {:d} / {:d}'.format(i+1, N))
            script.start()
            # script.wait()

            data[i] = deepcopy(script.data['random data'])

        self.data = {'data' : data}


    def plot(self, axes):
     for data_set in self.data['data']:
         axes.plot(data_set)

class ScriptDummyWithNestedSubScript(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('repetitions', 0, int, 'times the subscript will be executed')
    ])

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

        print([self.settings['repetitions'], self.scripts['sub_script'].settings['count']])

        data = np.zeros([self.settings['repetitions'], self.scripts['sub_script'].settings['count']])

        self.log('I am a test function runnning suscript {:s} {:d} times'.format(script.name, N))
        for i in range(N):
            self.log('run number {:d} / {:d}'.format(i+1, N))
            script.start()
            # script.wait()

            data[i] = deepcopy(script.data['random data'])

        self.data = {'data' : data}


    def plot(self, axes):
     for data_set in self.data['data']:
         axes.plot(data_set)


class ScriptDummyPlotMemoryTest(Script, QThread):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('datasize', 10, int, 'number of datapoints'),
        Parameter('repetition rate (s)', 0.1, float, 'time in between iterations'),
        Parameter('data_type', 'line', ['line', '2D'], 'data visualization mode')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {}
    updateProgress = pyqtSignal(int)
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

        QThread.__init__(self)
        self._plot_type = 'two'
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
            self.updateProgress.emit(50)
            self.msleep(1000*timestep)
            # print(memory)



        self.updateProgress.emit(100)

    def stop(self):
        self._abort = True
    def get_axes_layout(self, figure_data, figure_memory):
        """
        returns the axes objects the script needs to plot its data
        """

        figure_data.clf()
        axes1 = figure_data.add_subplot(111)
        figure_memory.clf()
        axes2 = figure_memory.add_subplot(111)

        return axes1, axes2

    def plot(self, figure_memory, figure_data):
        axes_data, axes_memory = self.get_axes_layout(figure_data, figure_memory)

        if self.settings['data_type'] == 'line':
            axes_data.plot(self.data['data'])
        elif self.settings['data_type'] == '2D':
            Nx = int(np.sqrt(len(self.data['data'])))
            img = np.array(self.data['data'][0:Nx**2])
            img = img.reshape((Nx, Nx))
            # print(img)
            plot_fluorescence(img, [-1,1,1,-1], axes_data)

        axes_memory.plot(np.array(self.data['memory'])/1000)

class ScriptDummySaveData(Script):
    """
This Dummy script is used to test saving of data, it takes a data set as input and save it with the internal save function of the Script class
    """

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:\Lab\Cantilever\Measurements\__tmp', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data')
    ])

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

class ScriptDummyPlotting(Script, QThread):
    """
This Dummy script is used to test saving of data, it takes a data set as input and save it with the internal save function of the Script class
    """
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:\Lab\Cantilever\Measurements\__tmp', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('plotting_mode', 0, int, 'Which plots to display')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    updateProgress = pyqtSignal(int)

    def __init__(self, name=None, settings=None, log_function=None, data=None, data_path=None):
        """
        Example of a script
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings, log_function=log_function, data_path=data_path)
        QThread.__init__(self)
        if data is None:
            self.data = {}
        else:
            self.data = data
        self._plot_type = 'two'

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        if self.settings['plotting_mode'] == 0:
            self._plot_type = 'two'
            print('two')
        elif self.settings['plotting_mode'] == 1:
            self._plot_type = 'aux'
            print('aux')
        elif self.settings['plotting_mode'] == 2:
            self._plot_type = 'main'
            print('main')
        elif self.settings['plotting_mode'] == 3:
            self._plot_type = 'aux'
            print('aux')

        self.updateProgress.emit(100)

    def plot(self, figure1, figure2 = None):
        if self.settings['plotting_mode'] == 0:
            axes1, axes2, axes3 = self.get_axes_layout(figure1, figure2)
            print('plotting_0')
            image = np.random.rand(120,120)
            plot_fluorescence(image, [-1,1,1,-1], axes1)

            plot1 = np.random.rand(100)
            plot2 = np.random.rand(100)
            axes2.plot(plot1)
            axes3.plot(plot2)
            axes2.set_title('meep')
            axes2.set_xlabel('tick')
            axes2.set_ylabel('tock')
            axes3.set_title('meep')
            axes3.set_xlabel('tick')
            axes3.set_ylabel('tock')

            figure1.tight_layout()
            figure2.tight_layout()

            self.settings['plotting_mode'] = 2

        elif self.settings['plotting_mode'] == 1:
            print('plotting_1')
            axes = super(ScriptDummyPlotting, self).get_axes_layout(figure1)
            image = np.random.rand(120,120)
            plot_fluorescence(image, [-1,1,1,-1], axes)
            figure1.tight_layout()

        elif self.settings['plotting_mode'] == 2:
            print('plotting_2')
            patch = patches.Circle((0,0), .1, fc='r', alpha=.75)
            figure1.axes[0].add_patch(patch)

        elif self.settings['plotting_mode'] == 3:
            print('plotting_3')
            axes1 = super(ScriptDummyPlotting, self).get_axes_layout(figure1)
            plot = np.random.rand(100)
            axes1.plot(plot)
            axes1.set_title('meep')
            axes1.set_xlabel('tick')
            axes1.set_ylabel('tock')
            figure1.tight_layout()

        elif self.settings['plotting_mode'] ==  10:
            print('plotting_4')

    def get_axes_layout(self, figure1, figure2):
        if self.settings['plotting_mode'] == 0:
            figure1.clf()
            axes1 = figure1.add_subplot(111)

            figure2.clf()
            axes2 = figure2.add_subplot(121)
            axes3 = figure2.add_subplot(122)

            return axes1, axes2, axes3

        elif self.settings['plotting_mode'] == 1:
            return Script.get_axes_layout(figure1)

        elif self.settings['plotting_mode'] == 3:
            return Script.get_axes_layout(figure1)

        else:
            pass


if __name__ == '__main__':
    import numpy as np


    s = ScriptDummyWithQtSignal()
    print(s)