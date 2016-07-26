from copy import deepcopy

import numpy as np
import trackpy as tp
from matplotlib import patches

from b26_toolkit.src.plotting import plot_fluorescence_new
from src.core import Script, Parameter
from src.scripts import GalvoScanWithLightControl, SetLaser


class FindMaxCounts2D(Script):
    """
GalvoScan uses the apd, daq, and galvo to sweep across voltages while counting photons at each voltage,
resulting in an image in the current field of view of the objective.

Known issues:
    1.) if fits are poor, check  sweep_range. It should extend significantly beyond end of NV on both sides.
    """

    _DEFAULT_SETTINGS = [
        Parameter('initial_point',
                  [Parameter('x', 0, float, 'x-coordinate'),
                   Parameter('y', 0, float, 'y-coordinate')
                   ]),
        Parameter('sweep_range', .02, float, 'voltage range to sweep over to find a max'),
        Parameter('num_points', 40, int, 'number of points to sweep in the sweep range'),
        Parameter('nv_size', 11, int, 'TEMP: size of nv in pixels - need to be refined!!'),
        Parameter('min_mass', 180, int, 'TEMP: brightness of nv - need to be refined!!'),
        Parameter('number_of_attempts', 1, int, 'Number of times to decrease min_mass if an NV is not found')
    ]

    _INSTRUMENTS = {}

    _SCRIPTS = {'take_image': GalvoScanWithLightControl, 'set_laser': SetLaser}

    def __init__(self, scripts, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):

        Script.__init__(self, name, scripts = scripts, settings=settings, log_function=log_function, data_path = data_path)


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        attempt_num = 1

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

        def min_mass_adjustment(min_mass):
            #COMMENT_ME
            return (min_mass - 40)

        self.scripts['take_image'].scripts['acquire_image'].settings['point_a'].update({'x': self.settings['initial_point']['x'], 'y': self.settings['initial_point']['y']})
        self.scripts['take_image'].scripts['acquire_image'].settings['point_b'].update({'x': self.settings['sweep_range'], 'y': self.settings['sweep_range']})
        self.scripts['take_image'].scripts['acquire_image'].update({'RoI_mode': 'center'})
        self.scripts['take_image'].scripts['acquire_image'].settings['num_points'].update({'x': self.settings['num_points'], 'y': self.settings['num_points']})

        self.scripts['take_image'].run()

        self.data['image_data'] = deepcopy(self.scripts['take_image'].scripts['acquire_image'].data['image_data'])
        self.data['extent'] = deepcopy(self.scripts['take_image'].scripts['acquire_image'].data['extent'])
        while True:
            f = tp.locate(self.data['image_data'], nv_size, minmass=min_mass)

            po = [self.data['initial_point']['x'], self.data['initial_point']['y']]
            if len(f) == 0:
                self.data['maximum_point'] = {'x': float(po[0]), 'y': float(po[1])}
                self.log('pytrack failed to find NV --- setting laser to initial point instead')
            else:

                # all the points that have been identified as valid NV centers
                pts = [pixel_to_voltage(p, self.data['extent'], np.shape(self.data['image_data'])) for p in
                       f[['x', 'y']].as_matrix()]
                if len(pts) > 1:
                    self.log('Info!! Found more than one NV. Selecting the one closest to initial point!')
                # pick the one that is closest to the original one
                pm = pts[np.argmin(np.array([np.linalg.norm(p - np.array(po)) for p in pts]))]
                self.data['maximum_point'] = {'x': float(pm[0]), 'y': float(pm[1])}
                break

            if attempt_num <= self.settings['number_of_attempts']:
                min_mass = min_mass_adjustment(min_mass)
                attempt_num += 1
            else:
                break

        self.scripts['set_laser'].settings['point'].update(self.data['maximum_point'])
        self.scripts['set_laser'].run()

        # if self.settings['save']:
        #     #COMMENT_ME
        #     self.save_b26()
        #     self.save_data()
        #     self.save_log()
        #     self.save_image_to_disk()

    def _plot(self, axes_list):
        # COMMENT_ME

        if self._current_subscript_stage['current_subscript'] == self.scripts['take_image']:
            self.scripts['take_image']._plot(axes_list)
        else:
            plot_fluorescence_new(self.data['image_data'], self.data['extent'], axes_list[0])

        # plot marker
        maximum_point = self.data['maximum_point']
        patch = patches.Circle((maximum_point['x'], maximum_point['y']), .001, ec='r', fc='none')
        axes_list[0].add_patch(patch)

        initial_point = self.data['initial_point']
        patch = patches.Circle((initial_point['x'], initial_point['y']), .001, ec='g', fc='none')
        axes_list[0].add_patch(patch)


    def _update_plot(self, axes_list):
        # COMMENT_ME

        if self._current_subscript_stage['current_subscript'] == self.scripts['take_image']:
            self.scripts['take_image']._update_plot(axes_list)

            # # plot marker
            # maximum_point = self.data['maximum_point']
            # patch = patches.Circle((maximum_point['x'], maximum_point['y']), .001, ec='r', fc='none')
            # axes_list[0].add_patch(patch)
            #
            # initial_point = self.data['initial_point']
            # patch = patches.Circle((initial_point['x'], initial_point['y']), .001, ec='g', fc='none')
            # axes_list[0].add_patch(patch)


    def get_axes_layout(self, figure_list):
        """
        returns the axes objects the script needs to plot its data
        the default creates a single axes object on each figure
        This can/should be overwritten in a child script if more axes objects are needed
        Args:
            figure_list: a list of figure objects
        Returns:
            axes_list: a list of axes objects

        """

        # create a new figure list that contains only figure 1, this assures that the super.get_axes_layout doesn't
        # empty the plot contained on figure 2
        return super(FindMaxCounts2D, self).get_axes_layout([figure_list[0]])




    if __name__ == '__main__':
        script, failed, instruments = Script.load_and_append(script_dict={'FindMaxCounts': 'FindMaxCounts'})

        print(script)
        print(failed)
        print(instruments)
