"""
Created on Wed Oct 22 17:46:08 2014

@author: Erik Hebestreit, Jan Gieseler


Wrapper for c-compiled FPGA_read_inputs.vi

"""

from ctypes import c_uint32, c_int32

import src.lib.FPGAlib as FPGAlib


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



class AnalogInput(object):
    _channel_number = None
    _fpga = None

    def __init__(self, channel, fpga):
        self._channel_number = channel
        self._fpga = fpga

    def read(self):
        return getattr(FPGAlib, 'read_AI%0d' % self._channel_number)(self._fpga.session, self._fpga.is_connected)


class AnalogOutput(object):
    _channel_number = None
    _fpga = None

    def __init__(self, channel, fpga):
        self._channel_number = channel
        self._fpga = fpga

    def write(self, value):
        return getattr(FPGAlib, 'set_AO%0d' % self._channel_number) \
            (value, self._fpga.session,
             self._fpga.is_connected)


# class DigitalInput(object):
#     _channel_number = None
#     _fpga = None
#
#     def __init__(self, channel, fpga):
#         self._channel_number = channel
#         self._fpga = fpga
#
#     def read(self):
#         return getattr(fpga_binder, 'read_DIO%0d' % self._channel_number) \
#             (self._fpga.session, self._fpga.status)


# class DigitalOutput(object):
#     _channel_number = None
#     _fpga = None
#
#     def __init__(self, channel, fpga):
#         self._channel_number = channel
#         self._fpga = fpga
#
#     def write(self, state):
#         return getattr(fpga_binder, 'set_DIO%0d' % self._channel_number) \
#             (state, self._fpga.session, self._fpga.status)