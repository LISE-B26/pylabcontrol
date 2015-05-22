# B26 Lab Code
# Last Update: 1/28/15

# External Connections: No external connection to counter 1 out (PFI13)

# import standard libraries
import ctypes
import threading
import time
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
DAQmx_Val_Rising = 10280
DAQmx_Val_CountUp = 10128
DAQmx_Val_ContSamps =10123; #continuous samples
DAQmx_Val_Hz = 10373; #Hz
DAQmx_Val_Low =10214; #Low


# This class creates a thread to perform buffered reading from an APD
class ReadAPD(threading.Thread):
    # initializes values, counter, and clock, and starts clock
    # device: string with name of APD channel (usually Dev1/ctr0 or Dev1/ctr1)
    # frequency: frequency at which to take data
    # sampleNum: number of samples to acquire in buffer
    # RETURN: a 1D array with sampleNum ctypes.c_double values taken at the
    #         desired frequency
    def __init__(self, device, frequency, sampleNum):
        self.running = True
        self.sampleNum = sampleNum
        self.device = device
        self.timeout = float64(5 * (1 / frequency) * sampleNum)
        self.taskHandleCtr = TaskHandle(0)
        self.taskHandleClk = TaskHandle(1)
        # set up clock
        self.DigPulseTrainCont(frequency, 0.5, sampleNum)
        self.CHK(nidaq.DAQmxStartTask(self.taskHandleClk))
        # set up counter using clock as reference
        self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandleCtr)))
        self.CHK(nidaq.DAQmxCreateCICountEdgesChan(self.taskHandleCtr,
                      self.device, "", DAQmx_Val_Rising, 0, DAQmx_Val_CountUp))
        # PFI13 is standard output channel for ctr1 channel used for clock and
        # is internally looped back to ctr1 input to be read
        self.CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandleCtr, '/Dev1/PFI13',
                                          float64(frequency), DAQmx_Val_Rising,
                                       DAQmx_Val_ContSamps, uInt64(sampleNum)))
        threading.Thread.__init__(self)

    # start reading sampleNum values from counter into buffer
    def runCtr(self):
        self.CHK(nidaq.DAQmxStartTask(self.taskHandleCtr))

    # read sampleNum previously generated values from a buffer, and return the
    # corresponding 1D array of ctypes.c_double values
    def read(self):
        #initialize array and intiger to pass as pointers
        self.data = (float64 * self.sampleNum)()
        self.samplesPerChanRead = int32()
        self.CHK(nidaq.DAQmxReadCounterF64(self.taskHandleCtr,
                 int32(self.sampleNum), float64(-1), ctypes.byref(self.data),
                 uInt32(self.sampleNum), ctypes.byref(self.samplesPerChanRead),
                 None))
        return self.data

    # stop and clean up clock
    def stopClk(self):
        self.running = False
        nidaq.DAQmxStopTask(self.taskHandleClk)
        nidaq.DAQmxClearTask(self.taskHandleClk)

    # stop and clean up counter
    def stopCtr(self):
        nidaq.DAQmxStopTask(self.taskHandleCtr)
        nidaq.DAQmxClearTask(self.taskHandleCtr)

    # initialize reference clock output
    def DigPulseTrainCont(self, Freq, DutyCycle, Samps):
        self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandleClk)))
        self.CHK(nidaq.DAQmxCreateCOPulseChanFreq(self.taskHandleClk,
                 'Dev1/ctr1', '', DAQmx_Val_Hz, DAQmx_Val_Low, float64(0.0),
                 float64(Freq), float64(DutyCycle)))
        self.CHK(nidaq.DAQmxCfgImplicitTiming(self.taskHandleClk,
                 DAQmx_Val_ContSamps, uInt64(Samps)))

    # error checking routine for nidaq commands. Input should be return value
    # from nidaq function
    # err: nidaq error code
    def CHK( self, err ):
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

# Test code to do a single buffered read

#mythread = ReadAPD("Dev1/ctr0",100.0,100)
#mythread.run()
#time.sleep(2)
#data = mythread.read()
#mythread.stopCtr()
#mythread.stopClk()
#for i in data: print i