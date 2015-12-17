__author__ = 'Experiment'
import functions.plot_save_AI as AIO


#plot_AI('Dev1/AI0', 20000, 20)

freq = 50000
acq_time = 5
AIO.save_AI_toRAM('Dev1/AI0', freq, acq_time, 'Z:\\Lab\\Cantilever\\Measurements\\151123_Interferometer\\interferometer_timetraces', 'NoLight_Gain_1e2_Filter_DC_3MHz_AcqTime_{:0d}s_SampleFreq_{:05d}Hz'.format(acq_time, freq))


#
# freq = 500
# acq_time = 200
# AIO.save_AI_toRAM('Dev1/AI0', freq, acq_time, 'Z:\\Lab\\Cantilever\\Measurements\\151123_Interferometer\\interferometer_timetraces', 'interference_Gain_1e2_Filter_DC_100Hz_AcqTime_{:0d}s_SampleFreq_{:05d}Hz'.format(acq_time, freq))