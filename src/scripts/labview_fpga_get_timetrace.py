from src.core import Script, Parameter
from collections import deque
import numpy as np
from src.instruments import NI7845RReadFifo
import time
from copy import deepcopy
from src.labview_fpga_lib.labview_fpga_error_codes import LabviewFPGAException

class LabviewFpgaTimetrace(Script):

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', False, bool,'check to automatically save data'),
        Parameter('dt', 200, int, 'sample period of acquisition loop in ticks (40 MHz)'),
        Parameter('N', 10000, int, 'numer of samples'),
        # Parameter('TimeoutBuffer', 0, int, 'time after which buffer times out in clock ticks (40MHz)'),
        Parameter('BlockSize', 1000, int, 'block size of chunks that are read from FPGA'),
    ])

    _INSTRUMENTS = {'fpga' : NI7845RReadFifo}

    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None, log_function = None, data_path = None):

        Script.__init__(self, name, settings, instruments, log_function= log_function, data_path = data_path)

        self.data = deque()



    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        def calculate_progress(loop_index):
            progress = int(100.0 * loop_index / number_of_reads)
            return progress

        self._recording = True
        self.data.clear() # clear data queue


        # reset FIFO
        self.instruments['fpga'].stop_fifo()
        block_size = self.settings['BlockSize']
        # self.instruments['fpga'].update({'fifo_size' :block_size * 2})
        time.sleep(0.1)
        self.instruments['fpga'].start_fifo()
        time.sleep(0.1)
        number_of_reads = int(np.ceil(1.0 * self.settings['N'] / self.settings['BlockSize']))
        self.log('number_of_reads: {:d}'.format(number_of_reads))
        N_actual = number_of_reads * block_size
        if N_actual!=self.settings['N']:
            self.log('warning blocksize not comensurate with number of datapoints, set N = {:d}'.format(N_actual))
            self.settings.update({'N' : N_actual})
            time.sleep(0.1)

        # apply settings to instrument
        instr_settings = {
            'SamplePeriodsAcq' : self.settings['dt'],
            'ElementsToWrite' : self.settings['N']
            # 'TimeoutBuffer' : self.settings['TimeoutBuffer']
        }
        self.instruments['fpga'].update(instr_settings)
        time.sleep(0.1)
        self.instruments['fpga'].update({'Acquire' : True})

        ai1 = np.zeros(N_actual)
        ai2 = np.zeros(N_actual)
        i = 0
        while i < number_of_reads:
            elem_written = self.instruments['fpga'].ElementsWritten
            if elem_written >= block_size:
                data = self.instruments['fpga'].read_fifo(block_size)

                ai1[i * block_size:(i + 1) * block_size] = deepcopy(data['AI1'])
                ai2[i * block_size:(i + 1) * block_size] = deepcopy(data['AI2'])
                i += 1

                progress = calculate_progress(i)

                self.data.append({
                    'AI1' : ai1,
                    'AI2' : ai2,
                    'elements_remaining': data['elements_remaining']
                })

                self.updateProgress.emit(progress)

        self._recording = False

        if self.settings['save']:
            self.save_b26()


    def _plot(self, axes_list):
        axes = axes_list[0]


        r = self.data[-1]['AI1']
        dt = self.settings['dt']/40e6

        time = dt * np.arange(len(r))
        if max(time)<1e-3:
            time *= 1e6
            xlabel = 'time (us)'
        elif max(time)<1e0:
            time *= 1e3
            xlabel = 'time (ms)'
        elif max(time)<1e3:
            xlabel = 'time (s)'
        elif max(time)<1e6:
            time *= 1e-3
            xlabel = 'time (ks)'
        axes.plot(time, r)
        axes.set_xlabel(xlabel)


if __name__ == '__main__':

    import time
    import numpy as np
    from copy import deepcopy

    fpga = NI7845RReadFifo()

    print(fpga.settings)

    # reset FIFO
    block_size = 2 ** 8

    N = 2 * block_size
    dt = 2000

    time.sleep(0.1)
    print('----stop-----')
    fpga.stop_fifo()
    print('----config-----')
    # fpga.update({'fifo_size': block_size * 2})
    print('----start-----')
    fpga.start_fifo()
    time.sleep(0.1)
    number_of_reads = int(np.ceil(1.0 * N / block_size))
    print('number_of_reads', number_of_reads)
    N_actual = number_of_reads * block_size

    # apply settings to instrument
    instr_settings = {
        'SamplePeriodsAcq': dt,
        'ElementsToWrite': N
    }
    fpga.update(instr_settings)
    time.sleep(0.1)

    print('----------')
    print(fpga.settings)
    print('----------')

    print('ElementsWritten: ', fpga.ElementsWritten)
    fpga.update({'Acquire': True})

    # time.sleep(1)
    print(fpga.settings)

    ai1 = np.zeros(N_actual)
    ai2 = np.zeros(N_actual)
    i = 0
    while i < number_of_reads:
        elem_written = fpga.ElementsWritten
        if elem_written >= block_size:
            data = fpga.read_fifo(block_size)
            # print(i, 'AI1', data['AI1'])
            print(i, 'elements_remaining', data['elements_remaining'])
            ai1[i * block_size:(i + 1) * block_size] = deepcopy(data['AI1'])
            ai2[i * block_size:(i + 1) * block_size] = deepcopy(data['AI2'])
            i += 1

        print('-----', i, '------', 'elem_written', elem_written)

    print(ai1)
    print('------------------------------------------------')
    print(ai2)
