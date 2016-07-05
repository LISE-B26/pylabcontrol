from src.core import Script, Parameter
from src.scripts import Take_And_Correlate_Images_2, AutoFocus
import os


class Refind_NVs(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', '', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', False, bool, 'save data on/off'),
        Parameter('activate_correlation', True, bool, 'perform correlation'),
        Parameter('activate_autofocus', True, bool, 'perform autofocus')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {'Correlate_Images': Take_And_Correlate_Images_2,
                'AF': AutoFocus}

    def __init__(self, instruments = None, scripts = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)

        self.index = 0

        self.scripts['AF'].log_function = self.log_function
        self.scripts['Correlate_Images'].log_function = self.log_function

        self.data = {'baseline_image': [],
                     'baseline_extent': [],
                     'new_image': [],
                     'baseline_nv_locs': [],
                     'new_nv_locs': []}

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

        self.scripts['AF'].updateProgress.connect(self._receive_signal)

        self.scripts['Correlate_Images'].updateProgress.connect(self._receive_signal)

        self.current_stage = None

        if self.settings['save']:
            # create and save images
            filename_image = '{:s}\\image\\'.format(self.filename())
            if os.path.exists(filename_image) == False:
                os.makedirs(filename_image)

        if self.settings['activate_autofocus']:
            self.current_stage = 'Autofocus'

            self.scripts['AF'].run()

            self.updateProgress.emit(50)

        if self.settings['activate_correlation']:
            self.current_stage = 'Correlate'
            # code for Correlate_Images
            # self.log('Correlating for point ' + str(index + 1) + ' of ' + str(len(nv_locs)))
            # self.scripts['Correlate_Images'].settings['new_image_center'] = pt
            # if self._abort:
            #     break
            # self.scripts['Correlate_Images'].run()
            # self.scripts['Correlate_Images'].wait()
            # self.updateProgress.emit(self.progress)
            # pt = self.scripts['Correlate_Images'].shift_coordinates(pt)
            # self.scripts['Correlate_Images'].settings['reset'] = False
            self.log('Correlating images')
            if self.data['baseline_image'] == []:
                self.log('No baseline image avaliable. Script will exit.')
                return
            elif self.data['baseline_extent'] == []:
                self.log('No image extent avaliable. Script will exit.')
                return
            elif self.data['baseline_nv_locs'] == []:
                self.log('No nv list avaliable. Script will exit.')
                return

            self.scripts['Correlate_Images'].data['baseline_image'] = self.data['baseline_image']
            self.scripts['Correlate_Images'].data['image_extent'] = self.data['baseline_extent']
            self.scripts['Correlate_Images'].data['old_nv_list'] = self.data['baseline_nv_locs']

            self.scripts['Correlate_Images'].run()

            self.data['new_nv_locs'] = self.scripts['Correlate_Images'].data['new_NV_list']
            self.data['new_image'] = self.scripts['Correlate_Images'].data['new_image']


        self.current_stage = 'finished'

        if self.settings['save']:
            self.current_stage = 'saving'
            self.save_b26()
            self.save_data()

        self.scripts['AF'].updateProgress.disconnect(self._receive_signal)

        self.scripts['Correlate_Images'].updateProgress.disconnect(self._receive_signal)


    def stop(self):
        self._abort = True
        self.scripts['AF'].stop()
        self.scripts['Correlate_Images'].stop()

    def plot(self, figure_list):
        if self.current_stage == 'Autofocus':
            self.scripts['AF'].plot(figure_list)
        elif self.current_stage == 'Correlate':
            self.scripts['Correlate_Images'].plot(figure_list)

if __name__ == '__main__':
    from src.core import Instrument

    script, failed, instruments = Script.load_and_append(script_dict={'Refind_NVs':'Refind_NVs'})

    print(script)
    print(failed)
    print(instruments)