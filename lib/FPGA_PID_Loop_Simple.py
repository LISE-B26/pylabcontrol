"""
Created on Wed Oct 22 17:46:08 2014

@author: Jan Gieseler

higher level Python objects, for an example how to use them see run_NI_FPGA_PID.py

"""

from ctypes import c_uint32, c_int32
import helper_functions.sgl2int as sgl2int
import lib.FPGA_PID_Loop_Simple_lib_Wrapper as FPGAlib
import Queue as queue
import numpy as np
from PySide import QtCore

class NI7845R(object):
    session = c_uint32()
    status = c_int32()

    def __init__(self):
        """
        object to establish communication with the NI FPGA
        """
        pass

    def start(self):
        FPGAlib.start_fpga(self.session, self.status)
        if self.status.value != 0:
            print('ERROR IN STARTING FPGA  (ERROR CODE: ', self.status.value, ')')
        return self.status

    def stop(self):
        FPGAlib.stop_fpga(self.session, self.status)

    @property
    def device_temperature(self):
        FPGAlib.read_DeviceTemperature(self.session, self.status)

class NI_FPGA_PI(object):
    def __init__(self, fpga, sample_period_PI = 4e5, gains = {'proportional': 0, 'integral':0}, setpoint = 0, piezo = 0):
        '''

        :param fpga: NI7845R object
        :param PI_gains: dictionary  with values for PI gains {'integral': XX, 'proportional': XX}
        :return:
        '''
        self._fpga = fpga
        self.sample_period_PI = sample_period_PI
        # todo: change statuses into a single dictionary
        self.status_PI = False # PI off at startup
        self.status_LP = False # Lowpass filter off
        self.status_acq = False # acquire data off
        # todo: define function for scaled coefficients for LP and set values
        self.gains = gains
        self.setpoint = setpoint
        self.piezo = piezo

    # ====== DEFINE FUNCTIONS ========================================

    # ====== DEFINE PROPERTIES ========================================
    @property
    def piezo(self):
        '''
        get or set the piezo output. Note that if PI-Loop is active, piezo value can not be changed
        '''
        self._piezo = getattr(FPGAlib, 'read_PiezoOut')(self._fpga.session, self._fpga.status)
        return self._piezo
    @piezo.setter
    def piezo(self, value):
        PIDactive = self.status_PI

        if PIDactive == True:
            print('PID is active, manual piezo control not active!')
            return False
        else:
            self._piezo = value
            return getattr(FPGAlib, 'set_PiezoOut')(self._piezo, self._fpga.session, self._fpga.status)

    @property
    def setpoint(self):
        '''
        set and read the setpoint for the PI_Loop
        '''
        return self._setpoint
    @setpoint.setter
    def setpoint(self, value):
            self._setpoint = value
            return getattr(FPGAlib, 'set_Setpoint')(self._setpoint, self._fpga.session, self._fpga.status)

    @property
    def status_PI(self):
        '''
        activate or read status of PI-Loop (if active or not)
        '''
        self._status_PI = getattr(FPGAlib, 'read_PIDActive')(self._fpga.session, self._fpga.status)
        return self._status_PI
    @status_PI.setter
    def status_PI(self, status):
        self._status_PI = status
        return getattr(FPGAlib, 'set_PIDActive') (self._status_PI, self._fpga.session, self._fpga.status)

    @property
    def status_LP(self):
        '''
        activate or read status of PI-Loop (if active or not)
        '''
        self._status_LP = getattr(FPGAlib, 'read_LowPassActive')(self._fpga.session, self._fpga.status)
        return self._status_PI
    @status_LP.setter
    def status_LP(self, status):
        self._status_LP = status
        return getattr(FPGAlib, 'set_LowPassActive') (self._status_LP, self._fpga.session, self._fpga.status)

    @property
    def detector(self):
        '''
        read detector value
        '''
        # if is_raw_value == True:
        # self._AI1 = getattr(FPGAlib, 'read_AI1')(self._fpga.session, self._fpga.status)
        self._AI1 = getattr(FPGAlib, 'read_AI1_Filtered')(self._fpga.session, self._fpga.status)
        return self._AI1
        # else:
        #     self._AI1_filtered = getattr(FPGAlib, 'read_AI1_Filtered')(self._fpga.session, self._fpga.status)
        #     return self._AI1_filtered

    @property
    def gains(self):
        '''
        set and read gains of PI_Loop
        '''
        return self._gains
    @gains.setter
    def gains(self, gains):
        # map the floating point number to a U32 integer
        self._gains = {'proportional': sgl2int.SGL_to_U32(gains['proportional']), 'integral': sgl2int.SGL_to_U32(gains['integral'])}
        getattr(FPGAlib, 'set_PI_gain_prop') (self._gains['proportional'], self._fpga.session, self._fpga.status)
        getattr(FPGAlib, 'set_PI_gain_int') (self._gains['integral'], self._fpga.session, self._fpga.status)

    @property
    def sample_period_PI(self):
        '''
        set and read sample_period of PI_Loop in ticks (clock cycle is 40MHz)
        '''
        self._sample_period_PI = getattr(FPGAlib, 'read_SamplePeriodsPID')(self._fpga.session, self._fpga.status)
        return self._sample_period_PI
    @sample_period_PI.setter
    def sample_period_PI(self, sample_period_PI):
        self._sample_period_PI = int(sample_period_PI)
        getattr(FPGAlib, "set_SamplePeriodsPID") (self._sample_period_PI, self._fpga.session, self._fpga.status)

    @property
    def loop_rate_limit_PI(self):
        '''
        read status if PI-loop runs slower than expected
        '''
        self._loop_rate_limit_PI = getattr(FPGAlib, 'read_LoopRateLimitPID')(self._fpga.session, self._fpga.status)
        return self._loop_rate_limit_PI

    @property
    def loop_time_PI(self):
        '''
        read duration of PI loop in ticks (clock cycle 40MHz)
        '''
        self._loop_time_PI = getattr(FPGAlib, 'read_LoopTicksPID')(self._fpga.session, self._fpga.status)
        return self._loop_time_PI

