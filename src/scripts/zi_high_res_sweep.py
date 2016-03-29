from src.scripts import ZISweeper
import time
from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from collections import deque

class ZISweeperHighResolution(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('high_res_df', 1.0, float, 'frequency step of high res. scan'),
        Parameter('high_res_N', 10, int, 'number of data points of high res. scan'),
    ])

    _INSTRUMENTS = {}

    _SCRIPTS = {'zi sweep' : ZISweeper}

    def __init__(self, scripts, name = None, settings = None, timeout = 1000000000):
        self._recording = False
        self._timeout = timeout

        Script.__init__(self, name, settings, scripts = scripts)
        QThread.__init__(self)

        self.data = deque()

        # todo: clean this up! and plot data in gui!
        self._sweep_values =  {'frequency' : [], 'x' : [], 'y' : [], 'phase': [], 'r':[]}.keys()


    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        def receive_signal(progess):
            print('progess', progess, self.subscript_is_running)
            if progess == 100:
                self.current_subscript = None

        def calculate_weights():
            """
            calculate a weight proportional to the expected to duration of the two steps in the
            script

            Returns:

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

            print(weights)

            return weights

        def run_scan(name):
            self.current_subscript = name
            sweeper_script.start()
            while self.current_subscript is not None:
                time.sleep(0.1)

        def calc_new_range():


            df = self.settings['high_res_df']
            N = self.settings['high_res_N']
            fo = None

            f_start, f_end = fo - N/2 *df, fo + N/2 *df
            return f_start, f_end, N



        weights = calculate_weights()

        sweeper_script = self.scripts['zi sweep']

        # take the signal from the subscript and route it to a function that takes care of it
        sweeper_script.updateProgress.connect(receive_signal)

        # ====== start quick scan ============
        self.current_subscript = 'quick scan'
        run_scan()

        # ====== calculate new scan range ====
        f_start, f_stop, N = calc_new_range()

        # ====== update sweeper ==============
        sweeper_script.update({
            'start' : f_start,
            'stop' : f_stop,
            'samplecount' : N
        })
        # ====== start high res scan =========
        self.current_subscript = 'high res scan'
        run_scan()


        # f_range = sweeper_script.settings['stop'] - sweeper_script.settings['start']
        # N_samples = sweeper_script.settings['samplecount']
        # df = f_range / N_samples
        #
        # self.subscript_is_running = True
        # self.current_subscript = 'high res scan'
        # sweeper_script.update('')
        # sweeper_script.start()
        #
        # # wait until finished
        # while self.subscript_is_running:
        #     print('runnning subscript')
        #     time.sleep(0.1)
        #
        # print('DONE!!!')

        #
        # if self.sweeper.finished():
        #     self._recording = False
        #     progress = 100 # make sure that progess is set 1o 100 because we check that in the old_gui
        #
        #     if self.settings['save']:
        #         self.save()