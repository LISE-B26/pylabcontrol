import hardware_modules.GalvoMirrors as DaqOut
from hardware_modules import APD as APDIn
from hardware_modules import MicrowaveGenerator
# import standard libraries
import numpy as np
import matplotlib.pyplot
import scipy.optimize as opt


RANGE_STEP = 1000000 #32 MHz steps
MIN_MOD_VOLTAGE = -1
MAX_MOD_VOLTAGE = +1


def esr(rf_power,freq_values,(nv_x,nv_y) = (None,None), num_avg = 1, int_time = .001, settle_time = .0002):
    freq_range = max(freq_values)-min(freq_values)
    num_freq_sections = freq_range%RANGE_STEP + 1
    clock_adjust = (int_time+settle_time)/settle_time
    freq_array = np.repeat(freq_values, clock_adjust)
    dt = (int_time+settle_time)/clock_adjust
    mwgen = MicrowaveGenerator.SG384()
    mwgen.setAmplitude(rf_power)
    mwgen.modOn()
    mwgen.setModFreq()
    mwgen.setModExt()

    #move to NV point if given
    if not (nv_x is None):
        initPt = np.transpose(np.column_stack((nv_x,nv_y)))
        initPt = (np.repeat(np.initPt, 2, axis=1))
        # move galvo to first point in line
        pointthread = DaqOut.DaqOutputWave(initPt, 1 / dt, "Dev1/ao0:1")
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()

    esr_data = np.zeros(len(freq_values))

    for scan_num in xrange(0,num_avg):
        esr_data_pos = 0
        for sec_num in xrange(0,num_freq_sections):
            # initialize APD thread
            sec_min = min(freq_values)+RANGE_STEP*sec_num
            sec_max = sec_min+RANGE_STEP
            freq_section_array = freq_array[np.where( freq_array >= sec_min and freq_array < sec_max) ]
            if not freq_section_array:
                continue
            center_freq = (sec_max+sec_min)/2
            freq_voltage_array = ((freq_section_array-sec_min)/RANGE_STEP)*2 - 1 #normalize voltages to +-1 range

            mwgen.setFreq(center_freq)
            mwgen.outputOn()

            readthread = APDIn.ReadAPD("Dev1/ctr0", 1 / dt,
                                       len(freq_voltage_array) + 1)
            writethread = DaqOut.DaqOutputWave(freq_voltage_array, 1 / dt,
                                               "Dev1/ao2")
            # start counter and scanning sequence
            readthread.runCtr()
            writethread.run()
            writethread.waitToFinish()
            writethread.stop()
            raw_data = readthread.read()
            diff_data = np.diff(raw_data)
            summed_data = np.zeros(len(freq_voltage_array)/clock_adjust)
            for i in range(0,int((len(freq_voltage_array)/clock_adjust))):
                summed_data[i] = np.sum(diff_data[(i*clock_adjust+1):(i*clock_adjust+clock_adjust-1)])
            #also normalizing to kcounts/sec
            esr_data[esr_data_pos:(esr_data_pos + len(summed_data))] = summed_data*(.001/int_time)
            # clean up APD tasks
            readthread.stopCtr()
            readthread.stopClk()

            fit_esr(freq_values, esr_data)

def fit_esr(freq_values, esr_data, fit_start_params = None):
    if(fit_start_params is None):
        offset = np.mean(esr_data)
        amplitude = np.max(esr_data)-np.min(esr_data)
        center = freq_values[esr_data.argmin()]
        width = 10000000 #10 MHz arbitrarily chosen as reasonable
        fit_start_params = [amplitude, width, center, offset]

    def lorentzian(x, amplitude, width, center, offset):
        return (-(amplitude*(.5*width)**2)/((x-center)**2+(.5*width)**2))+offset

    return opt.curve_fit(lorentzian, freq_values, esr_data, fit_start_params)



