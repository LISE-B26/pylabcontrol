"""
Created on Wed Oct 22 17:46:08 2014

@author: Jan Gieseler

higher level Python objects, for an example how to use them see run_NI_FPGA_PID.py

"""

from ctypes import c_uint32, c_int32

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

    # @property
    # def device_temperature(self):
    #     FPGAlib.read_DeviceTemperature(self.session, self.status)
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
    def __init__(self, fpga, PI_gains = {}):
        '''

        :param fpga: NI7845R object
        :param PI_gains: dictionary  with values for PI gains {'integral': XX, 'proportional': XX}
        :return:
        '''
        self._fpga = fpga
        self._PI_gains = PI_gains

    def set_piezo(self, value):
        '''
        sets the voltage that is sent to the amplifier, and from there to the piezo
        :param value:
        :return:
        '''

        PIDactive = self.get_PI_status()

        if PIDactive == True:
            print('PID is active, manual piezo control not active!')
            return False
        else:
            return getattr(FPGAlib, 'set_PiezoOut')(value, self._fpga.session, self._fpga.status)

    def get_piezo(self):
        '''
        :return: returns the value that is sent to the amplifier
        '''
        return getattr(FPGAlib, 'read_PiezoOut')(self._fpga.session, self._fpga.status)

    def set_PI_status(self, status):
        '''
        tuen PID on or off
        :param status:
        :return:
        '''
        return getattr(FPGAlib, 'set_PIDActive') (status, self._fpga.session, self._fpga.status)

    def get_PI_status(self):
        '''
        get status of PID (on or off)
        :return:
        '''
        return getattr(FPGAlib, 'read_PIDActive')(self._fpga.session, self._fpga.status)

    def get_detector(self, is_raw_value = True):
        '''
        read detector value
        :param is_raw_value: True: raw value as read from the input, False: filtered value (discrete filter if Lowpass off or lowpass filter if lowpass on)
        :return:
        '''
        if is_raw_value == True:
            return getattr(FPGAlib, 'read_AI1')(self._fpga.session, self._fpga.status)
        else:
            return getattr(FPGAlib, 'read_AI1_Filtered')(self._fpga.session, self._fpga.status)

    def set_PI_gains(self, gains):

        return getattr(FPGAlib, 'set_PIDActive') (status, self._fpga.session, self._fpga.status)