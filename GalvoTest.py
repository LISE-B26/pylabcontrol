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

#Outputs arbitrary waveform to any number of channels from a DAQ
class DaqOutputWave(threading.Thread):
    # initializes values and sets up output channel
    # waveform: takes a number of channels X number of samples to output
    #           matrix, which each channels row contains the waveform to output
    #           on that channel
    # sampleRate: sets rate in Hz for waveform output
    # device: list of channels to output to, in same order as in waveform
    def __init__(self, waveform, sampleRate, device):
        self.running = True
        self.sampleRate = sampleRate
        # special case 1D waveform since length(waveform[0]) is undefined
        if(len(numpy.shape(waveform))==2):
            self.numChannels = len(waveform)
            self.periodLength = len(waveform[0])
        else:
            self.periodLength = len(waveform)
            self.numChannels = 1
        self.taskHandle = TaskHandle(0)
        # special case 1D waveform since length(waveform[0]) is undefined
        # converts python array to ctypes array
        if(len(numpy.shape(waveform))==2):
            self.data = numpy.zeros((self.numChannels, self.periodLength),
                                     dtype=numpy.float64)
            for i in range(self.numChannels):
                for j in range(self.periodLength):
                    self.data[i, j] = waveform[i, j]
        else:
            self.data = numpy.zeros((self.periodLength), dtype=numpy.float64)
            for i in range(self.periodLength):
                self.data[i] = waveform[i]
        self.CHK(nidaq.DAQmxCreateTask("",
                          ctypes.byref(self.taskHandle)))
        self.CHK(nidaq.DAQmxCreateAOVoltageChan(self.taskHandle,
                                   device,
                                   "",
                                   float64(-10.0),
                                   float64(10.0),
                                   DAQmx_Val_Volts,
                                   None))
        self.CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle,
                                "",
                                float64(self.sampleRate),
                                DAQmx_Val_Rising,
                                DAQmx_Val_FiniteSamps,
                                uInt64(self.periodLength)))
        self.CHK(nidaq.DAQmxWriteAnalogF64(self.taskHandle,
                              int32(self.periodLength),
                              0,
                              float64(-1),
                              DAQmx_Val_GroupByChannel,
                              self.data.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)),
                              None,
                              None))
        threading.Thread.__init__(self)


    # begin outputting waveforms
    def run(self):
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle))

    # wait until waveform output has finished
    def waitToFinish(self):
        self.CHK(nidaq.DAQmxWaitUntilTaskDone(self.taskHandle,
                 float64(self.periodLength / self.sampleRate * 2)))

    # stop output and clean up
    def stop(self):
        self.running = False
        nidaq.DAQmxStopTask(self.taskHandle)
        nidaq.DAQmxClearTask(self.taskHandle)

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

    # Gets voltages currently output on all four channels, and returns them as a tuple.
    @classmethod
    def getOutputVoltages(cls):
        device = ('Dev1/_ao0_vs_aognd, Dev1/_ao1_vs_aognd, Dev1/_ao2_vs_aognd, Dev1/_ao3_vs_aognd')
        data = (float64 * 4)()
        taskHandle = TaskHandle(0)
        cls.CHK(nidaq.DAQmxCreateTask("",
                    ctypes.byref(taskHandle)))
        cls.CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle, device, "", DAQmx_Val_Cfg_Default, float64(-10), float64(10), DAQmx_Val_Volts, None))
        cls.CHK(nidaq.DAQmxReadAnalogF64(taskHandle, int32(1), float64(10), DAQmx_Val_GroupByChannel, ctypes.byref(data), uInt32(4), None, None))
        cls.CHK(nidaq.DAQmxClearTask(taskHandle))
        return data[0:4]

#When initialized, sets Galvo to the point xVolt,yVolt
class SetGalvoPoint:
    def __init__(self,xVolt,yVolt):
        pt = numpy.transpose(numpy.column_stack((xVolt,yVolt)))
        pt = (numpy.repeat(pt, 2, axis=1))
        # prefacing string with b should do nothing in python 2, but otherwise this doesn't work
        pointthread = DaqOutputWave(pt, 1000.0, b"Dev1/ao0:1")
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()



# Test code to do simple output
#print(sys.path)

#t = numpy.arange( 0, 1, .5 )
#x = numpy.sin( t )
#y = numpy.ones(625)
#z = numpy.zeros(625)
#x = numpy.concatenate((y,z))
#inputArray = numpy.transpose(numpy.column_stack((x,x)))
#print(inputArray)
#print(len(numpy.shape(inputArray)))
#mythread = DaqOutputWave( x, 1.0/250, "Dev1/ao0")
#mythread.run()
#time.sleep( 5 )
#mythread.stop()