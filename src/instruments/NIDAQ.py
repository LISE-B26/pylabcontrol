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
TaskHandle = uInt64
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
    '''
    Class containing all functions used to interact with the NI DAQ, mostly
    acting as a wrapper around C-level dlls provided by NI. Tested on an
    NI DAQ 6259, but should be compatable (with small changes of default
    channels) with most daqmx devices. In particular, the physical channel
    corresponding to the ctr1 PFI in the digital input channelmust be changed
    '''

    try:
        if os.name == 'nt':
            #checks for windows. If not on windows, check for your OS and add
            #the path to the DLL on your machine
            nidaq = ctypes.WinDLL("C:\\Windows\\System32\\nicaiu.dll") # load the DLL
            dll_detected = True
        else:
            dll_detected = False
    except WindowsError:
        # make a fake DAQOut instrument
        dll_detected = False
    except:
        raise

    #currently includes four analog outputs, five analog inputs, and one digital counter input. Add
    #more as needed adn your device allows
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

    #unlike most instruments, all of the settings are sent to the DAQ on instantiation of
    #a task, such as an input or output. Thus, changing the settings only updates the internal
    #daq construct in the program and makes no hardware changes
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
        '''
        Makes a non-state-changing call (a get id call) to check connection to a daq
        Returns: True if daq is connected, false if it is not

        '''
        buf_size = 10
        data = ctypes.create_string_buffer('\000' * buf_size)
        try:
            #Calls arbitrary function to check connection
            self._check_error(self.nidaq.DAQmxGetDevProductType(self._parameters['device'], ctypes.byref(data), buf_size))
            return True
        except RuntimeError:
            return False

    def DI_init(self, channel, sampleNum, continuous_acquisition=False):
        '''
        Initializes a hardware-timed digital counter, bound to a hardware clock
        Args:
            channel: digital channel to initialize for read in
            sampleNum: number of samples to read in for finite operation, or number of samples between
                       reads for continuous operation (to set buffer size)
            continuous_acquisition: run in continuous acquisition mode (ex for a continuous counter) or
                                    finite acquisition mode (ex for a scan, where the number of samples needed
                                    is known a priori)

        Returns: source of clock that this method sets up, which can be given to another function to synch that
         input or output to the same clock

        '''
        if not channel in self.settings['digital_input'].keys():
            raise KeyError('This is not a valid digital input channel')
        channel_settings = self.settings['digital_input'][channel]
        self.running = True
        self.DI_sampleNum = sampleNum
        self.DI_sample_rate = float(channel_settings['sample_rate'])
        if not continuous_acquisition:
            self.numSampsPerChan = self.DI_sampleNum
        else:
            self.numSampsPerChan = -1
        self.DI_timeout = float64(5 * (1 / self.DI_sample_rate) * self.DI_sampleNum)
        self.input_channel_str = self.settings['device'] + '/' + channel
        self.counter_out_PFI_str = '/' + self.settings['device'] + '/PFI' + str(channel_settings['clock_PFI_channel']) #initial / required only here, see NIDAQ documentation
        self.counter_out_str = self.settings['device'] + '/ctr' + str(channel_settings['clock_counter_channel'])
        self.DI_taskHandleCtr = TaskHandle(0)
        self.DI_taskHandleClk = TaskHandle(1)

        # set up clock
        self._dig_pulse_train_cont(self.DI_sample_rate, 0.5, self.DI_sampleNum)
        # set up counter using clock as reference
        self._check_error(self.nidaq.DAQmxCreateTask("", ctypes.byref(self.DI_taskHandleCtr)))
        self._check_error(self.nidaq.DAQmxCreateCICountEdgesChan(self.DI_taskHandleCtr,
                                                                 self.input_channel_str, "", DAQmx_Val_Rising, 0, DAQmx_Val_CountUp))
        # PFI13 is standard output channel for ctr1 channel used for clock and
        # is internally looped back to ctr1 input to be read
        self._check_error(self.nidaq.DAQmxCfgSampClkTiming(self.DI_taskHandleCtr, self.counter_out_PFI_str,
                                                           float64(self.DI_sample_rate), DAQmx_Val_Rising,
                                                           DAQmx_Val_FiniteSamps, uInt64(self.DI_sampleNum)))
        # if (self.settings['override_buffer_size'] > 0):
        #     self._check_error(self.nidaq.DAQmxCfgInputBuffer(self.DI_taskHandleCtr, uInt64(self.settings['override_buffer_size'])))
        # self._check_error(self.nidaq.DAQmxCfgInputBuffer(self.DI_taskHandleCtr, uInt64(sampleNum)))

        self._check_error(self.nidaq.DAQmxStartTask(self.DI_taskHandleCtr))

        return self.counter_out_PFI_str


    # initialize reference clock output
    def _dig_pulse_train_cont(self, Freq, DutyCycle, Samps):
        '''
        Initializes a digital pulse train to act as a reference clock
        Args:
            Freq: frequency of reference clock
            DutyCycle: percentage of cycle that clock should be high voltage (usually .5)
            Samps: number of samples to generate

        Returns:

        '''
        self._check_error(self.nidaq.DAQmxCreateTask("", ctypes.byref(self.DI_taskHandleClk)))
        self._check_error(self.nidaq.DAQmxCreateCOPulseChanFreq(self.DI_taskHandleClk,
                                                                self.counter_out_str, '', DAQmx_Val_Hz, DAQmx_Val_Low,
                                                                float64(0.0),
                                                                float64(Freq), float64(DutyCycle)))
        self._check_error(self.nidaq.DAQmxCfgImplicitTiming(self.DI_taskHandleClk,
                                                            DAQmx_Val_ContSamps, uInt64(Samps)))

    # start reading sampleNum values from counter into buffer
    # todo: AK - should this be threaded? original todo: is this actually blocking? Is the threading actually doing anything? see nidaq cookbook
    def DI_run(self):
        '''
        start reading sampleNum values from counter into buffer
        '''
        self._check_error(self.nidaq.DAQmxStartTask(self.DI_taskHandleClk))


    # read sampleNum previously generated values from a buffer, and return the
    # corresponding 1D array of ctypes.c_double values
    def DI_read(self):
        '''
        read sampleNum previously generated values from a buffer, and return the
        corresponding 1D array of ctypes.c_double values
        Returns: 1d array of ctypes.c_double values with the requested counts

        '''
        # initialize array and integer to pass as pointers
        self.data = (float64 * self.DI_sampleNum)()
        self.samplesPerChanRead = int32()
        self._check_error(self.nidaq.DAQmxReadCounterF64(self.DI_taskHandleCtr,
                                                         int32(self.numSampsPerChan), float64(-1), ctypes.byref(self.data),
                                                         uInt32(self.DI_sampleNum), ctypes.byref(self.samplesPerChanRead),
                                                         None))
        return self.data, self.samplesPerChanRead

    def DI_stop(self):
        '''
        Stops and cleans up digital input
        '''
        self._DI_stopClk()
        self._DI_stopCtr()

    def _DI_stopClk(self):
        '''
        stop and clean up clock
        '''
        self.running = False
        self.nidaq.DAQmxStopTask(self.DI_taskHandleClk)
        self.nidaq.DAQmxClearTask(self.DI_taskHandleClk)

    def _DI_stopCtr(self):
        '''
        stop and clean up counter
        '''
        self.nidaq.DAQmxStopTask(self.DI_taskHandleCtr)
        self.nidaq.DAQmxClearTask(self.DI_taskHandleCtr)

    def AO_init(self, channels, waveform, clk_source = ""):
        '''
        Initializes a arbitrary number of analog output channels to output an arbitrary waveform
        Args:
            channels: List of channels to output on
            waveform: 2d array of voltages to output, with each column giving the output values at a given time
                (the timing given by the sample rate of the channel) with the channels going from top to bottom in
                the column in the order given in channels
            clk_source: the PFI channel of the hardware clock to lock the output to, or "" to use the default
                internal clock
        '''
        for c in channels:
            if not c in self.settings['analog_output'].keys():
                raise KeyError('This is not a valid analog output channel')
        self.AO_sample_rate = float(self.settings['analog_output'][channels[0]]['sample_rate']) #float prevents truncation in division
        for c in channels:
            if not self.settings['analog_output'][c]['sample_rate'] == self.AO_sample_rate:
                raise ValueError('All sample rates must be the same')
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
        self._check_error(self.nidaq.DAQmxCreateTask("",
                                                     ctypes.byref(self.AO_taskHandle)))
        self._check_error(self.nidaq.DAQmxCreateAOVoltageChan(self.AO_taskHandle,
                                                              channel_list,
                                                "",
                                                              float64(-10.0),
                                                              float64(10.0),
                                                              DAQmx_Val_Volts,
                                                              None))
        self._check_error(self.nidaq.DAQmxCfgSampClkTiming(self.AO_taskHandle,
                                             clk_source,
                                                           float64(self.AO_sample_rate),
                                                           DAQmx_Val_Rising,
                                                           DAQmx_Val_FiniteSamps,
                                                           uInt64(self.periodLength)))
        self._check_error(self.nidaq.DAQmxWriteAnalogF64(self.AO_taskHandle,
                                                         int32(self.periodLength),
                                                         0,
                                                         float64(-1),
                                                         DAQmx_Val_GroupByChannel,
                                                         self.data.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)),
                                                         None,
                                                         None))


    # todo: AK - does this actually need to be threaded like in example code? Is it blocking?
    def AO_run(self):
        '''
        Begin outputting waveforms (or, if a non-default clock is used, trigger output immediately
        on that clock starting)
        '''
        self._check_error(self.nidaq.DAQmxStartTask(self.AO_taskHandle))

    def AO_waitToFinish(self):
        '''
        Wait until output has finished
        '''
        self._check_error(self.nidaq.DAQmxWaitUntilTaskDone(self.AO_taskHandle,
                                                            float64(self.periodLength / self.AO_sample_rate * 2)))

    def AO_stop(self):
        '''
        Stop and clean up output
        '''
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
        '''
        Initializes an input channel to read on
        Args:
            channel: Channel to read input
            num_samples_to_acquire: number of samples to acquire on that channel
        '''
        self.AI_taskHandle = TaskHandle(0)
        self.AI_numSamples = num_samples_to_acquire
        self.data = numpy.zeros((self.AI_numSamples,), dtype=numpy.float64)
        # now, on with the program
        self._check_error(self.nidaq.DAQmxCreateTask("", ctypes.byref(self.AI_taskHandle)))
        self._check_error(self.nidaq.DAQmxCreateAIVoltageChan(self.AI_taskHandle, self.settings['device'], "",
                                                              DAQmx_Val_Cfg_Default,
                                                              float64(-10.0), float64(10.0),
                                                              DAQmx_Val_Volts, None))
        self._check_error(self.nidaq.DAQmxCfgSampClkTiming(self.AI_taskHandle, "", float64(self.settings['analog_input'][channel]['sample_rate']),
                                                           DAQmx_Val_Rising, DAQmx_Val_FiniteSamps,
                                                           uInt64(self.AI_numSamples)))

    def AI_run(self):
        '''
        Start taking analog input and storing it in a buffer
        '''
        self._check_error(self.nidaq.DAQmxStartTask(self.AI_taskHandle))

    def AI_read(self):
        '''
        Reads the AI voltage values from the buffer
        Returns: array of ctypes.c_long with the voltage data
        '''
        read = int32()
        self._check_error(self.nidaq.DAQmxReadAnalogF64(self.AI_taskHandle, self.AI_numSamples, float64(10.0),
                                                        DAQmx_Val_GroupByChannel, self.data.ctypes.data,
                                                        self.AI_numSamples, ctypes.byref(read), None))
        if self.AI_taskHandle.value != 0:
            self.nidaq.DAQmxStopTask(self.AI_taskHandle)
            self.nidaq.DAQmxClearTask(self.AI_taskHandle)
        return self.data

    def triggered_DI_init(self):
        pass

    def _check_error(self, err):
        """
        Error Checking Routine for DAQmx functions. Pass in the returned values form DAQmx functions (the errors) to get
        an error description. Raises a runtime error
        Args:
            err: 32-it integer error from an NI-DAQmx function

        Returns: a verbose description of the error taken from the nidaq dll

        """
        if err < 0:
            buffer_size = 100
            buffer = ctypes.create_string_buffer('\000' * buffer_size)
            self.nidaq.DAQmxGetErrorString(err,ctypes.byref(buffer),buffer_size)
            raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buffer.value)))
        if err > 0:
            buffer_size = 100
            buffer = ctypes.create_string_buffer('\000' * buffer_size)
            self.nidaq.DAQmxGetErrorString(err,ctypes.byref(buffer), buffer_size)
            raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))

if __name__ == '__main__':

    from src.core import Instrument

    instr, failed = Instrument.load_and_append({'galvo':'DAQ'})
    print(instr)
    print(failed)