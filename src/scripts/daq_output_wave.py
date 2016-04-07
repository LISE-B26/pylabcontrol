from src.core import Script, Parameter
from PyQt4 import QtCore
from PySide.QtCore import Signal, QThread
import time
from collections import deque
from src.instruments import ZIHF2
import numpy as np
from src.core import plotting
from src.instruments import NIDAQ
import ctypes

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

class Daq_Output_Wave(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('sample_rate', 1000, int, 'sample rate of output waveform'),
        Parameter('waveform', [0], float, 'waveform to output on run')
    ])

    _INSTRUMENTS = {'daq':  NIDAQ}

    _SCRIPTS = {}

    def __init__(self, instruments = None, name = None, settings = None,  log_output = None, timeout = 1000000000):
        self.nidaq = self.instruments['daq'].nidaq
        self.running = True
        # special case 1D waveform since length(waveform[0]) is undefined
        if(len(np.shape(self.settings['waveform']))==2):
            self.numChannels = len(self.settings['waveform'])
            self.periodLength = len(self.settings['waveform'][0])
        else:
            self.periodLength = len(self.settings['waveform'])
            self.numChannels = 1
        self.taskHandle = TaskHandle(0)
        # special case 1D waveform since length(waveform[0]) is undefined
        # converts python array to ctypes array
        if(len(np.shape(self.settings['waveform']))==2):
            self.data = np.zeros((self.numChannels, self.periodLength),
                                     dtype=np.float64)
            for i in range(self.numChannels):
                for j in range(self.periodLength):
                    self.data[i, j] = self.settings['waveform'][i, j]
        else:
            self.data = np.zeros((self.periodLength), dtype=np.float64)
            for i in range(self.periodLength):
                self.data[i] = self.settings['waveform'][i]
        self.CHK(self.nidaq.DAQmxCreateTask("",
                          ctypes.byref(self.taskHandle)))
        self.CHK(self.nidaq.DAQmxCreateAOVoltageChan(self.taskHandle,
                                   self.instruments['daq'].settings['device'],
                                   "",
                                   float64(-10.0),
                                   float64(10.0),
                                   DAQmx_Val_Volts,
                                   None))
        self.CHK(self.nidaq.DAQmxCfgSampClkTiming(self.taskHandle,
                                "",
                                float64(self.sampleRate),
                                DAQmx_Val_Rising,
                                DAQmx_Val_FiniteSamps,
                                uInt64(self.periodLength)))
        self.CHK(self.nidaq.DAQmxWriteAnalogF64(self.taskHandle,
                              int32(self.periodLength),
                              0,
                              float64(-1),
                              DAQmx_Val_GroupByChannel,
                              self.data.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)),
                              None,
                              None))
        threading.Thread.__init__(self)
