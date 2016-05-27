from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.scripts import GalvoScan, SetLaser
import numpy as np
import time


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
                  [Parameter('x', 0, float, 'x-coordinate'),
                   Parameter('y', 0, float, 'y-coordinate')
                   ]),
        Parameter('num_sweep_iterations', 1, int,
                  'number of times to sweep galvo (in both x and y) and find max'),
        Parameter('sweep_range', .005, float, 'voltage range to sweep over to find a max')
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'take_sweep': GalvoScan, 'set_laser': SetLaser}

    def __init__(self, scripts, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):


        Script.__init__(self, name, scripts = scripts, settings=settings, log_function=log_function, data_path = data_path)

        QThread.__init__(self)

        self._plot_type = 'aux'

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        #start x scan

        self.settings['initial_point']
        self.data['maximum_points'] = []
        self.data['maximum_points'].append([self.settings['initial_point']['x'], self.settings['initial_point']['y']])

        for i in range(self.settings['num_sweep_iterations']):
            initial_point = self.data['maximum_points'][-1]

            self.scripts['take_sweep'].update({'point_a': {'x': initial_point[0], 'y': initial_point}})
            self.scripts['take_sweep'].update({'point_b': {'x': self.settings['sweep_range'], 'y': 0}})
            self.scripts['take_sweep'].update({'RoI_mode': 'center'})
            self.scripts['take_sweep'].update({'num_points': {'x': 20, 'y': 1}})

            self.scripts['take_sweep'].run()

            self.x_sweeps = []
            self.x_sweeps.append(self.scripts['take_sweep'].data['image_data'])
            max_x_coordinate = np.argmax(self.x_sweeps[-1])
            self.data['maximum_points'].append([find_max(self.x_sweeps[-1]), self.data['maximum_points'][-1][1]])
            print self.data['x_sweeps']

            self.updateProgress.emit(50)
            time.sleep(1)

            self.scripts['take_sweep'].update({'point_a': initial_point})
            self.scripts['take_sweep'].update({'point_b': {'x': 0, 'y': self.settings['sweep_range']}})
            self.scripts['take_sweep'].update({'RoI_mode': 'center'})
            self.scripts['take_sweep'].update({'num_points': {'x': 1, 'y': 20}})

            self.scripts['take_sweep'].run()

            self.y_sweeps = []
            self.y_sweeps.append(np.array(self.scripts['take_sweep'].data['image_data']).flatten())
            print self.data['y_sweeps']


        self.updateProgress.emit(100)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

    def plot(self, axes):
        sweep_voltages = np.linspace(self.settings['sweep_range']/2.0, )
        axes.plot(np.linspace('xsweeps'[0], endpoint=True))
        axes.change_geometry(1,2,1)
        axes.set_title('hi')
        fig = axes.get_figure()
        ax = fig.add_subplot(1, 2, 2)
        ax.plot(range(0, 15))
        ax.set_title('hi2')
        fig.subplots_adjust(top=0.85)

        fig.tight_layout()

    def stop(self):
        self._abort = True

    # def save_data(self, filename = None):
    #     super(GalvoScan, self).save_data(filename)
    #     if filename is None:
    #         filename = self.filename('.jpg')
    #     # self.saveFigure.emit(filename)
