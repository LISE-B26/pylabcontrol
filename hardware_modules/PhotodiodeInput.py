# B26 Lab Code
# import system libraries
import ctypes
import numpy
import threading
import time
import sys
# load any DLLs
nidaq = ctypes.WinDLL("C:\\Windows\\System32\\nicaiu.dll") # load the DLL
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

class ReadPhotodiode(threading.Thread):
    # initializes values, counter, and clock, and starts clock
    # device: string with name of Photodiode channel (usually Dev1/AI1)
    # frequency: frequency at which to take data
    # sampleNum: number of samples to acquire in buffer
    # RETURN: a 1D array with sampleNum ctypes.c_double values taken at the
    #         desired frequency
    def __init__(self, device, frequency, sampleNum):
        self.taskHandle = TaskHandle(0)
        self.numSamples = sampleNum
        self.data = numpy.zeros((self.numSamples,),dtype=numpy.float64)
        # now, on with the program
        self.CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.taskHandle)))
        self.CHK(nidaq.DAQmxCreateAIVoltageChan(self.taskHandle,device,"",
                                           DAQmx_Val_Cfg_Default,
                                           float64(-10.0),float64(10.0),
                                           DAQmx_Val_Volts,None))
        self.CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle,"",float64(frequency),
                                        DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                        uInt64(self.numSamples)))

    def run(self):
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle))

    def read(self):
        read = int32()
        self.CHK(nidaq.DAQmxReadAnalogF64(self.taskHandle,self.numSamples,float64(10.0),
                                     DAQmx_Val_GroupByChannel,self.data.ctypes.data,
                                     self.numSamples,ctypes.byref(read),None))
        if self.taskHandle.value != 0:
            nidaq.DAQmxStopTask(self.taskHandle)
            nidaq.DAQmxClearTask(self.taskHandle)
        return self.data

    # error checking routine for nidaq commands. Input should be return value
    # from nidaq function
    # err: nidaq error code
    @staticmethod
    def CHK(err):
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))