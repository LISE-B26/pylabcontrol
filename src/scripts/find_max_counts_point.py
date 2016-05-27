from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.scripts import GalvoScan, SetLaser


class FindMaxCounts(Script, QThread):
    """
    GalvoScan uses the apd, daq, and galvo to sweep across voltages while counting photons at each voltage,
    resulting in an image in the current field of view of the objective.
    """
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('initial_point',
                  [Parameter('x', -0.4, float, 'x-coordinate'),
                   Parameter('y', -0.4, float, 'y-coordinate')
                   ]),
        Parameter('num_sweep_iterations', 2, int,
                  'number of times to sweep galvo (in both x and y) and find max'),
        Parameter('sweep_range', .005, float, 'voltage range to sweep over to find a max')
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'take_image': GalvoScan, 'set_laser': SetLaser}

    def __init__(self, instruments, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):


        Script.__init__(self, name, settings=settings, instruments=instruments, log_function=log_function, data_path = data_path)

        QThread.__init__(self)

        self._plot_type = 'aux'

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        #start x scan
        self.scripts['set_laser']

        initial_point = self.settings['initial_point']

        self.scripts['take_image']['point_a'] = initial_point
        self.scripts['take_image']['point_b'] = [self.settings['sweep_range'], 0]
        self.scripts['take_image']['RoI_mode'] = 'center'
        self.scripts['take_image']['num_points'] = [20, 0]

        self.scripts['take_image'].run()

        self.data['x_sweeps'] = []
        self.data['x_sweeps'].append(self.scripts['take_image'].data['image_data'])
        print self.data['x_sweeps']

        self.updateProgress(100)

        if self.settings['save']:
            self.save()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

    def plot(self, axes):
        pass


    def stop(self):
        self._abort = True

    # def save_data(self, filename = None):
    #     super(GalvoScan, self).save_data(filename)
    #     if filename is None:
    #         filename = self.filename('.jpg')
    #     # self.saveFigure.emit(filename)
