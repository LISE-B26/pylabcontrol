from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.scripts import GalvoScan, SetLaser
from src.data_processing.fit_functions import fit_gaussian
import numpy as np
import time


class FindMaxCounts(Script, QThread):
    """
GalvoScan uses the apd, daq, and galvo to sweep across voltages while counting photons at each voltage,
resulting in an image in the current field of view of the objective.

Known issues:
    1.) if fits are poor, check  sweep_range. It should extend significantly beyond end of NV on both sides.
    """
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', False, bool,'check to automatically save data'),
        Parameter('initial_point',
                  [Parameter('x', 0, float, 'x-coordinate'),
                   Parameter('y', 0, float, 'y-coordinate')
                   ]),
        Parameter('num_sweep_iterations', 1, int,
                  'number of times to sweep galvo (in both x and y) and find max'),
        Parameter('sweep_range', .02, float, 'voltage range to sweep over to find a max'),
        Parameter('num_points', 20, int, 'number of points to sweep in the sweep range')
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'take_sweep': GalvoScan, 'set_laser': SetLaser}

    def __init__(self, scripts, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):


        Script.__init__(self, name, scripts = scripts, settings=settings, log_function=log_function, data_path = data_path)

        QThread.__init__(self)

        self._plot_type = 'aux'

        self.scripts['take_sweep'].settings['time_per_pt'] = .01

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        #start x scan

        self._abort = False

        self.data = {'maximum_points': [], 'sweep_domain': [], 'sweep': []}
        self.data['maximum_points'].append([self.settings['initial_point']['x'], self.settings['initial_point']['y']])

        self.x_sweeps = []
        self.x_sweep_domains = []
        self.y_sweeps = []
        self.y_sweep_domains = []

        for iteration in range(self.settings['num_sweep_iterations']):

            if self._abort:
                self.log('Leaving focusing loop')
                break

            initial_point = self.data['maximum_points'][-1]

            # self.scripts['take_sweep'].update({'point_a': {'x': initial_point[0], 'y': initial_point[1]}})
            self.scripts['take_sweep'].settings['point_a'].update({'x': initial_point[0], 'y': initial_point[1]})
            self.scripts['take_sweep'].settings['point_b'].update({'x': self.settings['sweep_range'], 'y': 0})
            self.scripts['take_sweep'].update({'RoI_mode': 'center'})
            self.scripts['take_sweep'].settings['num_points'].update({'x': self.settings['num_points'], 'y': 1})
            print('points', {'x': initial_point[0], 'y': initial_point[1]}, {'x': self.settings['sweep_range'], 'y': 0})

            self.scripts['take_sweep'].run()

            self.x_sweeps.append(np.array(self.scripts['take_sweep'].data['image_data']).flatten())
            self.x_sweep_domains.append(np.linspace(initial_point[0] - self.settings['sweep_range'] / 2.0,
                                                    initial_point[0] + self.settings['sweep_range'] / 2.0,
                                                    self.settings['num_points'], endpoint=True))

            guess_noise = min(self.x_sweeps[-1])
            guess_amp = max(self.x_sweeps[-1]) - guess_noise
            reasonable_fit_params = [guess_noise, guess_amp, initial_point[0], .002]

            self.fit_params_x = [-1,-1,-1,-1]
            try:
                # self.fit_params_x = fit_gaussian(self.x_sweep_domains[-1], self.x_sweeps[-1], reasonable_fit_params,
                #                           bounds=([0, [np.inf, np.inf, 100., 100.]]))
                self.fit_params_x = fit_gaussian(self.x_sweep_domains[-1], self.x_sweeps[-1])
                print('rfp', reasonable_fit_params)
                print('fp', self.fit_params_x)
                max_x_coordinate = self.fit_params_x[2]
                assert((max_x_coordinate > min(self.x_sweep_domains[-1])) and (max_x_coordinate < max(self.x_sweep_domains[-1])))
                self.data['maximum_points'].append([max_x_coordinate, initial_point[1]])
                self.log('Gaussian fit successful! Centering on new point at x = {:.03f}'.format(max_x_coordinate))
            except (ValueError, RuntimeError, AssertionError):
                self.log('Gaussian fit NOT successful. Centering on previous point at x = {0}'.format(initial_point[0]))
                self.data['maximum_points'].append(initial_point)

            progress = 100 * ((float(iteration)+0.5)/float(self.settings['num_sweep_iterations']))
            self.updateProgress.emit(progress)
            time.sleep(1)

            initial_point = self.data['maximum_points'][-1]

            self.scripts['take_sweep'].settings['point_a'].update({'x': initial_point[0], 'y': initial_point[1]})
            self.scripts['take_sweep'].settings['point_b'].update({'x': 0, 'y': self.settings['sweep_range']})
            self.scripts['take_sweep'].update({'RoI_mode': 'center'})
            self.scripts['take_sweep'].settings['num_points'].update({'x': 1, 'y': self.settings['num_points']})

            print('points', {'x': initial_point[0], 'y': initial_point[1]}, {'x': self.settings['sweep_range'], 'y': 0})

            self.scripts['take_sweep'].run()

            self.y_sweeps.append(np.array(self.scripts['take_sweep'].data['image_data']).flatten())
            self.y_sweep_domains.append(np.linspace(initial_point[1] - self.settings['sweep_range'] / 2.0,
                                                    initial_point[1] + self.settings['sweep_range'] / 2.0,
                                                    self.settings['num_points'], endpoint=True))

            guess_noise = min(self.y_sweeps[-1])
            guess_amp = max(self.y_sweeps[-1]) - guess_noise
            reasonable_fit_params = [guess_noise, guess_amp, initial_point[0], .002]

            self.fit_params_y = [-1,-1,-1,-1]

            try:
                # fit_params = fit_gaussian(self.y_sweep_domains[-1], self.y_sweeps[-1], reasonable_fit_params,
                #                           bounds=([0, [np.inf, np.inf, 100., 100.]]))
                self.fit_params_y = fit_gaussian(self.y_sweep_domains[-1], self.y_sweeps[-1])
                max_y_coordinate = self.fit_params_y[2]
                assert((max_y_coordinate > min(self.y_sweep_domains[-1])) and (max_y_coordinate < max(self.y_sweep_domains[-1])))
                self.data['maximum_points'].append([initial_point[0], max_y_coordinate])
                self.log('Gaussian fit successful! Centering on new point at y = {:.03f}'.format(max_y_coordinate))
            except (ValueError, RuntimeError, AssertionError):
                self.log(
                    'Gaussian fit NOT successful. Centering on previous point at y = {0}'.format(initial_point[1]))
                self.data['maximum_points'].append(initial_point)


            progress = 100 * ((float(iteration) + 1.0) / float(self.settings['num_sweep_iterations']))
            self.updateProgress.emit(progress)
            time.sleep(1)

        self.data['sweep_domain'].append(self.x_sweep_domains)
        self.data['sweep'].append(self.x_sweeps)
        self.data['sweep_domain'].append(self.y_sweep_domains)
        self.data['sweep'].append(self.y_sweeps)


        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

    def plot(self, figure):
        def gaussian(x, constant_offset, amplitude, center, width):
            return constant_offset + amplitude * np.exp(-1.0 * (np.square((x - center)) / (2 * (width ** 2))))

        axes, axes2 = self.get_axes(figure)

        if self.x_sweeps:
            axes.plot(self.x_sweep_domains[-1], self.x_sweeps[-1], self.x_sweep_domains[-1], gaussian(self.x_sweep_domains[-1], self.fit_params_x[0], self.fit_params_x[1], self.fit_params_x[2], self.fit_params_x[3]))
            axes.set_title('x-coordinate sweep')
            axes.set_xlabel('galvo voltage [V]')
            axes.set_ylabel('counts [kcounts/s]')
        if self.y_sweeps:
            axes2.plot(self.y_sweep_domains[-1], self.y_sweeps[-1], self.y_sweep_domains[-1], gaussian(self.y_sweep_domains[-1], self.fit_params_y[0], self.fit_params_y[1], self.fit_params_y[2], self.fit_params_y[3]))
            axes2.plot(self.y_sweep_domains[-1], self.y_sweeps[-1])
            axes2.set_title('y-coordinate sweep')
            axes2.set_xlabel('galvo voltage [V]')
            axes2.set_ylabel('counts [kcounts/s]')
            #fig.subplots_adjust(top=0.85)

        fig.tight_layout()

    def get_axes(self, figure):
        figure.clf()
        axes = figure.add_subplot(121)
        axes2 = figure.add_subplot(122)

        return axes, axes2


    def stop(self):
        self._abort = True

    # def save_data(self, filename = None):
    #     super(GalvoScan, self).save_data(filename)
    #     if filename is None:
    #         filename = self.filename('.jpg')
    #     # self.saveFigure.emit(filename)

    if __name__ == '__main__':
        script, failed, instruments = Script.load_and_append(script_dict={'FindMaxCounts': 'FindMaxCounts'})

        print(script)
        print(failed)
        print(instruments)
