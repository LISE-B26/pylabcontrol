import ctypes
import threading
import os
import numpy

from src.core.instruments import *

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
# Analog constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByChannel = 0

# DI constants
DAQmx_Val_CountUp = 10128
DAQmx_Val_Hz = 10373; #Hz
DAQmx_Val_Low =10214; #Low


# =============== NI DAQ 6259======= =======================
# ==========================================================

class DAQ(Instrument):

    try:
        if os.name == 'nt':
            nidaq = ctypes.WinDLL("C:\\Windows\\System32\\nicaiu.dll") # load the DLL
            dll_detected = True
        else:
            dll_detected = False
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
            self.update_parameters(self._parameters_default)

    @property
    def _parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('device', 'Dev1', (str), 'Name of DAQ device'),
            Parameter('override_buffer_size', -1, int, 'Buffer size for manual override (unused if -1)'),
            Parameter('output',
                      [
                          Parameter('channel', [0,1], [0,1,2,3], 'output channel(s)'),
                          Parameter('sample_rate', 1000, (int, float), 'output sample rate'),
                          Parameter('min_voltage', -10, (int, float), 'minimum output voltage'),
                          Parameter('max_voltage', 10, (int, float), 'maximum output voltage')
                       ]
                      ),
            Parameter('analog_input',
                      [
                          Parameter('channel', 0, range(0,32), 'input channel(s)'),
                          Parameter('sample_rate', 1000, (int, float), 'input sample rate'),
                          Parameter('min_voltage', -10, (int, float), 'minimum input voltage'),
                          Parameter('max_voltage', 10, (int, float), 'maximum input voltage')
                       ]
                      ),
            Parameter('digital_input',
                      [
                          Parameter('input_channel', 0, range(0,32), 'input channel(s)'),
                          Parameter('clock_PFI_channel', 13, range(0,32), 'PFI output clock channel'),
                          Parameter('clock_counter_channel', 1, [0,1], 'counter output clock channel'),
                          Parameter('sample_rate', 1000, (int, float), 'input sample rate')
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

# This class creates a thread to perform buffered reading from an APD
class ReadAPD(threading.Thread):
    # initializes values, counter, and clock, and starts clock
    # device: string with name of APD channel (usually Dev1/ctr0 or Dev1/ctr1). The apd should be attached to the source
    #   port for this counter channel
    # sample_rate: sample rate at which to take data
    # sampleNum: number of samples to acquire in buffer
    # RETURN: a 1D array with sampleNum ctypes.c_double values taken at the
    #         desired sample rate
    def __init__(self, nidaq, device, channel, sample_rate, sampleNum, clock_PFI_channel = 13, clock_counter_channel = 1, override_buffer_size = -1, continuous_acquisition = False):
        self.running = True
        self.sampleNum = sampleNum
        if continuous_acquisition == False:
            self.numSampsPerChan = sampleNum
        elif continuous_acquisition == True:
            self.numSampsPerChan = -1
        self.device = device
        self.timeout = float64(5 * (1 / sample_rate) * sampleNum)
        self.counter_out_PFI = device + '/PFI' + str(clock_PFI_channel)
        self.counter_out = device + '/ctr' + str(clock_counter_channel)
        self.taskHandleCtr = TaskHandle(0)
        self.taskHandleClk = TaskHandle(1)
        # set up clock
        self.DigPulseTrainCont(sample_rate, 0.5, sampleNum)
        self.CHK(nidaq.DAQmxStartTask(self.taskHandleClk))
        # set up counter using clock as reference
        self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandleCtr)))
        self.CHK(nidaq.DAQmxCreateCICountEdgesChan(self.taskHandleCtr,
                      self.device, "", DAQmx_Val_Rising, 0, DAQmx_Val_CountUp))
        # PFI13 is standard output channel for ctr1 channel used for clock and
        # is internally looped back to ctr1 input to be read
        self.CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandleCtr, self.counter_out_PFI,
                                             float64(sample_rate), DAQmx_Val_Rising,
                                             DAQmx_Val_ContSamps, uInt64(sampleNum)))
        if (override_buffer_size > 0):
            self.CHK(nidaq.DAQmxCfgInputBuffer(self.taskHandleCtr, override_buffer_size))
        threading.Thread.__init__(self)

    # start reading sampleNum values from counter into buffer
    # todo: AK - is this actually blocking? Is the threading actually doing anything? see nidaq cookbook
    def run(self):
        self.CHK(self.nidaq.DAQmxStartTask(self.taskHandleCtr))

    # read sampleNum previously generated values from a buffer, and return the
    # corresponding 1D array of ctypes.c_double values
    def read(self):
        #initialize array and integer to pass as pointers
        self.data = (float64 * self.sampleNum)()
        self.samplesPerChanRead = int32()
        self.CHK(self.nidaq.DAQmxReadCounterF64(self.taskHandleCtr,
                 int32(self.numSampsPerChan), float64(-1), ctypes.byref(self.data),
                 uInt32(self.sampleNum), ctypes.byref(self.samplesPerChanRead),
                 None))
        return self.data, self.samplesPerChanRead

    def stop(self):
        self.stopClk()
        self.stopCtr()

    # stop and clean up clock
    def stopClk(self):
        self.running = False
        self.nidaq.DAQmxStopTask(self.taskHandleClk)
        self.nidaq.DAQmxClearTask(self.taskHandleClk)

    # stop and clean up counter
    def stopCtr(self):
        self.nidaq.DAQmxStopTask(self.taskHandleCtr)
        self.nidaq.DAQmxClearTask(self.taskHandleCtr)

    # initialize reference clock output
    def DigPulseTrainCont(self, Freq, DutyCycle, Samps):
        self.CHK(self.nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandleClk)))
        self.CHK(self.nidaq.DAQmxCreateCOPulseChanFreq(self.taskHandleClk,
                 self.counter_out, '', DAQmx_Val_Hz, DAQmx_Val_Low, float64(0.0),
                 float64(Freq), float64(DutyCycle)))
        self.CHK(self.nidaq.DAQmxCfgImplicitTiming(self.taskHandleClk,
                 DAQmx_Val_ContSamps, uInt64(Samps)))

    # error checking routine for nidaq commands. Input should be return value
    # from nidaq function
    # err: nidaq error code
    def CHK( self, err ):
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

