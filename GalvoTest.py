# B26 Lab Code
# import system libraries
import ctypes
import numpy
import threading
# load any DLLs
nidaq = ctypes.windll.nicaiu # load the DLL
##############################
# Setup some typedefs and constants
# to correspond with values in
# C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\
#                                                                     NIDAQmx.h
# the typedefs
int32 = ctypes.c_long
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


# This class sets some number of channels from a DAQ each to an input value
class DaqSetPt(threading.Thread):
    # sets each channel to an input value upon object creation
    # waveform: takes a number of channels X 2 matrix, which each channels
    #           two value row has the desired output voltage twice
    # sampleRate: rate in Hz defining minimum time output is held at given value
    # device: list of channels to output to, in same order as in waveform
    def __init__(self, waveform, sampleRate, device):
        self.running = True
        self.sampleRate = sampleRate
        self.numChannels = len(waveform)
        self.periodLength = 2
        self.taskHandle = TaskHandle(0)
        self.data = numpy.zeros( ( self.numChannels, 2), dtype=numpy.float64 )
        #converts python array to ctype array
        for i in range(self.numChannels):
            for j in range(2):
                self.data[i, j] = waveform[i, j]
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
                              self.data.ctypes.data,
                              None,
                              None))
        self.run()
        self.CHK(nidaq.DAQmxWaitUntilTaskDone(self.taskHandle, float64(1)))
        self.stop()
        threading.Thread.__init__(self)

    #runs output task
    def run(self):
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle))

    #stops and cleans up output task
    def stop(self):
        self.running = False
        nidaq.DAQmxStopTask(self.taskHandle)
        nidaq.DAQmxClearTask(self.taskHandle)

    # error checking routine for nidaq commands. Input should be return value
    # from nidaq function. Successful execution of command (usual case) sends 0
    # to this function, which passes through code. Nonzero value is error case
    # err: nidaq error code
    def CHK(self, err):
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
        if(isinstance(waveform[0], list)):
            self.numChannels = len(waveform)
            self.periodLength = len(waveform[0])
        else:
            self.periodLength = len(waveform)
            self.numChannels = 1
        self.taskHandle = TaskHandle(0)
        # special case 1D waveform since length(waveform[0]) is undefined
        # converts python array to ctypes array
        if(isinstance(waveform[0], list)):
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
                              self.data.ctypes.data,
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
    def CHK(self, err):
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

# Test code to do simple output

#t = numpy.arange( 0, 5, 1.0/250.0 )
#x = numpy.sin( t )
#y = numpy.ones(625)
#z = numpy.zeros(625)
#x = numpy.concatenate((y,z))
#inputArray = numpy.transpose(numpy.column_stack((x,x)))
#mythread = DaqOutputWave( inputArray, 250, "Dev1/ao0:1")
#mythread.run()
#time.sleep( 5 )
#mythread.stop()