from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.instruments import MaestroLightControl
from src.scripts import GalvoScan
from copy import deepcopy
from src.plotting.plots_2d import plot_fluorescence

class GalvoScanWithLightControl(Script, QThread):
    """
Takes an image based in galvo scan script and controls light with MaestroLightControl instrument
    """

    updateProgress = Signal(int)
    saveFigure = Signal(str)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool, 'check to automatically save data'),
        Parameter('light_mode','fluorescence', ['fluorescence', 'reflection'])
    ])

    _INSTRUMENTS = {'MaestroLightControl': MaestroLightControl}

    _SCRIPTS = {'acquire_image': GalvoScan}


    def __init__(self, instruments, scripts, name=None, settings=None, log_function=None, data_path=None):

        Script.__init__(self, name, settings=settings, instruments=instruments, scripts = scripts, log_function=log_function, data_path=data_path)

        QThread.__init__(self)

        self._plot_type = 'main'

        self.scripts['acquire_image'].updateProgress.connect(self._receive_signal)

    def _receive_signal(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript

        progress = progress_sub_script
        if progress == 100:
            progress = 99
        self.updateProgress.emit(progress)

    def _function(self):

        instrument_settings = self.instruments['MaestroLightControl']['settings']

        if self.settings['light_mode'] == 'fluorescence':
            instrument_settings.update({
                'white light':{'open':False},
                'filter wheel': {'current_position': 'red_filter'},
                'block IR': {'open': False},
                'block green': {'open': True}
            })

        elif  self.settings['light_mode'] == 'reflection':
            instrument_settings.update({
                'white light':{'open':False},
                'filter wheel': {'current_position': 'ND1.0'},
                'block IR': {'open': False},
                'block green': {'open': True}
            })
        else:
            raise TypeError('unknown light mode')

        self.instruments['MaestroLightControl']['instance'].update(instrument_settings)

        self.scripts['acquire_image'].run()
        self.scripts['acquire_image'].wait()

        self.data = deepcopy(self.scripts['acquire_image'].data)

        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()

        self.updateProgress.emit(100)

    def stop(self):
        self.scripts['acquire_image'].stop()


    def plot(self, image_figure, axes_colorbar = None):
        self.scripts['acquire_image'].plot(image_figure, axes_colorbar = axes_colorbar)


