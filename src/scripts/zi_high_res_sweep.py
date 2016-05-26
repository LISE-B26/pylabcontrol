from src.scripts import ZISweeper
import time
from src.core import Script, Parameter, plotting
from PySide.QtCore import Signal, QThread
from collections import deque
import numpy as np
from copy import deepcopy

class ZISweeperHighResolution(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data\\fast', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('high_res_df', 1000, float, 'frequency step of high res. scan'),
        Parameter('high_res_N', 21, int, 'number of data points of high res. scan'),
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'zi sweep' : ZISweeper}

    def __init__(self, scripts, name = None, settings = None, log_function = None, timeout = 1000000000, data_path = None):
        self._recording = False
        self._timeout = timeout

        Script.__init__(self, name, settings, scripts = scripts, log_function= log_function, data_path = data_path)
        QThread.__init__(self)

        self.data = deque()

        # todo: clean this up! and plot data in gui!
        self._sweep_values =  {'frequency' : [], 'x' : [], 'y' : [], 'phase': [], 'r':[]}.keys()


    def _receive_signal(self, progess_sub_script):
        # calculate progress of this script based on progress in subscript

        if self.current_subscript == 'quick scan':
            progress = int(self.weights['quick scan'] * progess_sub_script)
        elif self.current_subscript == 'high res scan':
            progress = int(self.weights['quick scan']*100 + self.weights['high res scan'] * progess_sub_script)
        else:
            progress = None
        # if calculated progress is 100 force it to 99, because we still have to save before script is finished
        if progress>= 100:
            progress = 99

        if progress is not None:
            self.updateProgress.emit(progress)

        if progess_sub_script == 100:
            self.current_subscript = None

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """



        def calculate_weights():
            """
            calculate a weight inversely proportional to the expected to duration of the two steps in the
            script

            Returns: weights as a dictionary for the two steps

            """
            weights = {}


            # estimate run time of step 1 (fast sweep)
            f_range = sweeper_script.settings['stop'] - sweeper_script.settings['start']
            N_samples = sweeper_script.settings['samplecount']
            df = f_range / N_samples

            t = N_samples / df

            weights['quick scan'] = t

            # estimate run time of step 2 (high res sweep)
            df = self.settings['high_res_df']
            N_samples = self.settings['high_res_N']

            t = N_samples / df

            weights['high res scan'] = t


            total_time = sum([v for k, v in weights.iteritems()])

            weights = {k: v/total_time for k, v in weights.iteritems()}

            print('weights',weights)

            return weights

        def run_scan(name):
            self.current_subscript = name
            sweeper_script.start()
            while self.current_subscript is name:
                time.sleep(0.1)

        def calc_new_range():


            df = self.settings['high_res_df']
            N = self.settings['high_res_N']

            r = sweeper_script.data[-1]['r']
            freq = sweeper_script.data[-1]['frequency']
            freq = freq[np.isfinite(r)]
            r = r[np.isfinite(r)]

            fo = freq[np.argmax(r)]

            f_start, f_end = fo - N/2 *df, fo + N/2 *df


            # make sure that we convert back to native python types (numpy file types don't pass the Parameter validation)
            return float(f_start), float(f_end), int(N)


        sweeper_script = self.scripts['zi sweep']
        #save initial settings, so that we can rest at the end of the script
        initial_settings = deepcopy(sweeper_script.settings)
        self.weights = calculate_weights()

        # take the signal from the subscript and route it to a function that takes care of it
        sweeper_script.updateProgress.connect(self._receive_signal)

        print('====== start quick scan ============')

        run_scan('quick scan')

        print('====== calculate new scan range ====')
        f_start, f_stop, N = calc_new_range()

        print('f_start, f_stop, N', f_start, f_stop, N)

        print('====== update sweeper ==============')
        sweeper_script.update({
            'start' : f_start,
            'stop' : f_stop,
            'samplecount' : N
        })

        print('====== start high res scan =========')
        # print(sweeper_script.sweeper.finished())
        # print(sweeper_script.sweeper.progress())

        run_scan('high res scan')

        sweeper_script.updateProgress.disconnect()
        self.data = sweeper_script.data[-1]

        self._recording = False

        if self.settings['save']:
            self.save()

        # set the sweeper script back to initial settings
        sweeper_script.update(initial_settings)
        # make sure that progess is set 1o 100 because we check that in the old_gui
        self.updateProgress.emit(100)


    def plot(self, axes):
        if self.current_subscript == 'quick scan' and self.scripts['zi sweep'].data:
            self.scripts['zi sweep'].plot(axes)
        elif self.current_subscript in ('high res scan', None) and self.data:
            r = self.data['r']
            freq = self.data['frequency']
            freq = freq[np.isfinite(r)]
            r = r[np.isfinite(r)]
            plotting.plot_psd(freq, r, axes, False)

