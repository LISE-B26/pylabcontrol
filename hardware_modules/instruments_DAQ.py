import ctypes
import numpy
import threading
import time
import sys
from instruments import *

##############################
# Setup some typedefs and constants
# to correspond with values in
# C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\
#                                                                     NIDAQmx.h
# the typedefs
int32 = ctypes.c_long
int64 = ctypes.c_longlong
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
# the constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByChannel = 0


# =============== NI DAQ 6259======= =======================
# ==========================================================

class DAQ(Instrument):

    try:
        nidaq = ctypes.WinDLL("C:\\Windows\\System32\\nicaiu.dll") # load the DLL
        dll_detected = True
    except WindowsError:
        # make a fake DAQOut instrument
        dll_detected = False
    except:
        raise

    def __init__(self, device, name = None, parameter_list = []):
        if self.dll_detected:
            buf_size = 10
            data = ctypes.create_string_buffer('\000' * buf_size)
            try:
                #Calls arbitrary function to check connection
                self.CHK(self.nidaq.DAQmxGetDevProductType(device, ctypes.byref(data), buf_size))
                self.hardware_detected = True
            except RuntimeError:
                self.hardware_detected = False
            super(DAQ, self).__init__(name)
            self.update_parameters(self.parameters_default)

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('device', 'Dev1', (str), 'Name of DAQ device'),
            Parameter('output',
                      [
                          Parameter('channel', {0,1}, [0,1], 'output channel(s)')
                       ]
                      )
        ]

        return parameter_list_default



    # error checking routine for nidaq commands. Input should be return value
    # from nidaq function
    # err: nidaq error code
    def CHK(self, err):
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            self.nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            self.nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))

if __name__ == '__main__':
    a = DAQ('Dev1')
    print(a.parameters)