from src.core import Script, Parameter
from src.scripts import StanfordResearch_ESR, Select_NVs_Simple, GalvoScan
from src.instruments.NIDAQ import DAQ
import time
import scipy.spatial
import numpy as np
from matplotlib import patches
from PySide.QtCore import Signal, QThread
from src.core.plotting import plot_fluorescence



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

    def __init__(self, instruments = None, scripts = None, name = None, settings = None,  log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False

        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_output = log_output)

        QThread.__init__(self)

        self._plot_type = 2

        self.index = 0

        self.scripts['StanfordResearch_ESR'].updateProgress.connect(self._receive_signal)

        self.data = None

    def _receive_signal(self, progress_sub_script):
        # calculate progress of this script based on progress in subscript

        progress = int((float(self.index)/self.num_esrs)*100 + float(progress_sub_script)/self.num_esrs)
        self.updateProgress.emit(progress)


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self._abort = False

        nv_locs = self.scripts['select_NVs'].data['nv_locations']

        if self.scripts['acquire_image'].plotting_data == None:
            self.log('no image acquired!! Run subscript acquire_image first!!')

        if nv_locs == []:
            self.log('no points selected acquired!! Run subscript select_NVs first!!')

        xVmin = min(self.scripts['acquire_image'].settings['point_a']['x'], self.scripts['acquire_image'].settings['point_b']['x'])
        xVmax = max(self.scripts['acquire_image'].settings['point_a']['x'], self.scripts['acquire_image'].settings['point_b']['x'])
        yVmin = min(self.scripts['acquire_image'].settings['point_a']['y'], self.scripts['acquire_image'].settings['point_b']['y'])
        yVmax = max(self.scripts['acquire_image'].settings['point_a']['y'], self.scripts['acquire_image'].settings['point_b']['y'])

        self.data = {'image_data': self.scripts['acquire_image'].plotting_data,
                     'extent' :  [xVmin, xVmax, yVmin, yVmax],
                     'nv_locs': nv_locs,
                     'ESR_freqs': [],
                     'ESR_data': np.zeros((len(nv_locs)))}

        for index, pt in enumerate(nv_locs):
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
                # self.scripts['StanfordResearch_ESR']['instance'].tag = self.scripts['StanfordResearch_ESR']['instance'].tag + '_NV_no_' + index
                self.scripts['StanfordResearch_ESR'].run()
                self.scripts['StanfordResearch_ESR'].wait() #wait for previous ESR thread to complete

                self.data['ESR_freqs'] = self.scripts['StanfordResearch_ESR'].data[-1]['frequency']
                self.data['ESR_data'][index] = self.scripts['StanfordResearch_ESR'].data[-1]['data']

                #can't call run twice on the same object, so start a new, identical ESR script for the next run
                #update: probably not supported, but doesn't seem to have any ill effects
                # self.scripts['StanfordResearch_ESR'] = StanfordResearch_ESR(esr_instruments, settings = esr_settings)
                # self.scripts['StanfordResearch_ESR'].updateProgress.connect(self._receive_signal)



        self.updateProgress.emit(100)
        if self.settings['save']:
            self.save()
            self.save_data()

    def stop(self):
        self._abort = True
        self.scripts['StanfordResearch_ESR'].stop()

    def plot(self, axes_Image, axes_ESR = None):
        if self.data is not None:

            image = self.data['image_data'].image_data
            extend = self.data['extend'].image_data
            plot_fluorescence(image, extend, axes_Image)

        if self.isRunning():
            patch = patches.Circle((self.cur_pt[0], self.cur_pt[1]), .0005, fc='r')
            axes_Image.add_patch(patch)
        else:
            for pt in self.data['nv_locs']:
                patch = patches.Circle((pt[0], pt[1]), .0005, fc='b')
                axes_Image.add_patch(patch)

        if axes_ESR is not None:
            self.scripts['StanfordResearch_ESR'].plot(None, axes_ESR)



if __name__ == '__main__':
    from src.core import Instrument

    instruments, instruments_failed = Instrument.load_and_append({'daq':  'DAQ'})

    script, failed, instruments = Script.load_and_append(script_dict={'ESR_Selected_NVs':'ESR_Selected_NVs'}, instruments = instruments)

    # print(script)
    # print(failed)
    print(instruments)