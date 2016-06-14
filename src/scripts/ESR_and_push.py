import numpy as np
from PySide.QtCore import Signal, QThread
from matplotlib import patches

from src.core import Script, Parameter
from src.scripts import ESR_Selected_NVs, Refind_NVs, AttoStep
import time

class ESR_And_Push(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('activate_correlate', True, bool, 'perform correlation'),
        Parameter('trackpy_correlation', False, bool, 'Use trackpy to create an artificial image of just the NVs to filter a noisy background'),
        Parameter('activate_autofocus', True, bool, 'perform autofocus'),
        Parameter('autofocus_size', .1, float, 'Side length of autofocusing square in Volts'),
        Parameter('number_of_step_instances', 0, int, 'number of times to do steps_per_instance steps'),
        Parameter('steps_per_instance', 1, int, 'number of steps in between each ESR')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {'ESR_Selected_NVs': ESR_Selected_NVs,
                'AttoStep': AttoStep,
                'Refind_NVs': Refind_NVs}

    #updateProgress = Signal(int)

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.

    def __init__(self, instruments = None, scripts = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False

        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)

        QThread.__init__(self)

        self._plot_type = 'two'

        self.index = 0

        self.scripts['ESR_Selected_NVs'].log_function = self.log_function
        self.scripts['AttoStep'].log_function = self.log_function
        self.scripts['Refind_NVs'].log_function = self.log_function

    def _receive_signal(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript

        self.progress = progress_sub_script
        if self.progress ==100:
            self.progress = 99
        self.updateProgress.emit(self.progress)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self.progress = 0
        self.current_stage = None

        self.scripts['ESR_Selected_NVs'].updateProgress.connect(self._receive_signal)
        self.scripts['AttoStep'].updateProgress.connect(self._receive_signal)
        self.scripts['Refind_NVs'].updateProgress.connect(self._receive_signal)

        self.data = {'baseline_image': [],
                     'baseline_extent': [],
                     'baseline_nv_locs': [],
                     'ESR_freqs': [],
                     'ESR_data': []}

        acquire_image = self.scripts['ESR_Selected_NVs'].scripts['acquire_image']
        if 'image_data' not in acquire_image.data.keys():
            self.log('no image acquired!! Run subscript ESR_Selected_NVs.acquire_image first!!')
            return

        if self.scripts['ESR_Selected_NVs'].scripts['Select_NVs'].data['nv_locations'] == []:
            self.log('no points selected!! Run subscript ESR_Selected_NVs.select_NVs first!!')
            return

        self.data['baseline_image'] = acquire_image.data['image_data']
        self.data['baseline_extent'] = acquire_image.pts_to_extent(acquire_image.settings['point_a'],
                                                                   acquire_image.settings['point_b'],
                                                                   acquire_image.settings['RoI_mode'])
        self.data['baseline_nv_locs'] = self.scripts['ESR_Selected_NVs'].scripts['Select_NVs'].data['nv_locations']

        self.current_stage = 'ESR_Selected_NVs'

        self.scripts['ESR_Selected_NVs'].run()
        self.scripts['ESR_Selected_NVs'].wait()

        self.scripts['Refind_NVs'].data['baseline_image'] = self.data['baseline_image']
        self.scripts['Refind_NVs'].data['baseline_extent'] = self.data['baseline_extent']
        self.scripts['Refind_NVs'].data['baseline_nv_locs'] = self.data['baseline_nv_locs']


        step_num = 0

        while step_num <= self.settings['number_of_step_instances'] and not self._abort:

            for i in range(0,self.settings['steps_per_instance']):
                self.scripts['AttoStep'].run()
                time.sleep(1)

            self.current_stage = 'Refind_NVs'
            self.scripts['Refind_NVs'].run()
            self.scripts['Refind_NVs'].wait()

            self.current_stage = 'ESR_Selected_NVs'
            self.scripts['ESR_Selected_NVs'].scripts['select_NVs'].data['nv_locations'] = self.scripts['Refind_NVs'].data['new_nv_locs']
            self.scripts['ESR_Selected_NVs'].run()
            self.scripts['ESR_Selected_NVs'].wait()


        self.data['ESR_freqs'] = self.scripts['ESR_Selected_NVs'].data['ESR_freqs']
        self.data['ESR_data'] = self.scripts['ESR_Selected_NVs'].data['ESR_data']


        self.current_stage = 'finished'

        self.updateProgress.emit(100)
        if self.settings['save']:
            self.current_stage = 'saving'
            self.save_b26()
            self.save_data()

        self.scripts['ESR_Selected_NVs'].updateProgress.disconnect(self._receive_signal)
        self.scripts['AttoStep'].updateProgress.disconnect(self._receive_signal)
        self.scripts['Refind_NVs'].updateProgress.disconnect(self._receive_signal)


    def stop(self):
        self._abort = True
        self.scripts['ESR_Selected_NVs'].stop()
        self.scripts['Refind_NVs'].stop()

    def plot(self, figure_image, figure_ESR):
        pass

if __name__ == '__main__':
    script, failed, instruments = Script.load_and_append(script_dict={'ESR_And_Push':'ESR_And_Push'})

    print(script)
    print(failed)
    print(instruments)