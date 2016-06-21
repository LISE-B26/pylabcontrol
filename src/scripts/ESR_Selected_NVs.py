import numpy as np
from PySide.QtCore import Signal, QThread
from matplotlib import patches

from src.core import Script, Parameter
from src.plotting.plots_1d import plot_esr
from src.plotting.plots_2d import plot_fluorescence
from src.scripts import StanfordResearch_ESR, Select_NVs_Simple, GalvoScanWithLightControl, SetLaser
from src.scripts import FindMaxCounts2D
import os


class ESR_Selected_NVs(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('save_subscripts', False, bool, 'save subscripts for troubleshooting'),
        Parameter('num_between_correlate', -1, int, 'Number of ESRs between correlations, -1 to deactivate correlation'),
        Parameter('trackpy_correlation', False, bool, 'Use trackpy to create an artificial image of just the NVs to filter a noisy background'),
        Parameter('num_between_autofocus', -1, int, 'Number of ESRs between autofocuses, -1 to deactivate autofocus'),
        Parameter('autofocus_size', .1, float, 'Side length of autofocusing square in Volts')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {'StanfordResearch_ESR': StanfordResearch_ESR,
                'Find_Max': FindMaxCounts2D,
                'select_NVs': Select_NVs_Simple,
                'acquire_image': GalvoScanWithLightControl,
                'move_to_point': SetLaser}

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

        self.scripts['acquire_image'].log_function = self.log_function
        self.scripts['Find_Max'].log_function = self.log_function
        self.scripts['StanfordResearch_ESR'].log_function = self.log_function
        self.scripts['move_to_point'].log_function = self.log_function

        self.current_stage = 'init'

    def _receive_signal(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript

        if self.current_stage == 'ESR':
            self.progress = int((float(self.index)/self.num_esrs)*100 + float(progress_sub_script)/self.num_esrs)
        if self.progress ==100:
            self.progress = 99
        self.updateProgress.emit(self.progress)

    def _receive_signal_2(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript
        if progress_sub_script ==100:
            progress_sub_script = 99
        self.updateProgress.emit(progress_sub_script)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self.progress = 0

        self.scripts['Find_Max'].updateProgress.connect(self._receive_signal)

        self.scripts['StanfordResearch_ESR'].updateProgress.connect(self._receive_signal)

        self.scripts['acquire_image'].updateProgress.connect(self._receive_signal_2)


        self._abort = False
        self.current_stage = None


        esr_settings = self.scripts['StanfordResearch_ESR'].settings
        esr_instruments = self.scripts['StanfordResearch_ESR'].instruments

        nv_locs = self.scripts['select_NVs'].data['nv_locations']

        acquire_image = self.scripts['acquire_image'].scripts['acquire_image']

        if 'image_data' not in acquire_image.data.keys():
            self.log('no image acquired!! Run subscript acquire_image first!!')
            return

        if nv_locs == []:
            self.log('no points selected!! Run subscript select_NVs first!!')
            return

        self.image_data = acquire_image.data['image_data']

        [xVmin, xVmax, yVmax, yVmin] = acquire_image.pts_to_extent(acquire_image.settings['point_a'],
                                                                   acquire_image.settings['point_b'],
                                                                   acquire_image.settings['RoI_mode'])

        self.data = {'image_data': self.image_data,
                     'extent': [xVmin, xVmax, yVmax, yVmin],
                     'nv_locs': nv_locs,
                     'nv_locs_max': [],
                     'ESR_freqs': [],
                     'ESR_data': np.zeros((len(nv_locs), esr_settings['freq_points'])),
                     'NV_image_data': np.zeros((len(nv_locs), self.scripts['Find_Max'].settings['num_points']**2)),
                     'NV_image_extents': np.zeros((len(nv_locs), 4))}

        if self.settings['save']:
            # create and save images
            filename_image = '{:s}\\image\\'.format(self.filename())
            if os.path.exists(filename_image) == False:
                os.makedirs(filename_image)

        self.num_esrs = len(nv_locs)

        for index, pt in enumerate(nv_locs):
            if not self._abort:
                self.plot_pt = pt

                self.current_stage = 'Find_Max'
                self.log('Finding center of point ' + str(index + 1) + ' of ' + str(len(nv_locs)))
                #TODO: remove empirical compensation for click not being centered
                self.scripts['Find_Max'].settings['initial_point'].update({'x': pt[0], 'y': pt[1]-.002})
                if self._abort:
                    break
                self.scripts['Find_Max'].start()
                self.scripts['Find_Max'].wait()
                self.updateProgress.emit(self.progress)
                self.data['NV_image_data'][index] = np.array(self.scripts['Find_Max'].data['image_data'].flatten())
                self.data['NV_image_extents'][index] = self.scripts['Find_Max'].data['extent']


                if self.settings['save']:
                    # create and save images
                    self.scripts['Find_Max'].save_image_to_disk('{:s}\\NV_{:03d}.jpg'.format(filename_image, index))

                self.current_stage = 'ESR'
                self._plot_refresh = True
                self.cur_pt = self.scripts['Find_Max'].data['maximum_point']
                self.data['nv_locs_max'].append(self.cur_pt)
                self.index = index
                self.log('Taking ESR of point ' + str(index + 1) + ' of ' + str(len(nv_locs)))
                #set laser to new point

                self.scripts['move_to_point'].settings['point'].update({'x': self.cur_pt[0], 'y': self.cur_pt[1]})
                self.scripts['move_to_point'].start()

                #run the ESR
                # self.scripts['StanfordResearch_ESR']['instance'].tag = self.scripts['StanfordResearch_ESR']['instance'].tag + '_NV_no_' + index
                if self._abort:
                    break
                self.scripts['StanfordResearch_ESR'].start()
                self.scripts['StanfordResearch_ESR'].wait() #wait for previous ESR thread to complete
                self.updateProgress.emit(self.progress)

                self.data['ESR_freqs'] = self.scripts['StanfordResearch_ESR'].data[-1]['frequency']
                self.data['ESR_data'][index] = self.scripts['StanfordResearch_ESR'].data[-1]['data']

                if self.settings['save']:
                    # create and save images
                    self.scripts['StanfordResearch_ESR'].save_image_to_disk('{:s}\\esr-point_{:03d}.jpg'.format(filename_image, index))

                #can't call run twice on the same object, so start a new, identical ESR script for the next run
                #update: probably not supported, but doesn't seem to have any ill effects
                # self.scripts['StanfordResearch_ESR'] = StanfordResearch_ESR(esr_instruments, settings = esr_settings)
                # self.scripts['StanfordResearch_ESR'].updateProgress.connect(self._receive_signal)

        self.current_stage = 'finished'

        self.updateProgress.emit(100)
        if self.settings['save']:
            self.current_stage = 'saving'
            self.save_b26()
            self.save_data()
            self.save_image_to_disk('{:s}\\nv-map.jpg'.format(filename_image))

        self.scripts['Find_Max'].updateProgress.disconnect(self._receive_signal)

        self.scripts['StanfordResearch_ESR'].updateProgress.disconnect(self._receive_signal)

        self.scripts['acquire_image'].updateProgress.disconnect(self._receive_signal_2)

    def stop(self):
        self._abort = True
        self.scripts['Find_Max'].stop()
        self.scripts['StanfordResearch_ESR'].stop()

    def plot(self, figure_image, figure_ESR):
        if self.current_stage == 'Find_Max':
            axes_image = self.get_axes(figure_image)
            image = self.data['image_data']
            extend = self.data['extent']
            plot_fluorescence(image, extend, axes_image)
            self.scripts['Find_Max'].plot(figure_ESR)
        elif self.current_stage == 'ESR':
            axes_full_image, axes_ESR, axes_zoomed_image = self.get_axes(figure_image, figure_ESR)
            image = self.data['image_data']
            extend = self.data['extent']
            plot_fluorescence(image, extend, axes_full_image)
            if self.scripts['StanfordResearch_ESR'].data:
                if not self.lines == []:
                    for i in range(0,len(self.lines)):
                        self.lines.pop(0).remove()
                self.lines = plot_esr(self.scripts['StanfordResearch_ESR'].data[-1]['fit_params'], self.scripts['StanfordResearch_ESR'].data[-1]['frequency'], self.scripts['StanfordResearch_ESR'].data[-1]['data'], axes_ESR)
            self.scripts['select_NVs'].plot(axes_full_image)
            patch = patches.Circle((self.plot_pt[0], self.plot_pt[1]),
                               1.1 * self.scripts['select_NVs'].settings['patch_size'], fc='r', alpha=.75)
            axes_full_image.add_patch(patch)
            plot_fluorescence(self.scripts['Find_Max'].data['image_data'], self.scripts['Find_Max'].data['extent'], axes_zoomed_image)
            maximum_point = self.scripts['Find_Max'].data['maximum_point']
            patch = patches.Circle((maximum_point[0], maximum_point[1]), .001, ec='r', fc = 'none')
            axes_zoomed_image.add_patch(patch)
            figure_ESR.tight_layout()
        elif self.current_stage in ('finished', 'saving'):
            self._plot_refresh = True
            axes_image = self.get_axes(figure_image)
            image = self.data['image_data']
            extend = self.data['extent']
            plot_fluorescence(image, extend, axes_image)
            self.scripts['select_NVs'].plot(axes_image)

    def get_axes(self, figure1, figure2 = None):
        if self.current_stage == 'ESR':
            if self._plot_refresh == True:
                print('refresh')
                figure1.clf()
                axes1 = figure1.add_subplot(111)

                figure2.clf()
                axes2 = figure2.add_subplot(121)
                axes3 = figure2.add_subplot(122)

                self._plot_refresh = False
                self.lines = []

            else:
                axes1 = figure1.axes[0]
                axes2 = figure2.axes[0]
                axes3 = figure2.axes[1]

            return axes1, axes2, axes3

        else:
            return super(ESR_Selected_NVs, self).get_axes(figure1, figure2)

if __name__ == '__main__':
    script, failed, instruments = Script.load_and_append(script_dict={'ESR_Selected_NVs':'ESR_Selected_NVs'})

    print(script)
    print(failed)
    print(instruments)