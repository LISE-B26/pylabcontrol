from src.scripts import ZISweeper

class ZISweeperAndSave(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('start', 1.8e6, float, 'start value of sweep'),
        Parameter('stop', 1.9e6, float, 'end value of sweep'),
        Parameter('samplecount', 101, int, 'number of data points'),
        Parameter('gridnode', 'oscs/0/freq', ['oscs/0/freq', 'oscs/1/freq'], 'output channel =not 100% sure, double check='),
        Parameter('xmapping', 0, [0, 1], 'mapping 0 = linear, 1 = logarithmic'),
        Parameter('bandwidthcontrol', 2, [2], '2 = automatic bandwidth control'),
        Parameter('scan', 0, [0, 1, 2], 'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)'),
        Parameter('loopcount', 1, int, 'number of times it sweeps'),
        Parameter('averaging/sample', 1, int, 'number of samples to average over'),
        Parameter('high_res_df', 1.0, float, 'frequency step of high res. scan'),
        Parameter('high_res_N', 10, int, 'number of data points of high res. scan'),
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'zi sweep' : ZISweeper}

    def __init__(self, zihf2, name = None, settings = None, timeout = 1000000000):
        # self._instrument = zihf2
        self._recording = False
        self._timeout = timeout

        Script.__init__(self, name, settings, {'zihf2' : zihf2})
        QThread.__init__(self)
        # self.sweeper = self._instrument.daq.sweep(self._timeout)
        # self.sweeper.set('sweep/device', self._instrument.device)

        self.sweeper = self.instruments['zihf2'].daq.sweep(self._timeout)
        self.sweeper.set('sweep/device', self.instruments['zihf2'].device)

        self.data = deque()

        # todo: clean this up! and plot data in gui!
        self._sweep_values =  {'frequency' : [], 'x' : [], 'y' : [], 'phase': [], 'r':[]}.keys()

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

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

        if self.sweeper.finished():
            self._recording = False
            progress = 100 # make sure that progess is set 1o 100 because we check that in the old_gui

            if self.settings['save']:
                self.save()