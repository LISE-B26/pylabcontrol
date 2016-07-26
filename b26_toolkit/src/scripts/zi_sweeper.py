from collections import deque

import numpy as np

from b26_toolkit.src.plotting import plotting
from src.core import Script, Parameter


class ZISweeper(Script):
    """
This script performs a frequency sweep with the Zurich Instrument HF2 Series Lock-in amplifier
    """
    _DEFAULT_SETTINGS = [
        Parameter('start', 1.8e6, float, 'start value of sweep'),
        Parameter('stop', 1.9e6, float, 'end value of sweep'),
        Parameter('samplecount', 101, int, 'number of data points'),
        Parameter('gridnode', 'oscs/0/freq', ['oscs/0/freq', 'oscs/1/freq'], 'output channel =not 100% sure, double check='),
        Parameter('xmapping', 0, [0, 1], 'mapping 0 = linear, 1 = logarithmic'),
        Parameter('bandwidthcontrol', 2, [2], '2 = automatic bandwidth control'),
        Parameter('scan', 0, [0, 1, 2], 'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)'),
        Parameter('loopcount', 1, int, 'number of times it sweeps'),
        Parameter('averaging/sample', 1, int, 'number of samples to average over')
    ]

    _INSTRUMENTS = {'zihf2' : ZIHF2}

    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):

        self._recording = False
        self._timeout = timeout

        Script.__init__(self, name, settings, instruments, log_function= log_function, data_path = data_path)

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

            # if self.settings['save']:
            #     self.save_b26()
            #     self.save_data()
            #     self.save_log()


    def _plot(self, axes_list):
        #COMMENT_ME
        axes = axes_list[0]

        r = self.data[-1]['r']
        freq = self.data[-1]['frequency']
        freq = freq[np.isfinite(r)]
        r = r[np.isfinite(r)]
        plotting.plot_psd(freq, r, axes)

if __name__ == '__main__':
    from b26_toolkit.src.instruments import ZIHF2
    import time

    zihf2 = ZIHF2()

    sweep = ZISweeper(zihf2)

    sweep.start()

    time.sleep(0.3)

    print(sweep.sweeper.progress())

    time.sleep(0.3)

    sweep.stop()