class NI_FPGA_READ_FIFO(QtCore.QThread):

    def __init__(self, fpga, data_length, sample_period_acq, block_size = 2 ** 16, timeout_buffer = 100, data_queue=None):
        '''

        :param fpga: NI7845R object
        :param data_length: length of data to be read
        :param sample_period_acq: time period in between samples
        :param block_size: block size of chunks that are read from FPGA
        :param data_queue: queue to which send the reading task
        :return:
        '''
        self._fpga = fpga
        self.block_size = block_size
        self.timeout_buffer = timeout_buffer
        self.data_length = data_length
        self.sample_period_acq = sample_period_acq
        self._status = {}
        self._acquisition_running = False

        QtCore.QThread.__init__(self)

        getattr(FPGAlib, 'set_ElementsToWrite') (self._data_length, self._fpga.session, self._fpga.status)

        if data_queue is None:
            self.data_queue = queue.Queue()
        else:
            self.data_queue = data_queue

    # ===================================================================================
    # ========= PROPETIES ===============================================================
    # ===================================================================================

    @property
    def number_of_reads(self):
        self._number_of_reads = int(np.ceil(1.0 * self.data_length / self.block_size))
        return self._number_of_reads

    @property
    def timeout_buffer(self):
        '''
        set or read number of elements that will be acquired in acquisition
        '''
        return self._timeout_buffer
    @timeout_buffer.setter
    def timeout_buffer(self, value):
        self._timeout_buffer = value
        return getattr(FPGAlib, 'set_TimeoutBuffer') (self._timeout_buffer, self._fpga.session, self._fpga.status)

    @property
    def data_length(self):
        '''
        set or read number of elements that will be acquired in acquisition
        '''
        return self._data_length
    @data_length.setter
    def data_length(self, data_length):
        self._data_length = data_length
        return getattr(FPGAlib, 'set_ElementsToWrite') (self._data_length, self._fpga.session, self._fpga.status)


    @property
    def sample_period_acq(self):
        '''
        set and read sample_period of acquisition in ticks (clock cycle is 40MHz)
        '''
        self._sample_period_acq = getattr(FPGAlib, 'read_SamplePeriodsAcq')(self._fpga.session, self._fpga.status)
        return self._sample_period_acq
    @sample_period_acq.setter
    def sample_period_acq(self, sample_period_acq):
        self._sample_period_acq = sample_period_acq
        getattr(FPGAlib, "set_SamplePeriodsAcq") (self._sample_period_acq, self._fpga.session, self._fpga.status)

    @property
    def block_size(self):
        return self._block_size
    @block_size.setter
    def block_size(self, value):
        self._block_size = value
        self.configure_fifo(value * 2)

    @property
    def status(self):
        self._status['LoopRateLimitAcq'] = bool(getattr(FPGAlib, "read_LoopRateLimitAcq") (self._fpga.session, self._fpga.status))
        self._status['TimeOutAcq'] = bool(getattr(FPGAlib, "read_TimeOutAcq") (self._fpga.session, self._fpga.status))
        self._status['PIDActive'] = bool(getattr(FPGAlib, "read_PIDActive") (self._fpga.session, self._fpga.status))
        self._status['FPGARunning'] = bool(getattr(FPGAlib, "read_FPGARunning") (self._fpga.session, self._fpga.status))
        self._status['DMATimeOut'] = bool(getattr(FPGAlib, "read_DMATimeOut") (self._fpga.session, self._fpga.status))
        self._status['AcquireData'] = bool(getattr(FPGAlib, "read_AcquireData") (self._fpga.session, self._fpga.status))
        self._status['LoopTicksAcq'] = getattr(FPGAlib, 'read_LoopTicksAcq')(self._fpga.session, self._fpga.status)
        self._status['ElementsWritten'] = getattr(FPGAlib, 'read_ElementsWritten') (self._fpga.session, self._fpga.status)
        self._status['AcqTime'] = getattr(FPGAlib, 'read_AcqTime') (self._fpga.session, self._fpga.status)

        return self._status

    # ===================================================================================
    # ========= FUNCTIONS ===============================================================
    # ===================================================================================

    def start_fifo(self):
        FPGAlib.start_FIFO_AI(self._fpga.session, self._fpga.status)

    def stop_fifo(self):
        FPGAlib.stop_FIFO_AI(self._fpga.session, self._fpga.status)

    def configure_fifo(self, fifo_size):
        return FPGAlib.configure_FIFO_AI(fifo_size, self._fpga.session, self._fpga.status)

    def read_fifo_block(self):
        '''
        read a block of data from the FIFO
        :return: data from channels AI1 and AI2 and the elements remaining in the FIFO
        '''
        ai1, ai2, elements_remaining = FPGAlib.read_FIFO_AI(self.block_size, self._fpga.session, self._fpga.status)
        return ai1, ai2, elements_remaining

    def run(self):
        '''
        queue to read data from fifo
        '''

        # reset FIFO
        self.start_fifo()
        # toggle boolean to start acquisition
        getattr(FPGAlib, "set_AcquireData") (True, self._fpga.session, self._fpga.status)

        for i in range(self.number_of_reads):
            data = self.read_fifo_block()
            # todo: emit signal
            self.data_queue.put(data)

