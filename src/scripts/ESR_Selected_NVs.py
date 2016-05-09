from src.core import Script, Parameter
from src.scripts import StanfordResearch_ESR
from src.instruments.NIDAQ import DAQ
import time
import scipy.spatial
import numpy as np
from matplotlib import patches
from PySide.QtCore import Signal, QThread



class ESR_Selected_NVs(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('nv_coor_path', 'Z:/Lab/Cantilever/Measurements/__test_data_for_coding/', str, 'path for NV coordinates'),
        Parameter('nv_coor_tag', 'dummy_tag', str, 'tag for NV coordinates'),
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off')
    ])

    _INSTRUMENTS = {'daq':  DAQ}
    _SCRIPTS = {'StanfordResearch_ESR': StanfordResearch_ESR}

    #updateProgress = Signal(int)

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


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        nv_locs = Script.load_data(self.settings['nv_coor_path'], data_name_in='nv_locations')

        esr_settings = self.scripts['StanfordResearch_ESR']['instance'].settings
        esr_instruments = self.scripts['StanfordResearch_ESR']['instance'].instruments

        for index, pt in enumerate(nv_locs):
            while not self._abort:
                self.log('Taking ESR of point ' + index + ' of ' + len(nv_locs))
                #set laser to new point
                self.instruments['daq']['instance'].AO_init(["ao0","ao1"], pt)
                self.instruments['daq']['instance'].AO_run()
                self.instruments['daq']['instance'].AO_waitToFinish()
                self.instruments['daq']['instance'].AO_stop()

                #run the ESR
                # self.scripts['StanfordResearch_ESR']['instance'].tag = self.scripts['StanfordResearch_ESR']['instance'].tag + '_NV_no_' + index
                self.scripts['StanfordResearch_ESR'].run()
                self.scripts['StanfordResearch_ESR'].wait() #wait for previous ESR thread to complete
                self.scripts['StanfordResearch_ESR'].save_data()

                #can't call run twice on the same object, so start a new, identical ESR script for the next run
                self.scripts['StanfordResearch_ESR'] = StanfordResearch_ESR(esr_instruments, settings = esr_settings)

                #does the GUI get signals from the subprocesses? If not:
                # progress = int(index / len(nv_locs) * 100)
                # self.updateProgress.emit(progress)

        if self.settings['save']:
            self.save()

    def stop(self):
        self._abort = True
        self.scripts['StanfordResearch_ESR'].stop()

    def plot(self, axes):
        self.scripts['StanfordResearch_ESR'].plot(axes)

if __name__ == '__main__':
    from src.core import Instrument

    instruments, instruments_failed = Instrument.load_and_append({'daq':  'DAQ'})

    script, failed, instruments = Script.load_and_append(script_dict={'ESR_Selected_NVs':'ESR_Selected_NVs'}, instruments = instruments)

    # print(script)
    # print(failed)
    print(instruments)