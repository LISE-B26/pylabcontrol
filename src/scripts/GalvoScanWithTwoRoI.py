from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.scripts import GalvoScanWithLightControl
from copy import deepcopy
from src.plotting.plots_2d import plot_fluorescence

class GalvoScanWithTwoRoI(Script, QThread):
    """
Select two regions of interest (RoI) and the light mode for each (fluorescence or reflection).
Takes an image based on GalvoScanWithLightControl script which takes image based in GalvoScan script and controls light with MaestroLightControl instrument
    """

    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', '\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', False, bool, 'check to automatically save data'),
        Parameter('RoI_1',[
            Parameter('point_a',
                    [Parameter('x', -0.4, float, 'x-coordinate'),
                     Parameter('y', -0.4, float, 'y-coordinate')
            ]),
            Parameter('point_b',
                    [Parameter('x', 0.4, float, 'x-coordinate'),
                     Parameter('y', 0.4, float, 'y-coordinate')
            ]),
            Parameter('light_mode', 'fluorescence', ['fluorescence', 'reflection']),
            Parameter('RoI_mode', 'corner', ['corner', 'center'], 'mode to calculate region of interest.\n \
                                                       corner: pta and ptb are diagonal corners of rectangle.\n \
                                                       center: pta is center and pta is extend or rectangle'),
            Parameter('num_points',
                      [Parameter('x', 20, int, 'number of x points to scan'),
                       Parameter('y', 20, int, 'number of y points to scan')
                       ])
                  ]),
        Parameter('RoI_2',[
            Parameter('point_a',
                    [Parameter('x', -0.4, float, 'x-coordinate'),
                     Parameter('y', -0.4, float, 'y-coordinate')
                     ]),
            Parameter('point_b',
                    [Parameter('x', 0.4, float, 'x-coordinate'),
                     Parameter('y', 0.4, float, 'y-coordinate')
                     ]),
            Parameter('light_mode', 'fluorescence', ['fluorescence', 'reflection'])
            ]),
            Parameter('RoI_mode', 'corner', ['corner', 'center'], 'mode to calculate region of interest.\n \
                                                       corner: pta and ptb are diagonal corners of rectangle.\n \
                                                       center: pta is center and pta is extend or rectangle'),
            Parameter('num_points',
                      [Parameter('x', 20, int, 'number of x points to scan'),
                       Parameter('y', 20, int, 'number of y points to scan')
                       ])
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'acquire_image': GalvoScanWithLightControl}


    def __init__(self, scripts, name=None, settings=None, log_function=None, data_path=None):

        Script.__init__(self, name, settings=settings, scripts = scripts, log_function=log_function, data_path=data_path)

        QThread.__init__(self)

        self._plot_type = 'aux'

        self.scripts['acquire_image'].updateProgress.connect(self._receive_signal)

        self.progress_details = 'initialized'
        self.data = {}

        self._abort = False

    def _receive_signal(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript

        progress = float(progress_sub_script)/2.

        if self.progress_details == 'acquire image 2':
            progress +=50
        if progress == 100:
            progress = 99

        self.updateProgress.emit(int(progress))

    def _function(self):


        acquire_image = self.scripts['acquire_image']

        if self._abort == False:
            self.progress_details = 'acquire image 1'

            acquire_image.settings['light_mode'] = self.settings['RoI_1']['light_mode']

            dictator = {
                'point_a' : self.settings['RoI_1']['point_a'],
                'point_b': self.settings['RoI_1']['point_b']
            }
            acquire_image.scripts['acquire_image'].settings.update(dictator)

            # acquire_image.settings['point_a']['x'] = self.settings['RoI_1']['point_a']['x']
            # acquire_image.settings['point_a']['y'] = self.settings['RoI_1']['point_a']['y']
            # acquire_image.settings['point_b']['x'] = self.settings['RoI_1']['point_b']['x']
            # acquire_image.settings['point_b']['y'] = self.settings['RoI_1']['point_b']['y']


            self.scripts['acquire_image'].start()
            self.scripts['acquire_image'].wait()

            self.data.update({
                'image_data_roi_1': deepcopy(self.scripts['acquire_image'].data['image_data']),
                'extent_roi_1': deepcopy(self.scripts['acquire_image'].data['extent'])
            })

        if self._abort == False:
            self.progress_details = 'acquire image 2'
            # acquire_image.settings['light_mode'] = self.settings['RoI_2']['light_mode']
            # acquire_image.settings['point_a']['x'] = self.settings['RoI_2']['point_a']['x']
            # acquire_image.settings['point_a']['y'] = self.settings['RoI_2']['point_a']['y']
            # acquire_image.settings['point_b']['x'] = self.settings['RoI_2']['point_b']['x']
            # acquire_image.settings['point_b']['y'] = self.settings['RoI_2']['point_b']['y']

            acquire_image.settings['light_mode'] = self.settings['RoI_2']['light_mode']

            dictator = {
                'point_a': self.settings['RoI_2']['point_a'],
                'point_b': self.settings['RoI_2']['point_b']
            }
            acquire_image.scripts['acquire_image'].settings.update(dictator)

            self.scripts['acquire_image'].start()
            self.scripts['acquire_image'].wait()

            self.data.update({
                'image_data_roi_2': deepcopy(self.scripts['acquire_image'].data['image_data']),
                'extent_roi_2': deepcopy(self.scripts['acquire_image'].data['extent'])
            })



        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

        self.updateProgress.emit(100)

    def stop(self):
        self._abort = True
        self.scripts['acquire_image'].stop()


    def plot(self, figure):

        # we need two axes object to plot both plots, if there is only one, create another
        # fig = axes1.get_figure()
        # if (len(fig.axes) != 4):
        #     axes1.change_geometry(1, 4, 1)
        #     axes1b = fig.add_subplot(1, 4, 2)
        #     axes2 = fig.add_subplot(1, 4, 3)
        #     axes2b = fig.add_subplot(1, 4, 4)
        # else:
        #     axes1.change_geometry(1, 4, 1)
        #     axes1b = fig.axes[1]
        #     axes2 = fig.axes[2]
        #     axes2b = fig.axes[3]
        #     # axes2.clear()

        axes1, axes1b, axes2, axes2b = self.get_axes_layout(figure)

        image_data_roi_1 = None
        image_data_roi_2 = None

        if self.progress_details == 'acquire image 1':
            self.scripts['acquire_image'].plot(axes1, axes_colorbar  =axes1b)
        elif self.progress_details == 'acquire image 2':
            image_data_roi_1 = self.data['image_data_roi_1']
            extent_roi_1 = self.data['extent_roi_1']
            self.scripts['acquire_image'].plot(axes2, axes_colorbar  =axes2b)
        else:
            image_data_roi_1 = self.data['image_data_roi_1']
            image_data_roi_2 = self.data['image_data_roi_2']
            extent_roi_1 = self.data['extent_roi_1']
            extent_roi_2 = self.data['extent_roi_2']

        # todo: allow user to set max_counts? Not really clear if max_counts is needed
        if image_data_roi_1 is not None:
            plot_fluorescence(image_data_roi_1, extent_roi_1, axes1, axes_colorbar=axes1b)
        if image_data_roi_2 is not None:
            plot_fluorescence(image_data_roi_2, extent_roi_2, axes2, axes_colorbar=axes2b)

        figure.tight_layout()

    def get_axes_layout(self, figure):
        figure.clf()

        axes1 = figure.add_subplot(141)
        axes1b = figure.add_subplot(142)
        axes2 = figure.add_subplot(143)
        axes2b = figure.add_subplot(144)

        return axes1, axes1b, axes2, axes2b