#Outputs arbitrary waveform to any number of channels from a DAQ
class DaqOutputWave(threading.Thread):
    # initializes values and sets up output channel
    # waveform: takes a number of channels X number of samples to output
    #           matrix, which each channels row contains the waveform to output
    #           on that channel
    # sampleRate: sets rate in Hz for waveform output
    # device: list of channels to output to, in same order as in waveform
    def __init__(self, nidaq, device, waveform, sample_rate):
        self.nidaq = nidaq
        self.running = True
        self.sampleRate = sample_rate
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
    # tddo: AK - does this actually need to be threaded like in example code? Is it blocking?
    def run(self):
        self.CHK(self.nidaq.DAQmxStartTask(self.taskHandle))

    # wait until waveform output has finished
    def waitToFinish(self):
        self.CHK(self.nidaq.DAQmxWaitUntilTaskDone(self.taskHandle,
                 float64(self.periodLength / self.sampleRate * 2)))

    # stop output and clean up
    def stop(self):
        self.running = False
        self.nidaq.DAQmxStopTask(self.taskHandle)
        self.nidaq.DAQmxClearTask(self.taskHandle)

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

    # Gets voltages currently output on all four channels, and returns them as a tuple.
    def getOutputVoltages(self):
        device = ('Dev1/_ao0_vs_aognd, Dev1/_ao1_vs_aognd, Dev1/_ao2_vs_aognd, Dev1/_ao3_vs_aognd')
        data = (float64 * 4)()
        taskHandle = TaskHandle(0)
        self.CHK(self.nidaq.DAQmxCreateTask("",
                    ctypes.byref(taskHandle)))
        self.CHK(self.nidaq.DAQmxCreateAIVoltageChan(taskHandle, device, "", DAQmx_Val_Cfg_Default, float64(-10), float64(10), DAQmx_Val_Volts, None))
        self.CHK(self.nidaq.DAQmxReadAnalogF64(taskHandle, int32(1), float64(10), DAQmx_Val_GroupByChannel, ctypes.byref(data), uInt32(4), None, None))
        self.CHK(self.nidaq.DAQmxClearTask(taskHandle))
        return data[0:4]

class SetGalvoPoint:
    def __init__(self,xVolt,yVolt, nidaq, device, sample_rate):
        pt = numpy.transpose(numpy.column_stack((xVolt,yVolt)))
        pt = (numpy.repeat(pt, 2, axis=1))
        # prefacing string with b should do nothing in python 2, but otherwise this doesn't work
        pointthread = DaqOutputWave(nidaq, device, pt, pt, sample_rate)
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()


if __name__ == '__main__':
    a = DAQ('Dev1')
    print(a.parameters)