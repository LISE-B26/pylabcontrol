import ctypes
import threading
import os
import numpy

from src.core.instruments import Instrument, Parameter

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

    _DEFAULT_SETTINGS = Parameter([
        Parameter('device', 'Dev1', (str), 'Name of DAQ device'),
        Parameter('override_buffer_size', -1, int, 'Buffer size for manual override (unused if -1)'),
        Parameter('analog_output',
                  [
                      Parameter('ao0',
                        [
                            Parameter('channel', 0, [0, 1, 2, 3], 'output channel'),
                            Parameter('sample_rate', 1000.0, float, 'output sample rate (Hz)'),
                            Parameter('min_voltage', -10.0, float, 'minimum output voltage (V)'),
                            Parameter('max_voltage', 10.0, float, 'maximum output voltage (V)')
                        ]
                                ),
                      Parameter('ao1',
                        [
                            Parameter('channel', 1, [0, 1, 2, 3], 'output channel'),
                            Parameter('sample_rate', 1000.0, float, 'output sample rate (Hz)'),
                            Parameter('min_voltage', -10.0, float, 'minimum output voltage (V)'),
                            Parameter('max_voltage', 10.0, float, 'maximum output voltage (V)')
                        ]
                                ),
                      Parameter('ao2',
                        [
                            Parameter('channel', 2, [0, 1, 2, 3], 'output channel'),
                            Parameter('sample_rate', 1000.0, float, 'output sample rate (Hz)'),
                            Parameter('min_voltage', -10.0, float, 'minimum output voltage (V)'),
                            Parameter('max_voltage', 10.0, float, 'maximum output voltage (V)')
                        ]
                                ),
                      Parameter('ao3',
                        [
                            Parameter('channel', 3, [0, 1, 2, 3], 'output channel'),
                            Parameter('sample_rate', 1000.0, float, 'output sample rate (Hz)'),
                            Parameter('min_voltage', -10.0, float, 'minimum output voltage (V)'),
                            Parameter('max_voltage', 10.0, float, 'maximum output voltage (V)')
                        ]
                                )
                  ]
                  ),
        Parameter('analog_input',
                  [
                      Parameter('ai0',
                                [
                                    Parameter('channel', 0, range(0, 32), 'input channel'),
                                    Parameter('sample_rate', 1000.0, float, 'input sample rate (Hz)'),
                                    Parameter('min_voltage', -10.0, float, 'minimum input voltage'),
                                    Parameter('max_voltage', 10.0, float, 'maximum input voltage')
                                ]
                                ),
                      Parameter('ai1',
                                [
                                    Parameter('channel', 1, range(0, 32), 'input channel'),
                                    Parameter('sample_rate', 1000.0, float, 'input sample rate'),
                                    Parameter('min_voltage', -10.0, float, 'minimum input voltage'),
                                    Parameter('max_voltage', 10.0, float, 'maximum input voltage')
                                ]
                                ),
                      Parameter('ai2',
                                [
                                    Parameter('channel', 2, range(0, 32), 'input channel'),
                                    Parameter('sample_rate', 1000.0, float, 'input sample rate'),
                                    Parameter('min_voltage', -10.0, float, 'minimum input voltage'),
                                    Parameter('max_voltage', 10.0, float, 'maximum input voltage')
                                ]
                                ),
                      Parameter('ai3',
                                [
                                    Parameter('channel', 3, range(0, 32), 'input channel'),
                                    Parameter('sample_rate', 1000.0, float, 'input sample rate'),
                                    Parameter('min_voltage', -10.0, float, 'minimum input voltage'),
                                    Parameter('max_voltage', 10.0, float, 'maximum input voltage')
                                ]
                                ),
                      Parameter('ai4',
                                [
                                    Parameter('channel', 4, range(0, 32), 'input channel'),
                                    Parameter('sample_rate', 1000.0, float, 'input sample rate'),
                                    Parameter('min_voltage', -10.0, float, 'minimum input voltage'),
                                    Parameter('max_voltage', 10.0, float, 'maximum input voltage (V)')
                                ]
                                )
                  ]
                  ),
        Parameter('digital_input',
                  [
                      Parameter('ctr0',
                                [
                                    Parameter('input_channel', 0, range(0, 32), 'input channel'),
                                    Parameter('clock_PFI_channel', 13, range(0, 32), 'PFI output clock channel'),
                                    Parameter('clock_counter_channel', 1, [0, 1], 'counter output clock channel'),
                                    Parameter('sample_rate', 1000.0, float, 'input sample rate (Hz)')
                                ]
                                )
                  ]
                  )
    ])

    def __init__(self, name = None, settings = None):
        if self.dll_detected:
            # buf_size = 10
            # data = ctypes.create_string_buffer('\000' * buf_size)
            # try:
            #     #Calls arbitrary function to check connection
            #     self.CHK(self.nidaq.DAQmxGetDevProductType(device, ctypes.byref(data), buf_size))
            #     self.hardware_detected = True
            # except RuntimeError:
            #     self.hardware_detected = False
            super(DAQ, self).__init__(name, settings)

    def update(self, settings):
        super(DAQ, self).update(settings)
        for key, value in settings.iteritems():
            if key == 'device':
                if not(self.is_connected):
                    raise EnvironmentError('Device invalid, cannot connect to DAQ')

    @property
    def _PROBES(self):
        return None

    def read_probes(self, key):
        pass

    @property
    def is_connected(self):
        buf_size = 10
        data = ctypes.create_string_buffer('\000' * buf_size)
        try:
            #Calls arbitrary function to check connection
            self.CHK(self.nidaq.DAQmxGetDevProductType(self._parameters['device'], ctypes.byref(data), buf_size))
            return True
        except RuntimeError:
            return False

    def DI_init(self, channel, sampleNum, continuous_acquisition = False, sample_rate_multiplier = 1):
        if not channel in self.settings['digital_input'].keys():
            raise KeyError('This is not a valid digital input channel')
        channel_settings = self.settings['digital_input'][channel]
        self.running = True
        self.DI_sampleNum = sampleNum
        self.DI_sample_rate = float(channel_settings['sample_rate'])*sample_rate_multiplier
        if continuous_acquisition == False:
            self.numSampsPerChan = self.DI_sampleNum
        elif continuous_acquisition == True:
            self.numSampsPerChan = -1
        self.DI_timeout = float64(5 * (1 / self.DI_sample_rate) * self.DI_sampleNum)
        self.input_channel_str = self.settings['device'] + '/' + channel
        self.counter_out_PFI_str = '/' + self.settings['device'] + '/PFI' + str(channel_settings['clock_PFI_channel']) #initial / required only here, see NIDAQ documentation
        self.counter_out_str = self.settings['device'] + '/ctr' + str(channel_settings['clock_counter_channel'])
        self.DI_taskHandleCtr = TaskHandle(0)
        self.DI_taskHandleClk = TaskHandle(1)
        # set up clock
        self._dig_pulse_train_cont(self.DI_sample_rate, 0.5, self.DI_sampleNum)
        self.CHK(self.nidaq.DAQmxStartTask(self.DI_taskHandleClk))
        # set up counter using clock as reference
        self.CHK(self.nidaq.DAQmxCreateTask("", ctypes.byref(self.DI_taskHandleCtr)))
        self.CHK(self.nidaq.DAQmxCreateCICountEdgesChan(self.DI_taskHandleCtr,
                            self.input_channel_str, "", DAQmx_Val_Rising, 0, DAQmx_Val_CountUp))
        # PFI13 is standard output channel for ctr1 channel used for clock and
        # is internally looped back to ctr1 input to be read
        self.CHK(self.nidaq.DAQmxCfgSampClkTiming(self.DI_taskHandleCtr, self.counter_out_PFI_str,
                                             float64(self.DI_sample_rate), DAQmx_Val_Rising,
                                             DAQmx_Val_ContSamps, uInt64(self.DI_sampleNum)))
        if (self.settings['override_buffer_size'] > 0):
            self.CHK(self.nidaq.DAQmxCfgInputBuffer(self.DI_taskHandleCtr, self.settings['override_buffer_size']))

    # initialize reference clock output
    def _dig_pulse_train_cont(self, Freq, DutyCycle, Samps):
        self.CHK(self.nidaq.DAQmxCreateTask("", ctypes.byref(self.DI_taskHandleClk)))
        self.CHK(self.nidaq.DAQmxCreateCOPulseChanFreq(self.DI_taskHandleClk,
                                                       self.counter_out_str, '', DAQmx_Val_Hz, DAQmx_Val_Low,
                                                       float64(0.0),
                                                       float64(Freq), float64(DutyCycle)))
        self.CHK(self.nidaq.DAQmxCfgImplicitTiming(self.DI_taskHandleClk,
                                                   DAQmx_Val_ContSamps, uInt64(Samps)))

    # start reading sampleNum values from counter into buffer
    # todo: AK - should this be threaded? original todo: is this actually blocking? Is the threading actually doing anything? see nidaq cookbook
    def DI_run(self):
        self.CHK(self.nidaq.DAQmxStartTask(self.DI_taskHandleCtr))

    # read sampleNum previously generated values from a buffer, and return the
    # corresponding 1D array of ctypes.c_double values
    def DI_read(self):
        # initialize array and integer to pass as pointers
        self.data = (float64 * self.DI_sampleNum)()
        self.samplesPerChanRead = int32()
        self.CHK(self.nidaq.DAQmxReadCounterF64(self.DI_taskHandleCtr,
                                                int32(self.numSampsPerChan), float64(-1), ctypes.byref(self.data),
                                                uInt32(self.DI_sampleNum), ctypes.byref(self.samplesPerChanRead),
                                                None))
        return self.data, self.samplesPerChanRead

    def DI_stop(self):
        self._DI_stopClk()
        self._DI_stopCtr()

    # stop and clean up clock
    def _DI_stopClk(self):
        self.running = False
        self.nidaq.DAQmxStopTask(self.DI_taskHandleClk)
        self.nidaq.DAQmxClearTask(self.DI_taskHandleClk)

    # stop and clean up counter
    def _DI_stopCtr(self):
        self.nidaq.DAQmxStopTask(self.DI_taskHandleCtr)
        self.nidaq.DAQmxClearTask(self.DI_taskHandleCtr)

    def AO_init(self, channels, waveform, sample_rate_multiplier = 1):
        for c in channels:
            if not c in self.settings['analog_output'].keys():
                raise KeyError('This is not a valid analog output channel')
        self.AO_sample_rate = float(self.settings['analog_output'][channels[0]]['sample_rate']) #float prevents truncation in division
        for c in channels:
            if not self.settings['analog_output'][c]['sample_rate'] == self.AO_sample_rate:
                raise ValueError('All sample rates must be the same')
        self.AO_sample_rate = self.AO_sample_rate * sample_rate_multiplier #float prevents truncation in division
        channel_list = ''
        for c in channels:
            channel_list += self.settings['device'] + '/' + c + ','
        channel_list = channel_list[:-1]
        self.running = True
        # special case 1D waveform since length(waveform[0]) is undefined
        if (len(numpy.shape(waveform)) == 2):
            self.numChannels = len(waveform)
            self.periodLength = len(waveform[0])
        else:
            self.periodLength = len(waveform)
            self.numChannels = 1
        self.AO_taskHandle = TaskHandle(0)
        # special case 1D waveform since length(waveform[0]) is undefined
        # converts python array to ctypes array
        if (len(numpy.shape(waveform)) == 2):
            self.data = numpy.zeros((self.numChannels, self.periodLength),
                                    dtype=numpy.float64)
            for i in range(self.numChannels):
                for j in range(self.periodLength):
                    self.data[i, j] = waveform[i, j]
        else:
            self.data = numpy.zeros((self.periodLength), dtype=numpy.float64)
            for i in range(self.periodLength):
                self.data[i] = waveform[i]
        self.CHK(self.nidaq.DAQmxCreateTask("",
                                       ctypes.byref(self.AO_taskHandle)))
        self.CHK(self.nidaq.DAQmxCreateAOVoltageChan(self.AO_taskHandle,
                                                channel_list,
                                                "",
                                                float64(-10.0),
                                                float64(10.0),
                                                DAQmx_Val_Volts,
                                                None))

        self.CHK(self.nidaq.DAQmxCfgSampClkTiming(self.AO_taskHandle,
                                             "",
                                             float64(self.AO_sample_rate),
                                             DAQmx_Val_Rising,
                                             DAQmx_Val_FiniteSamps,
                                             uInt64(self.periodLength)))
        self.CHK(self.nidaq.DAQmxWriteAnalogF64(self.AO_taskHandle,
                                           int32(self.periodLength),
                                           0,
                                           float64(-1),
                                           DAQmx_Val_GroupByChannel,
                                           self.data.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)),
                                           None,
                                           None))

    # begin outputting waveforms
    # todo: AK - does this actually need to be threaded like in example code? Is it blocking?
    def AO_run(self):
        self.CHK(self.nidaq.DAQmxStartTask(self.AO_taskHandle))

    # wait until waveform output has finished
    def AO_waitToFinish(self):
        self.CHK(self.nidaq.DAQmxWaitUntilTaskDone(self.AO_taskHandle,
                                                   float64(self.periodLength / self.AO_sample_rate * 2)))
    # stop output and clean up
    def AO_stop(self):
        self.running = False
        self.nidaq.DAQmxStopTask(self.AO_taskHandle)
        self.nidaq.DAQmxClearTask(self.AO_taskHandle)

    # def AO_set_pt(self, xVolt, yVolt):
    #     pt = numpy.transpose(numpy.column_stack((xVolt,yVolt)))
    #     pt = (numpy.repeat(pt, 2, axis=1))
    #     # prefacing string with b should do nothing in python 2, but otherwise this doesn't work
    #     pointthread = DaqOutputWave(nidaq, device, pt, pt, sample_rate)
    #     pointthread.run()
    #     pointthread.waitToFinish()
    #     pointthread.stop()


    def AI_init(self, channel, num_samples_to_acquire):
        self.AI_taskHandle = TaskHandle(0)
        self.AI_numSamples = num_samples_to_acquire
        self.data = numpy.zeros((self.AI_numSamples,), dtype=numpy.float64)
        # now, on with the program
        self.CHK(self.nidaq.DAQmxCreateTask("", ctypes.byref(self.AI_taskHandle)))
        self.CHK(self.nidaq.DAQmxCreateAIVoltageChan(self.AI_taskHandle, self.settings['device'], "",
                                                DAQmx_Val_Cfg_Default,
                                                float64(-10.0), float64(10.0),
                                                DAQmx_Val_Volts, None))
        self.CHK(self.nidaq.DAQmxCfgSampClkTiming(self.AI_taskHandle, "", float64(self.settings['analog_input'][channel]['sample_rate']),
                                             DAQmx_Val_Rising, DAQmx_Val_FiniteSamps,
                                             uInt64(self.AI_numSamples)))

    def AI_run(self):
        self.CHK(self.nidaq.DAQmxStartTask(self.AI_taskHandle))

    def AI_read(self):
        read = int32()
        self.CHK(self.nidaq.DAQmxReadAnalogF64(self.AI_taskHandle, self.AI_numSamples, float64(10.0),
                                          DAQmx_Val_GroupByChannel, self.data.ctypes.data,
                                          self.AI_numSamples, ctypes.byref(read), None))
        if self.AI_taskHandle.value != 0:
            self.nidaq.DAQmxStopTask(self.AI_taskHandle)
            self.nidaq.DAQmxClearTask(self.AI_taskHandle)
        return self.data

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

    from src.core import Instrument

    instr, failed = Instrument.load_and_append({'galvo':'DAQ'})
    print(instr)
    print(failed)