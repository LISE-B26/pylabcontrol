from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.scripts import GalvoScan, SetLaser
import numpy as np
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
        Parameter('path',  '', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', False, bool,'check to automatically save data'),
        Parameter('initial_point',
                  [Parameter('x', 0, float, 'x-coordinate'),
                   Parameter('y', 0, float, 'y-coordinate')
                   ]),
        Parameter('sweep_range', .02, float, 'voltage range to sweep over to find a max'),
        Parameter('num_points', 40, int, 'number of points to sweep in the sweep range'),
        Parameter('nv_size', 11, int, 'TEMP: size of nv in pixels - need to be refined!!'),
        Parameter('min_mass', 180, int, 'TEMP: brightness of nv - need to be refined!!')
    ])

    # todo: make minmass and nv_size more intelligent, i.e. uses extend to calculate the expected size and brightness
    _INSTRUMENTS = {}

    _SCRIPTS = {'take_image': GalvoScan, 'set_laser': SetLaser}

    def __init__(self, scripts, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):

        Script.__init__(self, name, scripts = scripts, settings=settings, log_function=log_function, data_path = data_path)

        QThread.__init__(self)

        self._plot_type = 'aux'

        self.scripts['take_image'].settings['time_per_pt'] = .01

        self.scripts['take_image'].updateProgress.connect(self._receive_signal)

        self.scripts['take_image'].log_function = self.log_function

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
        min_mass = self.settings['min_mass']

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

        # self.scripts['take_image'].update({'point_a': {'x': initial_point[0], 'y': initial_point[1]}})
        self.scripts['take_image'].settings['point_a'].update({'x': self.settings['initial_point']['x'], 'y': self.settings['initial_point']['y']})
        self.scripts['take_image'].settings['point_b'].update({'x': self.settings['sweep_range'], 'y': self.settings['sweep_range']})
        self.scripts['take_image'].update({'RoI_mode': 'center'})
        self.scripts['take_image'].settings['num_points'].update({'x': self.settings['num_points'], 'y': self.settings['num_points']})

        self.scripts['take_image'].run()
        self.scripts['take_image'].wait()

        self.data['image_data'] = deepcopy(self.scripts['take_image'].data['image_data'])
        self.data['extent'] = deepcopy(self.scripts['take_image'].data['extent'])

        f = tp.locate(self.data['image_data'], nv_size, minmass=min_mass)

        if len(f) == 0:
            self.data['maximum_point'] = [self.data['initial_point']['x'], self.data['initial_point']['y']]

            self.log('pytrack failed to find NV --- setting laser to initial point instead')
        else:

            pt = pixel_to_voltage(f[['x','y']].iloc[0].as_matrix(),
                                                          self.data['extent'],
                                                          np.shape(self.data['image_data']))
            self.data['maximum_point'] = pt
        self.script_stage = 'find max'

        print(self.data['maximum_point'])
        self.scripts['set_laser'].settings['point'].update({'x': self.data['maximum_point'][0],
                                                       'y': self.data['maximum_point'][1]})
        self.scripts['set_laser'].run()

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()

        self.updateProgress.emit(100)


    def plot(self, figure, axes_colorbar = None):
        # plot image
        if self.script_stage == 'take image':
            self.scripts['take_image'].plot(figure)

        if self.script_stage != 'take image':
            axes = self.get_axes(figure)

            plot_fluorescence(self.data['image_data'], self.data['extent'], axes, axes_colorbar=axes_colorbar)

            # plot marker
            maximum_point = self.data['maximum_point']
            patch = patches.Circle((maximum_point[0], maximum_point[1]), .001, ec='r', fc = 'none')
            axes.add_patch(patch)



    def stop(self):
        self.scripts['take_image'].stop()


    if __name__ == '__main__':
        script, failed, instruments = Script.load_and_append(script_dict={'FindMaxCounts': 'FindMaxCounts'})

        print(script)
        print(failed)
        print(instruments)
