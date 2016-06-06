import numpy as np
from PySide.QtCore import Signal, QThread
from matplotlib import patches

from src.core import Script, Parameter
from src.instruments.NIDAQ import DAQ
from src.plotting.plots_2d import plot_fluorescence
from src.scripts import StanfordResearch_ESR, Correlate_Images, AutoFocus, Select_NVs_Simple, GalvoScan
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
        Parameter('num_between_autofocus', -1, int, 'Number of ESRs between autofocuses, -1 to deactivate autofocus'),
        Parameter('autofocus_size', .1, float, 'Side length of autofocusing square in Volts')
    ])

    _INSTRUMENTS = {'daq':  DAQ}
    _SCRIPTS = {'StanfordResearch_ESR': StanfordResearch_ESR,
                'Correlate_Images': Correlate_Images,
                'AF': AutoFocus,
                'Find_Max': FindMaxCounts2D,
                'select_NVs': Select_NVs_Simple,
                'acquire_image': GalvoScan}

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

        self.progress = 0

        self.scripts['AF'].updateProgress.connect(self._receive_signal)

        self.scripts['Correlate_Images'].updateProgress.connect(self._receive_signal)

        self.scripts['Find_Max'].updateProgress.connect(self._receive_signal)

        self.scripts['StanfordResearch_ESR'].updateProgress.connect(self._receive_signal)

        self.scripts['acquire_image'].updateProgress.connect(self._receive_signal_2)

        self.scripts['AF'].log_function = self.log_function
        self.scripts['acquire_image'].log_function = self.log_function
        self.scripts['Correlate_Images'].log_function = self.log_function
        self.scripts['Find_Max'].log_function = self.log_function
        self.scripts['StanfordResearch_ESR'].log_function = self.log_function

        self.current_stage = 'init'

    def _receive_signal(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript

        if self.current_stage == 'ESR':
            self.progress = int((float(self.index)/self.num_esrs)*100 + float(progress_sub_script)/self.num_esrs)
        self.updateProgress.emit(self.progress)

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
        self.current_stage = None

        af_index = 1
        corr_index = 1

        esr_settings = self.scripts['StanfordResearch_ESR'].settings
        esr_instruments = self.scripts['StanfordResearch_ESR'].instruments

        nv_locs = self.scripts['select_NVs'].data['nv_locations']

        acquire_image = self.scripts['acquire_image']

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
                if (not self.settings['num_between_autofocus'] == -1) and (af_index == self.settings['num_between_autofocus']):
                    self.current_stage = 'Autofocus'
                    self.log('Autofocusing on point ' + str(index + 1) + ' of ' + str(len(nv_locs)))
                    daq_pt = np.transpose(np.column_stack((pt[0], pt[1])))
                    daq_pt = (np.repeat(daq_pt, 2, axis=1))

                    x_min = pt[0] - self.settings['autofocus_size']/2
                    x_max = pt[0] + self.settings['autofocus_size']/2
                    y_min = pt[1] - self.settings['autofocus_size']/2
                    y_max = pt[1] + self.settings['autofocus_size']/2
                    self.scripts['AF'].scripts['take_image'].settings['point_a'].update({'x': x_min, 'y': y_min})
                    self.scripts['AF'].scripts['take_image'].settings['point_b'].update({'x': x_max, 'y': y_max})

                    if self._abort:
                        break

                    self.scripts['AF'].run()
                    self.scripts['AF'].wait()

                    self.instruments['daq']['instance'].AO_init(["ao0", "ao1"], daq_pt)
                    self.instruments['daq']['instance'].AO_run()
                    self.instruments['daq']['instance'].AO_waitToFinish()
                    self.instruments['daq']['instance'].AO_stop()
                    self.updateProgress.emit(self.progress)

                    af_index = 0
                if (not self.settings['num_between_correlate'] == -1) and (self.corr_index == self.settings['num_between_correlate']):
                    self.current_stage = 'Correlate'
                    self.log('Correlating for point ' + str(index + 1) + ' of ' + str(len(nv_locs)))
                    self.scripts['Correlate_Images'].settings['new_image_center'] = pt
                    if self._abort:
                        break
                    self.scripts['Correlate_Images'].run()
                    self.scripts['Correlate_Images'].wait()
                    self.updateProgress.emit(self.progress)
                    pt = self.scripts['Correlate_Images'].shift_coordinates(pt)
                    self.scripts['Correlate_Images'].settings['reset'] = False

                self.current_stage = 'Find_Max'
                self.log('Finding center of point ' + str(index + 1) + ' of ' + str(len(nv_locs)))
                self.scripts['Find_Max'].settings['initial_point'].update({'x': pt[0], 'y': pt[1]})
                if self._abort:
                    break
                self.scripts['Find_Max'].run()
                self.scripts['Find_Max'].wait()
                self.updateProgress.emit(self.progress)
                self.data['NV_image_data'][index] = np.array(self.scripts['Find_Max'].data['image_data'].flatten())
                self.data['NV_image_extents'][index] = self.scripts['Find_Max'].data['extent']


                if self.settings['save']:
                    # create and save images
                    self.scripts['Find_Max'].save_image_to_disk('{:s}\\NV_{:03d}.jpg'.format(filename_image, index))

                self.current_stage = 'ESR'
                # self.cur_pt = self.scripts['Find_Max'].data['maximum_points']
                self.cur_pt = pt
                self.index = index
                self.log('Taking ESR of point ' + str(index + 1) + ' of ' + str(len(nv_locs)))
                #set laser to new point
                daq_pt = np.transpose(np.column_stack((pt[0], pt[1])))
                daq_pt = (np.repeat(daq_pt, 2, axis=1))
                self.instruments['daq']['instance'].AO_init(["ao0","ao1"], daq_pt)
                self.instruments['daq']['instance'].AO_run()
                self.instruments['daq']['instance'].AO_waitToFinish()
                self.instruments['daq']['instance'].AO_stop()

                #run the ESR
                # self.scripts['StanfordResearch_ESR']['instance'].tag = self.scripts['StanfordResearch_ESR']['instance'].tag + '_NV_no_' + index
                if self._abort:
                    break
                self.scripts['StanfordResearch_ESR'].run()
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

                af_index += 1

        self.current_stage = 'finished'

        self.updateProgress.emit(100)
        if self.settings['save']:
            self.current_stage = 'saving'
            self.save_b26()
            self.save_data()
            self.save_image_to_disk('{:s}\\nv-map.jpg'.format(filename_image))

    def stop(self):
        self._abort = True
        self.scripts['AF'].stop()
        self.scripts['Correlate_Images'].stop()
        self.scripts['Find_Max'].stop()
        self.scripts['StanfordResearch_ESR'].stop()

    def plot(self, axes_Image, axes_ESR):
        image = self.data['image_data']
        extend = self.data['extent']
        plot_fluorescence(image, extend, axes_Image)

        if self.current_stage == 'Autofocus':
            self.scripts['AF'].plot(axes_Image, axes_ESR)
            self.scripts['select_NVs'].plot(axes_Image)
        elif self.current_stage == 'Correlate':
            self.scripts['Correlate_Images'].plot(axes_Image, axes_ESR)
        elif self.current_stage == 'Find_Max':
            self.scripts['Find_Max'].plot(axes_ESR)
        elif self.current_stage == 'ESR':
            self.scripts['StanfordResearch_ESR'].plot(axes_ESR)
            self.scripts['select_NVs'].plot(axes_Image)
            patch = patches.Circle((self.plot_pt[0], self.plot_pt[1]),
                               1.1 * self.scripts['select_NVs'].settings['patch_size'], fc='r', alpha=.75)
            axes_Image.add_patch(patch)
        if self.current_stage in ('finished', 'saving'):
            self.scripts['select_NVs'].plot(axes_Image)

if __name__ == '__main__':
    from src.core import Instrument

    script, failed, instruments = Script.load_and_append(script_dict={'ESR_Selected_NVs':'ESR_Selected_NVs'})

    print(script)
    print(failed)
    print(instruments)