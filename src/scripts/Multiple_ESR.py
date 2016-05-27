from src.core import Script, Parameter
from src.scripts import StanfordResearch_ESR, Select_NVs_Simple, GalvoScan
from src.instruments.NIDAQ import DAQ
import time
import scipy.spatial
import numpy as np
from matplotlib import patches
from PySide.QtCore import Signal, QThread
from src.core.plotting import plot_fluorescence
from copy import deepcopy
import os

class ESR_Selected_NVs_Simple(Script, QThread):
    """
script that allows to select several NVs and run ESR on the selected points.
To select points, first run subscript Select_NVs_Simple
    """
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off')
    ])

    _INSTRUMENTS = {'daq': DAQ}
    _SCRIPTS = {'StanfordResearch_ESR': StanfordResearch_ESR,
                'select_NVs': Select_NVs_Simple,
                'acquire_image':GalvoScan}

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

        self.scripts['StanfordResearch_ESR'].updateProgress.connect(self._receive_signal)
        self.scripts['acquire_image'].updateProgress.connect(self._receive_signal_2)

        self.data = None

        self.progress_stage = 'ready'

    def _receive_signal(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript

        if progress_sub_script == 100:
            progress = float(self.index)/self.num_esrs
        else:
            progress = float(self.index) / self.num_esrs + float(progress_sub_script) / 100. / self.num_esrs

        progress*=100
        progress = int(progress)

        self.updateProgress.emit(progress)

    def _receive_signal_2(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript
        if progress_sub_script ==100:
            progress_sub_script = 90
        self.updateProgress.emit(progress_sub_script)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self._abort = False

        self.progress_stage = 'start script'

        nv_locs = self.scripts['select_NVs'].data['nv_locations']

        acquire_image = self.scripts['acquire_image']

        if 'image_data' not in acquire_image.data.keys():
            self.log('no image acquired!! Run subscript acquire_image first!!')

        if nv_locs == []:
            self.log('no points selected acquired!! Run subscript select_NVs first!!')

        [xVmin, xVmax, yVmax, yVmin] = acquire_image.pts_to_extent(acquire_image.settings['point_a'],
                                                                   acquire_image.settings['point_b'],
                                                                   acquire_image.settings['RoI_mode'])

        self.data = {'image_data': deepcopy(acquire_image.data['image_data']),
                     'image_data_2':None,
                     'extent' :  [xVmin, xVmax, yVmax, yVmin],
                     'nv_locs': nv_locs,
                     'ESR_freqs': [],
                     'ESR_data': np.zeros((len(nv_locs), self.scripts['StanfordResearch_ESR'].settings['freq_points']))}

        self.num_esrs = len(nv_locs)

        if self.settings['save']:
            # create and save images
            filename_image = '{:s}\\image\\'.format(self.filename())
            if os.path.exists(filename_image) == False:
                os.makedirs(filename_image)

        self.progress_stage = 'acquire esr'
        for index, pt in enumerate(nv_locs):
            self.index = index
            self.cur_pt = pt
            if not self._abort:
                self.log('Taking ESR of point ' + str(index + 1) + ' of ' + str(len(nv_locs)))
                #set laser to new point
                pt = np.transpose(np.column_stack((pt[0], pt[1])))
                pt = (np.repeat(pt, 2, axis=1))

                self.instruments['daq']['instance'].AO_init(["ao0","ao1"], pt)
                self.instruments['daq']['instance'].AO_run()
                self.instruments['daq']['instance'].AO_waitToFinish()
                self.instruments['daq']['instance'].AO_stop()

                #run the ESR
                self.scripts['StanfordResearch_ESR'].run()
                self.scripts['StanfordResearch_ESR'].wait() #wait for previous ESR thread to complete

                self.data['ESR_freqs'] = self.scripts['StanfordResearch_ESR'].data[-1]['frequency']

                self.data['ESR_data'][index] = self.scripts['StanfordResearch_ESR'].data[-1]['data']
                if self.settings['save']:
                    # create and save images
                    self.scripts['StanfordResearch_ESR'].save_image_to_disk('{:s}\\esr-point_{:03d}.jpg'.format(filename_image, index))

                #can't call run twice on the same object, so start a new, identical ESR script for the next run
                #update: probably not supported, but doesn't seem to have any ill effects
                # self.scripts['StanfordResearch_ESR'] = StanfordResearch_ESR(esr_instruments, settings = esr_settings)
                # self.scripts['StanfordResearch_ESR'].updateProgress.connect(self._receive_signal)

        self.log('acquire new image')
        self.progress_stage = 'acquire image'
        # take another image
        acquire_image.run()
        acquire_image.wait()  # wait for thread to complete

        self.data['image_data_2'] = deepcopy(acquire_image.data['image_data'])



        self.progress_stage = 'saving data'
        if self.settings['save']:
            self.save()
            self.save_data()
            self.save_image_to_disk('{:s}\\nv-map.jpg'.format(filename_image))


        self.progress_stage = 'finished'

        self.updateProgress.emit(100)



    def stop(self):
        self._abort = True
        self.scripts['StanfordResearch_ESR'].stop()

    def plot(self, axes_Image, axes_ESR = None):

        patch_size = self.scripts['select_NVs'].settings['patch_size']

        if self.progress_stage == 'finished' or  self.progress_stage == 'saving data':

            image = self.data['image_data_2']
            extent = self.data['extent']

            plot_fluorescence(image, extent, axes_Image)

            self.scripts['select_NVs'].plot(axes_Image)

            # patch = patches.Circle((self.cur_pt[0], self.cur_pt[1]), 1.1* patch_size, edgecolor='r')
            # axes_Image.add_patch(patch)
        elif self.progress_stage == 'acquire image':
            self.scripts['acquire_image'].plot(axes_Image)

        elif self.progress_stage == 'acquire esr':
            image = self.data['image_data']
            extent = self.data['extent']
            plot_fluorescence(image, extent, axes_Image)

            self.scripts['select_NVs'].plot(axes_Image)

            patch = patches.Circle((self.cur_pt[0], self.cur_pt[1]), 1.1 * patch_size, edgecolor='r')
            axes_Image.add_patch(patch)

        if axes_ESR is not None:
            self.scripts['StanfordResearch_ESR'].plot(axes_ESR)



if __name__ == '__main__':
    from src.core import Instrument

    instruments, instruments_failed = Instrument.load_and_append({'daq':  'DAQ'})

    script, failed, instruments = Script.load_and_append(script_dict={'ESR_Selected_NVs':'ESR_Selected_NVs'}, instruments = instruments)

    print(instruments)