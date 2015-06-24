import hardware_modules.GalvoMirrors as DaqOut
from hardware_modules import APD as APDIn
from hardware_modules import MicrowaveGenerator
# import standard libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import time

RANGE_MIN = 2025000000 #2.025 GHz
RANGE_MAX = 4050000000 #4.050 GHZ
RANGE_DEV = 32000000 #32 MHz maximum deviation
RANGE_STEP = RANGE_DEV * 2 #maximum range for a given center frequency
MIN_MOD_VOLTAGE = -1
MAX_MOD_VOLTAGE = +1


def esr(rf_power,freq_values,(nv_x,nv_y) = (None,None), num_avg = 1, int_time = .001, settle_time = .0002):
    freq_range = max(freq_values)-min(freq_values)
    num_freq_sections = int(freq_range) / int(RANGE_STEP) + 1
    print(num_freq_sections)
    clock_adjust = (int_time+settle_time)/settle_time
    freq_array = np.repeat(freq_values, clock_adjust)
    dt = (int_time+settle_time)/clock_adjust
    mwgen = MicrowaveGenerator.SG384()
    #mwgen.setAmplitude(rf_power)
    mwgen.modOn()
    mwgen.setModFreq()
    mwgen.setModExt()
    mwgen.setModFreqDeviation(RANGE_DEV)
    plotting = False

    #move to NV point if given
    if not (nv_x is None):
        initPt = np.transpose(np.column_stack((nv_x,nv_y)))
        initPt = (np.repeat(initPt, 2, axis=1))
        # move galvo to first point in line
        pointthread = DaqOut.DaqOutputWave(initPt, 1 / dt, "Dev1/ao0:1")
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()

    esr_data = np.zeros((num_avg, len(freq_values)))

    for scan_num in xrange(0,num_avg):
        esr_data_pos = 0
        #mwgen.outputOn()
        for sec_num in xrange(0,num_freq_sections):
            # initialize APD thread
            sec_min = min(freq_values)+RANGE_STEP*sec_num
            sec_max = sec_min+RANGE_STEP
            freq_section_array = freq_array[np.where(np.logical_and(freq_array >= sec_min, freq_array < sec_max))]
            print(len(freq_section_array))
            if (len(freq_section_array) == 0):
                continue
            center_freq = (sec_max+sec_min)/2
            freq_voltage_array = ((freq_section_array-sec_min)/RANGE_STEP)*2 - 1 #normalize voltages to +-1 range

            mwgen.setFreq(center_freq)

            readthread = APDIn.ReadAPD("Dev1/ctr0", 1 / dt,
                                       len(freq_voltage_array) + 1, 100000)
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
            esr_data[scan_num, esr_data_pos:(esr_data_pos + len(summed_data))] = summed_data*(.001/int_time)
            esr_data_pos += len(summed_data)
            # clean up APD tasks
            readthread.stopCtr()
            readthread.stopClk()

        esr_avg = np.mean(esr_data[0:(scan_num + 1)], axis=0)
        mwgen.outputOff()
        fit_params,_ = fit_esr(freq_values, esr_avg)
        plot_esr(freq_values, esr_avg, fit_params)
        plotting = True
    plt.show()


def fit_esr(freq_values, esr_data, fit_start_params = None):
    if(fit_start_params is None):
        offset = np.mean(esr_data)
        amplitude = np.max(esr_data)-np.min(esr_data)
        center = freq_values[esr_data.argmin()]
        width = 10000000 #10 MHz arbitrarily chosen as reasonable
        fit_start_params = [amplitude, width, center, offset]
    try:
        return opt.curve_fit(lorentzian, freq_values, esr_data, fit_start_params)
    except RuntimeError:
        print('Lorentzian fit failed')
        return (-1,-1,-1,-1),'Ignore'


def plot_esr(freq_values, esr_data, fit_params):
    plt.clf()
    if not fit_params[0] == -1:
        fit_data = lorentzian(freq_values, fit_params[0], fit_params[1], fit_params[2], fit_params[3])
        plt.plot(freq_values, esr_data, freq_values, fit_data)
    else:
        plt.plot(freq_values, esr_data)
    plt.title('ESR')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Kcounts/s')
    plt.show(block=False)
    plt.pause(.1) #required to force figure update, otherwise window hangs before displaying plot


def lorentzian(x, amplitude, width, center, offset):
    return (-(amplitude*(.5*width)**2)/((x-center)**2+(.5*width)**2))+offset


test_freqs = np.linspace(2500000000,2500010000,3000)
esr(0,test_freqs, num_avg=2)