from src.core import Script, Parameter
from PyQt4 import QtCore
from PySide.QtCore import Signal, QThread
import time
from collections import deque
from src.instruments import ZIHF2
import numpy as np
from src.core import plotting


class ZISweeper(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('start', 1.8e6, float, 'start value of sweep'),
        Parameter('stop', 1.9e6, float, 'end value of sweep'),
        Parameter('samplecount', 101, int, 'number of data points'),
        Parameter('gridnode', 'oscs/0/freq', ['oscs/0/freq', 'oscs/1/freq'], 'output channel =not 100% sure, double check='),
        Parameter('xmapping', 0, [0, 1], 'mapping 0 = linear, 1 = logarithmic'),
        Parameter('bandwidthcontrol', 2, [2], '2 = automatic bandwidth control'),
        Parameter('scan', 0, [0, 1, 2], 'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)'),
        Parameter('loopcount', 1, int, 'number of times it sweeps'),
        Parameter('averaging/sample', 1, int, 'number of samples to average over')

    ])

    _INSTRUMENTS = {'zihf2' : ZIHF2}

    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None, timeout = 1000000000):

        self._recording = False
        self._timeout = timeout

        Script.__init__(self, name, settings, instruments)
        QThread.__init__(self)
        # self.sweeper = self._instrument.daq.sweep(self._timeout)
        # self.sweeper.set('sweep/device', self._instrument.device)

        self.sweeper = self.instruments['zihf2'].daq.sweep(self._timeout)
        self.sweeper.set('sweep/device', self.instruments['zihf2'].device)

        self.data = deque()

        # todo: clean this up! and plot data in gui!
        self._sweep_values =  {'frequency' : [], 'x' : [], 'y' : [], 'phase': [], 'r':[]}.keys()


    def settings_to_commands(self, settings):
        '''
        converts dictionary to list of  setting, which can then be passed to the zi controler
        :param dictionary = dictionary that contains the commands
        :return: commands = list of commands, which can then be passed to the zi controler
        '''
        # create list that is passed to the ZI controler

        commands = []
        for key, val in settings.iteritems():
            if isinstance(val, dict) and 'value' in val:
                commands.append(['sweep/%s' % (key), val['value']])
            elif key in ('start', 'stop', 'samplecount', 'gridnode', 'xmapping',
                         'bandwidthcontrol', 'scan', 'loopcount', 'averaging/sample'):
                commands.append(['sweep/%s' % (key), val])
        return commands


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self.data.clear() # clear data queue
        commands = self.settings_to_commands(self.settings)

        self.sweeper.set(commands)

        path = '/%s/demods/%d/sample' % (self.instruments['zihf2'].device, self.instruments['zihf2'].settings['demods']['channel'])
        self.sweeper.subscribe(path)
        self.sweeper.execute()
        print('=>> SWEEPER SETTINGS', self.settings)
        while not self.sweeper.finished():
            time.sleep(1)
            progress = int(100*self.sweeper.progress())
            print('progress', progress)
            data = self.sweeper.read(True)# True: flattened dictionary

            #  ensures that first point has completed before attempting to read data
            if path not in data:
                continue

            data = data[path][0][0] # the data is nested, we remove the outer brackets with [0][0]
            # now we only want a subset of the data porvided by ZI
            data = {k : data[k] for k in self._sweep_values}

            start = time.time()
            self.data.append(data)

            if (time.time() - start) > self._timeout:
                # If for some reason the sweep is blocking, force the end of the
                # measurement
                print("\nSweep still not finished, forcing finish...")
                self.sweeper.finish()
                self._recording = False

            print("Individual sweep %.2f%% complete. \n" % (progress))

            self.updateProgress.emit(progress)
            print('len data: ',len(self.data))
        if self.sweeper.finished():
            self._recording = False
            progress = 100 # make sure that progess is set 1o 100 because we check that in the old_gui

            if self.settings['save']:
                self.save()


    def plot(self, axes):

        r = self.data[-1]['r']
        freq = self.data[-1]['frequency']
        freq = freq[np.isfinite(r)]
        r = r[np.isfinite(r)]
        plotting.plot_psd(freq, r,axes)

if __name__ == '__main__':
    from src.instruments import ZIHF2
    import time

    zihf2 = ZIHF2()

    sweep = ZISweeper(zihf2)

    sweep.start()

    time.sleep(0.3)

    print(sweep.sweeper.progress())

    time.sleep(0.3)

    sweep.stop()



