import numpy as np
from matplotlib import patches

from src.core import Script, Parameter
from src.plotting.plots_1d import plot_esr
from src.plotting.plots_2d import plot_fluorescence_new, update_fluorescence
from src.scripts import StanfordResearch_ESR, Select_NVs_Simple, GalvoScanWithLightControl, SetLaser
from src.scripts import FindMaxCounts2D
import os


class ESR_Selected_NVs(Script):

    _DEFAULT_SETTINGS = []
    _INSTRUMENTS = {}
    _SCRIPTS = {'StanfordResearch_ESR': StanfordResearch_ESR,
                'Find_Max': FindMaxCounts2D,
                'select_NVs': Select_NVs_Simple,
                'acquire_image': GalvoScanWithLightControl,
                'move_to_point': SetLaser}


    def __init__(self, instruments = None, scripts = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """

        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)

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
                self._plot_refresh = True
                self.scripts['Find_Max'].run()
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
                self.scripts['move_to_point'].run()

                #run the ESR
                # self.scripts['StanfordResearch_ESR']['instance'].tag = self.scripts['StanfordResearch_ESR']['instance'].tag + '_NV_no_' + index
                if self._abort:
                    break
                self.scripts['StanfordResearch_ESR'].run()
                self.updateProgress.emit(self.progress)

                self.data['ESR_freqs'] = self.scripts['StanfordResearch_ESR'].data[-1]['frequency']
                self.data['ESR_data'][index] = self.scripts['StanfordResearch_ESR'].data[-1]['data']

                if self.settings['save']:
                    # create and save images
                    print('SAVING')
                    print(filename_image)
                    self.scripts['StanfordResearch_ESR'].save_image_to_disk('{:s}\\esr-point_{:03d}.jpg'.format(filename_image, index))

                #can't call run twice on the same object, so start a new, identical ESR script for the next run
                #update: probably not supported, but doesn't seem to have any ill effects
                # self.scripts['StanfordResearch_ESR'] = StanfordResearch_ESR(esr_instruments, settings = esr_settings)
                # self.scripts['StanfordResearch_ESR'].updateProgress.connect(self._receive_signal)

        self.current_stage = 'finished'

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

    def _plot(self, axes_list):
        if self.current_stage == 'Find_Max':
            axes_image = axes_list[2]
            image = self.data['image_data']
            extend = self.data['extent']
            plot_fluorescence_new(image, extend, axes_image)

        elif self.current_stage == 'ESR':
            [axes_full_image, axes_ESR, axes_zoomed_image] = axes_list
            image = self.data['image_data']
            extend = self.data['extent']
            plot_fluorescence_new(image, extend, axes_full_image)
            if self.scripts['StanfordResearch_ESR'].data:
                plot_esr(axes_ESR,
                         self.scripts['StanfordResearch_ESR'].data[-1]['frequency'],
                         self.scripts['StanfordResearch_ESR'].data[-1]['data'],
                         self.scripts['StanfordResearch_ESR'].data[-1]['fit_params'])

            # todo: tightlayout warning test it this avoids the warning:
            axes_ESR.get_figure().set_tight_layout(True)
            # axes_ESR.get_figure().tight_layout()
            self.scripts['select_NVs'].plot([axes_full_image.get_figure()])
            patch = patches.Circle((self.plot_pt[0], self.plot_pt[1]),
                               1.1 * self.scripts['select_NVs'].settings['patch_size'], fc='r', alpha=.75)
            axes_full_image.add_patch(patch)
            plot_fluorescence_new(self.scripts['Find_Max'].data['image_data'], self.scripts['Find_Max'].data['extent'], axes_zoomed_image)
            maximum_point = self.scripts['Find_Max'].data['maximum_point']
            patch = patches.Circle((maximum_point[0], maximum_point[1]), .001, ec='r', fc = 'none')
            axes_zoomed_image.add_patch(patch)
        elif self.current_stage in ('finished', 'saving'):
            axes_image = axes_list[0]
            image = self.data['image_data']
            extend = self.data['extent']
            plot_fluorescence_new(image, extend, axes_image)
            self.scripts['select_NVs'].plot([axes_image.get_figure()])
        elif self.current_stage == 'init':
            pass
        else:
            print('current_stage FAILED', self.current_stage)
            raise KeyError

    def _update_plot(self, axes_list):
        if self.current_stage == 'Find_Max':
            axes_image = axes_list[0]
            image = self.data['image_data']
            update_fluorescence(image, axes_image)
        elif self.current_stage == 'ESR':
            [_, axes_ESR, _] = axes_list
            if self.scripts['StanfordResearch_ESR'].data:
                plot_esr(axes_ESR,
                         self.scripts['StanfordResearch_ESR'].data[-1]['frequency'],
                         self.scripts['StanfordResearch_ESR'].data[-1]['data'],
                         self.scripts['StanfordResearch_ESR'].data[-1]['fit_params']
                         )
                axes_ESR.get_figure().tight_layout()
        elif self.current_stage in ('finished', 'saving'):
            pass  # should never update in the saving/finished stage

    def get_axes_layout(self, figure_list):
        if self.current_stage in ('Find_Max', 'ESR'):
            axes1 = figure_list[0].axes[0]
            figure2 = figure_list[1]
            if self._plot_refresh is True:
                figure2.clf()
                axes2 = figure2.add_subplot(121)
                axes3 = figure2.add_subplot(122)
            else:
                axes2 = figure2.axes[0]
                axes3 = figure2.axes[1]

            return [axes1, axes2, axes3]

        else:
            return super(ESR_Selected_NVs, self).get_axes_layout([figure_list[0]])

if __name__ == '__main__':
    script, failed, instruments = Script.load_and_append(script_dict={'ESR_Selected_NVs':'ESR_Selected_NVs'})

    print(script)
    print(failed)
    print(instruments)