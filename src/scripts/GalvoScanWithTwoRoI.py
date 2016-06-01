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
    saveFigure = Signal(str)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', '\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool, 'check to automatically save data'),
        Parameter('RoI_1',[
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
                  ])
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'acquire_image': GalvoScanWithLightControl}


    def __init__(self, scripts, name=None, settings=None, log_function=None, data_path=None):

        Script.__init__(self, name, settings=settings, scripts = scripts, log_function=log_function, data_path=data_path)

        QThread.__init__(self)

        self._plot_type = 'main'

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
            acquire_image.settings['point_a']['x'] = self.settings['RoI_1']['point_a']['x']
            acquire_image.settings['point_a']['y'] = self.settings['RoI_1']['point_a']['y']
            acquire_image.settings['point_b']['x'] = self.settings['RoI_1']['point_b']['x']
            acquire_image.settings['point_b']['y'] = self.settings['RoI_1']['point_b']['y']


            self.scripts['acquire_image'].run()
            self.scripts['acquire_image'].wait()

            self.data.update({'image_data_roi_1': deepcopy(self.scripts['acquire_image'].data['image_data'])})

        if self._abort == False:
            self.progress_details = 'acquire image 2'
            acquire_image.settings['light_mode'] = self.settings['RoI_2']['light_mode']
            acquire_image.settings['point_a']['x'] = self.settings['RoI_2']['point_a']['x']
            acquire_image.settings['point_a']['y'] = self.settings['RoI_2']['point_a']['y']
            acquire_image.settings['point_b']['x'] = self.settings['RoI_2']['point_b']['x']
            acquire_image.settings['point_b']['y'] = self.settings['RoI_2']['point_b']['y']


            self.scripts['acquire_image'].run()
            self.scripts['acquire_image'].wait()

            self.data.update({'image_data_roi_2': deepcopy(self.scripts['acquire_image'].data['image_data'])})



        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

        self.updateProgress.emit(100)

    def stop(self):
        self._abort = True
        self.scripts['acquire_image'].stop()


    def plot(self, axes):

        if self.is_running:
            self.scripts['acquire_image'].plot(axes)
        else:
            # todo: create two subplots and show both data
            plot_fluorescence(self.data['image_data'], self.data['extent'], axes,
                              max_counts=self.scripts['acquire_image'].settings['max_counts_plot'])


