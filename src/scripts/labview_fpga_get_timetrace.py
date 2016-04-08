from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from collections import deque
import numpy as np
from src.instruments import NI7845RPidSimpleLoop
import time
class LabviewFpgaTimetrace(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('dt', 200, int, 'sample period of acquisition loop in ticks (40 MHz)'),
        Parameter('N', 200, int, 'numer of samples'),
        Parameter('TimeoutBuffer', 0, int, 'time after which buffer times out in clock ticks (40MHz)'),
        Parameter('BlockSize', 1000, int, 'block size of chunks that are read from FPGA'),
    ])

    _INSTRUMENTS = {'fpga' : NI7845RPidSimpleLoop}

    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None, log_output = None):

        self._recording = False

        Script.__init__(self, name, settings, instruments, log_output = log_output)
        QThread.__init__(self)

        self.data = deque()



    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        self._recording = True
        self.data.clear() # clear data queue

        block_size = self.settings['BlockSize']
        number_of_reads = int(np.ceil(1.0 * self.settings['N'] / self.settings['BlockSize']))

        N_actual = number_of_reads * block_size
        if N_actual!=self.settings['N']:
            self.log('warning blocksize not comensurate with number of datapoints, set N = {:d}'.format(N_actual))
            self.settings.update({'N' : N_actual})

        # apply settings to instrument
        instr_settings = {
            'SamplePeriodsAcq' : self.settings['SamplePeriodsAcq'],
            'ElementsToWrite' : self.settings['N'],
            'TimeoutBuffer' : self.settings['TimeoutBuffer']

        }
        self.instruments['fpga'].update(instr_settings)
        time.sleep(0.1)
        self.instruments['fpga'].update({'AcquireData' : True})

        def calculate_progress(loop_index):
            progress = int(100.0 * loop_index / number_of_reads)

        ai1 = np.zeros(N_actual)
        for i in range(number_of_reads):
            data = self.instruments['fpga'].read_fifo(block_size)
            ai1[i* block_size:(i+1)*block_size] = data['AI1']
            # append data to queue
            self.data.put({
                'AI1' : ai1
            })

            progress = calculate_progress(i)

            self.updateProgress.emit(progress)

        self._recording = False
        progress = 100 # make sure that progess is set 1o 100 because we check that in the old_gui

        if self.settings['save']:
            self.save()


    def plot(self, axes):

        r = self.data[-1]['AI1']
        axes.plot(r)