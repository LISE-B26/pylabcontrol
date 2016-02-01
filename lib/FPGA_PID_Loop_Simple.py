"""
Created on Wed Oct 22 17:46:08 2014

@author: Jan Gieseler

higher level Python objects, for an example how to use them see run_NI_FPGA_PID.py

"""

from ctypes import c_uint32, c_int32
import helper_functions.sgl2int as sgl2int
import lib.FPGA_PID_Loop_Simple_lib_Wrapper as FPGAlib


class NI7845R(object):
    session = c_uint32()
    status = c_int32()

    def __init__(self):
        pass

    def start(self):
        FPGAlib.start_fpga(self.session, self.status)
        return self.status

    def stop(self):
        FPGAlib.stop_fpga(self.session, self.status)

    @property
    def device_temperature(self):
        FPGAlib.read_DeviceTemperature(self.session, self.status)
#
#
# class FIFOAnalogInput(object):
#     _fpga = None
#     _block_size = None
#     _acquisition_running = False
#
#     thread = None
#
#     def __init__(self, fpga, data_queue=None):
#         self._fpga = fpga
#         self.block_size = 2 ** 16
#
#         self.time_reference = numpy.datetime64(int(time.time() * 1e6), 'us')
#
#         if data_queue is None:
#             self.data_queue = queue.Queue()
#         else:
#             self.data_queue = data_queue
#
#     @property
#     def block_size(self):
#         return self._block_size
#
#     @block_size.setter
#     def block_size(self, value):
#         self._block_size = value
#
#         self.configure_fifo(value * 2)
#
#     @property
#     def block_time(self):
#         return self.block_size * (fpga_binder.read_LoopTicks() *
#                                   numpy.timedelta64(25, 'ns'))
#
#     @property
#     def acquisition_running(self):
#         return self._acquisition_running
#
#     def start_fifo(self):
#         fpga_binder.start_FIFO_AI(self._fpga.session, self._fpga.status)
#
#         # start point of acquisition
#         self.time_reference = numpy.datetime64(int(time.time() * 1e6), 'us')
#
#     def stop_fifo(self):
#         fpga_binder.stop_FIFO_AI(self._fpga.session, self._fpga.status)
#
#     def configure_fifo(self, fifo_size):
#         return fpga_binder.configure_FIFO_AI(fifo_size, self._fpga.session,
#                                              self._fpga.status)
#
#     def start_acquisition(self):
#         if not self._acquisition_running:
#             self._acquisition_running = True
#             self.thread = threading.Thread(target=self.run)
#
#             self.start_fifo()
#             self.thread.start()
#
#     def stop_acquisition(self):
#         if self._acquisition_running:
#             self._acquisition_running = False
#             self.thread.join()
#             self.stop_fifo()
#
#     def read_fifo_block(self):
#         ai0, ai1, ai2, times = fpga_binder.read_FIFO_conv(
#             self.block_size, self._fpga.session, self._fpga.status)
#
#         times = numpy.array(times * 1e9, dtype='timedelta64[ns]')
#
#         total_block_time = times[-1]
#         times = times + self.time_reference
#         self.time_reference = self.time_reference + total_block_time
#
#         return ai0, ai1, ai2, times
#
#     def run(self):
#         # the first block is weird sometimes, drop it
#         self.read_fifo_block()
#
#         while self._acquisition_running:
#             data = self.read_fifo_block()
#
#             self.data_queue.put(data)

class NI_FPGA_PI(object):
    def __init__(self, fpga, sample_period_PI = 4e5, sample_period_acq = 800, gains = {'proportional': 0, 'integral':0}, setpoint = 0, piezo = 0):
        '''

        :param fpga: NI7845R object
        :param PI_gains: dictionary  with values for PI gains {'integral': XX, 'proportional': XX}
        :return:
        '''
        self._fpga = fpga
        self.sample_period_PI = sample_period_PI
        self.sample_period_acq = sample_period_acq
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
    @status_PI.setter
    def status_LP(self, status):
        self._status_LP = status
        return getattr(FPGAlib, 'set_LowPassActive') (self._status_LP, self._fpga.session, self._fpga.status)

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
    def data_written(self):
        '''
        set or read number of elements that were written to buffer during acquisition
        '''
        self._data_written = getattr(FPGAlib, 'read_ElementsToWrite') (self._data_written, self._fpga.session, self._fpga.status)
        return self._data_written

    @property
    def status_acq(self):
        '''
        activate or read status of data acquisition (if active or not)
        '''
        self._status_acq = getattr(FPGAlib, 'read_AcquireData')(self._fpga.session, self._fpga.status)
        return self._status_PI
    @status_acq.setter
    def status_acq(self, status):
        self._status_acq = status
        return getattr(FPGAlib, 'set_AcquireData') (self._status_acq, self._fpga.session, self._fpga.status)

    @property
    def detector(self):
        '''
        read detector value
        '''
        # if is_raw_value == True:
        self._AI1 = getattr(FPGAlib, 'read_AI1')(self._fpga.session, self._fpga.status)
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
    def loop_rate_limit_acq(self):
        '''
        read status if acquistion-loop runs slower than expected
        '''
        self._loop_rate_limit_acq = getattr(FPGAlib, 'read_LoopRateLimitAcq')(self._fpga.session, self._fpga.status)
        return self._loop_rate_limit_acq

    @property
    def loop_time_acq(self):
        '''
        read duration of PI loop in ticks (clock cycle 40MHz)
        '''
        self._loop_time_acq = getattr(FPGAlib, 'read_LoopTicksAcq')(self._fpga.session, self._fpga.status)
        return self._loop_time_acq




# def scaled_coefficients(cutoff_frequency, sample_rate):
#
