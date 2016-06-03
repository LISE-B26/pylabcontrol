from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.scripts import GalvoScan, SetLaser
from src.data_processing.fit_functions import fit_gaussian
import numpy as np
import time
import scipy.optimize
import pylab
from matplotlib import patches
import trackpy as tp
from copy import deepcopy
from src.plotting.plots_2d import plot_fluorescence
class FindMaxCounts2D(Script, QThread):
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
        Parameter('sweep_range', .02, float, 'voltage range to sweep over to find a max'),
        Parameter('num_points', 40, int, 'number of points to sweep in the sweep range'),
        Parameter('nv_size', 9, int),
        Parameter('minmass', 180, int)
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'take_sweep': GalvoScan, 'set_laser': SetLaser}

    def __init__(self, scripts, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):


        Script.__init__(self, name, scripts = scripts, settings=settings, log_function=log_function, data_path = data_path)

        QThread.__init__(self)

        self._plot_type = 'aux'

        self.scripts['take_sweep'].settings['time_per_pt'] = .01

        self.scripts['take_sweep'].updateProgress.connect(self._receive_signal)

        self.scripts['take_sweep'].log_function = self.log_function

    def _receive_signal(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript

        self.updateProgress.emit(progress_sub_script)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        initial_point = self.settings['initial_point']
        nv_size = self.settings['nv_size']
        minmass = self.settings['minmass']

        self.data = {'maximum_point': initial_point,
                     'initial_point': initial_point,
                     'image_data': [],
                     'extent': []
                     }


        def pixel_to_voltage(pt, extent, image_dimensions):
            """"
            pt: point in pixels
            extent: [xVmin, Vmax, Vmax, yVmin] in volts
            image_dimensions: dimensions of image in pixels

            Returns: point in volts
            """

            image_x_len, image_y_len = image_dimensions
            image_x_min, image_x_max, image_y_max, image_y_min = extent

            assert image_x_max > image_x_min
            assert image_y_max > image_y_min

            volt_per_px_x = (image_x_max - image_x_min) / image_x_len
            volt_per_px_y = (image_y_max - image_y_min) / image_y_len

            V_x = volt_per_px_x*pt[0] + image_x_min
            V_y = volt_per_px_y * pt[1] + image_y_min

            return [V_x, V_y]

        self.script_stage = 'take image'

        # self.scripts['take_sweep'].update({'point_a': {'x': initial_point[0], 'y': initial_point[1]}})
        self.scripts['take_sweep'].settings['point_a'].update({'x': self.settings['initial_point']['x'], 'y': self.settings['initial_point']['y']})
        self.scripts['take_sweep'].settings['point_b'].update({'x': self.settings['sweep_range'], 'y': self.settings['sweep_range']})
        self.scripts['take_sweep'].update({'RoI_mode': 'center'})
        self.scripts['take_sweep'].settings['num_points'].update({'x': self.settings['num_points'], 'y': self.settings['num_points']})

        self.scripts['take_sweep'].run()
        self.scripts['take_sweep'].wait()

        self.data['image_data'] = deepcopy(self.scripts['take_sweep'].data['image_data'])
        self.data['extent'] = deepcopy(self.scripts['take_sweep'].data['extent'])



        f = tp.locate(self.data['image_data'], nv_size, minmass=minmass)

        if len(f) ==0:
            self.data['maximum_point'] = [self.data['initial_point']['x'], self.data['initial_point']['y']]

            print('FINDING MAX DOESNT WORK: TAKE INITIAL POINT')
        else:
            self.data['maximum_point'] = pixel_to_voltage(f[['x','y']].iloc[0].as_matrix(),
                                                          self.data['extent'],
                                                          np.shape(self.data['image_data']))
        self.script_stage = 'find max'





        # #from scipy cookbook http://scipy.github.io/old-wiki/pages/Cookbook/FittingData
        # def gaussian(height, center_x, center_y, width_x, width_y):
        #     """Returns a gaussian function with the given parameters"""
        #     width_x = float(width_x)
        #     width_y = float(width_y)
        #     return lambda x, y: height * np.exp(
        #         -(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)
        #
        # #from scipy cookbook http://scipy.github.io/old-wiki/pages/Cookbook/FittingData
        # def moments(data):
        #     """Returns (height, x, y, width_x, width_y)
        #     the gaussian parameters of a 2D distribution by calculating its
        #     moments """
        #     total = data.sum()
        #     X, Y = np.indices(data.shape)
        #     x = (X * data).sum() / total
        #     y = (Y * data).sum() / total
        #     col = data[:, int(y)]
        #     width_x = np.sqrt(abs((np.arange(col.size) - y) ** 2 * col).sum() / col.sum())
        #     row = data[int(x), :]
        #     width_y = np.sqrt(abs((np.arange(row.size) - x) ** 2 * row).sum() / row.sum())
        #     height = data.max()
        #     return height, x, y, width_x, width_y
        #
        # #from scipy cookbook http://scipy.github.io/old-wiki/pages/Cookbook/FittingData
        # def fitgaussian(data):
        #     """Returns (height, x, y, width_x, width_y)
        #     the gaussian parameters of a 2D distribution found by a fit"""
        #     params = moments(data)
        #     errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
        #                                     data)
        #     p, success = scipy.optimize.leastsq(errorfunction, params)
        #     return p
        #
        # self.data['fit_parameters'] = fitgaussian(self.data['image_data'])


        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

        self.updateProgress.emit(100)
        import time
        time.sleep(3)

    def plot(self, axes, axes_colorbar = None):
        #from scipy cookbook http://scipy.github.io/old-wiki/pages/Cookbook/FittingData
        # def gaussian(height, center_x, center_y, width_x, width_y):
        #     """Returns a gaussian function with the given parameters"""
        #     width_x = float(width_x)
        #     width_y = float(width_y)
        #     return lambda x, y: height * np.exp(
        #         -(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)

        # plot image
        if self.script_stage == 'take image':
            self.scripts['take_sweep'].plot(axes)

        if self.script_stage != 'take image':

            print('DDDDD - fluor')
            plot_fluorescence(self.data['image_data'], self.data['extent'], axes, axes_colorbar=axes_colorbar)

            # plot marker
            maximum_point = self.data['maximum_point']
            print(maximum_point)
            patch = patches.Circle((maximum_point[0], maximum_point[1]), .001, ec='r', fc = 'none')
            axes.add_patch(patch)


            print('DDDDD - pt')


        # fit = gaussian(*self.data['fit_parameters'])
        # axes.contour(fit(*np.indices(self.data['image_data'].shape)), cmap=np.cm.copper)


    def stop(self):
        self.scripts['take_sweep'].stop()

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
