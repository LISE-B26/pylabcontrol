"""
Created on Wed Oct 22 17:46:08 2014

@author: Erik Hebestreit, Jan Gieseler


Wrapper for c-compiled FPGA_read_inputs.vi

"""

from ctypes import c_uint32, c_int32

import lib.FPGAlib as FPGAlib


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
