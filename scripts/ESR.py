# B26 Lab Code
# Last Update: 7/1/15

# External Connections: Galvo x axis on DAQ AO channel 0
#                       Galvo y axis on DAQ AO channel 1
#                       SRS modulation input on DAQ AO channel 2
#                       APD input to counter 0 (PFI8)
#                       No external connection to counter 1 out (PFI13)
#                       GPIB connection to SRS SG384

import hardware_modules.GalvoMirrors as DaqOut
from hardware_modules import APD as APDIn
from hardware_modules import MicrowaveGenerator
# import standard libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import time
import pandas as pd

RANGE_MIN = 2025000000 #2.025 GHz
RANGE_MAX = 4050000000 #4.050 GHZ
RANGE_DEV = 32000000 #32 MHz maximum deviation from center frequency sest
RANGE_STEP = RANGE_DEV * 2 #maximum range for a given center frequency
MIN_MOD_VOLTAGE = -1 # minimum and maximum voltages put into signal generator to scan across
MAX_MOD_VOLTAGE = +1 # full frequency range

# Runs ESR, plotting it in pyplot and returning the data and lorentzian fit parameters
def run_esr(rf_power,freq_values,(nv_x,nv_y) = (None,None), num_avg = 1, int_time = .001, settle_time = .0002, plotting = True, canvas = None):
    '''
    rf_power: Power (in dBm) of signal generator before amplification. Must not exceed 0 dBm. If none, uses current RF power.
    freq_values: array of frequency values (in Hz) to use for ESR. Usually generate outside of function using np.linspace.
                 Must be between 2.025 GHz and 4.050 GHz.
    (nv_x,nv_y): tuple of nv coordinates (in galvo voltages). If none given, use current galvo location.
    num_avg: number of times to scan across frequency values and average the results
    int_time: time spent integrating at each frequency. Must be an integer multiple of settle_time
    settle_time: time spent waiting after daq changes voltage, corresponding to frequency change
    dirpath: path of directory in which to save data
    canvas: matplotlib backends canvas for gui integration. If not passed in, use pyplot.
    '''
    if(max(freq_values) > RANGE_MAX or min(freq_values) < RANGE_MIN):
        raise ValueError("Invalid frequency. All frequencies must be between 2.025 GHz and 4.050 GHz.")
    freq_values = np.sort(freq_values)
    freq_range = max(freq_values)-min(freq_values)
    num_freq_sections = int(freq_range) / int(RANGE_STEP) + 1
    clock_adjust = (int_time+settle_time)/settle_time
    freq_array = np.repeat(freq_values, clock_adjust)
    dt = (int_time+settle_time)/clock_adjust
    mwgen = init_mwgen(rf_power) # object pointing to microwave generator with proper initial settings

    #move to NV point if given
    if not (nv_x is None):
        move_to_NV((nv_x,nv_y))

    esr_data = np.zeros((num_avg, len(freq_values)))
    converge_data = []

    # run sweeps
    for scan_num in xrange(0,num_avg):
        print("Scan Number: " + str(scan_num))
        esr_data_pos = 0
        mwgen.outputOn()
        for sec_num in xrange(0,num_freq_sections):
            # initialize APD thread
            sec_min = min(freq_values)+RANGE_STEP*sec_num
            sec_max = sec_min+RANGE_STEP
            freq_section_array = freq_array[np.where(np.logical_and(freq_array >= sec_min, freq_array < sec_max))]
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
        fit_params,_ = fit_esr(freq_values, esr_avg)
        if(plotting == True):
            if not fit_params[0] == -1: # check if fit failed
                fit_data = lorentzian(freq_values, fit_params[0], fit_params[1], fit_params[2], fit_params[3])
                converge_data = np.append(converge_data,np.std(esr_data-fit_data))
            else:
                fit_data = None
                converge_data = np.append(converge_data,0)
            plot_esr(freq_values, esr_avg, fit_data = fit_data, converge_data = converge_data)
    mwgen.outputOff()
    plt.show()
    return esr_avg, fit_params

def init_mwgen(rf_power):
    mwgen = MicrowaveGenerator.SG384()
    if rf_power > 0:
      raise ValueError("Invalid RF power. Requested RF power must be below 0 dBm")
    elif rf_power is not None:
        mwgen.setAmplitude(rf_power)
    mwgen.modOn()
    mwgen.setModFreq()
    mwgen.setModExt()
    mwgen.setModFreqDeviation(RANGE_DEV)
    return mwgen

# sets the galvo voltages to move to the nv located at (nv_x,nv_y)
def move_to_NV((nv_x,nv_y)):
    if(abs(nv_x) > .5 or abs(nv_y) > .5):
        raise ValueError("Invalid nv coordinate, galvo voltages must not exceed +- .5 V")
    initPt = np.transpose(np.column_stack((nv_x,nv_y)))
    initPt = (np.repeat(initPt, 2, axis=1))
    # move galvo to first point in line
    pointthread = DaqOut.DaqOutputWave(initPt, 1 / .001, "Dev1/ao0:1")
    pointthread.run()
    pointthread.waitToFinish()
    pointthread.stop()

# fit ESR curve to lorentzian and return fit parameters. If initial guess known, put in fit_start_params, otherwise
# guesses reasonable initial values.
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

# dynamically plots the ESR curve and, if chosen, the fit to the curve and the convergence plot using pyplot
def plot_esr(freq_values, esr_data, fit_data = None, converge_data = None):
    plt.clf()
    if not (fit_data == None or converge_data == None): # plot esr, fit, and convergence data
        scan_array = np.linspace(1,len(converge_data),len(converge_data))
        plt.figure(1)
        plt.subplot(211)
        plt.plot(freq_values, esr_data, freq_values, fit_data)
        plt.title('ESR')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Kcounts/s')
        plt.subplot(212)
        plt.plot(scan_array, converge_data)
        plt.title('Convergence Plot')
        plt.xlabel('Scan Number')
        plt.ylabel('Deviation from Fit')
        plt.tight_layout()
    elif not (converge_data == None): # plot esr and convergence, prevents entire plot disappearing when one fit fails
        scan_array = np.linspace(1,len(converge_data),len(converge_data))
        plt.figure(1)
        plt.subplot(211)
        plt.plot(freq_values, esr_data)
        plt.title('ESR')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Kcounts/s')
        plt.subplot(212)
        plt.plot(scan_array, converge_data)
        plt.title('Convergence Plot')
        plt.xlabel('Scan Number')
        plt.ylabel('Deviation from Fit')
        plt.tight_layout()
    elif not (fit_data == None): # plot esr and fit data
        plt.plot(freq_values, esr_data, freq_values, fit_data)
        plt.title('ESR')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Kcounts/s')
    else: #plot just esr data
        plt.plot(freq_values, esr_data)
        plt.title('ESR')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Kcounts/s')

    if not (converge_data == None): # checks if called from inside esr_run, then runs dynamic plot
        plt.show(block=False)
        plt.pause(.1) #required to force figure update, otherwise window hangs before displaying plot
    else: # if called from outside esr_run, runs static plot
        plt.show()

# defines a lorentzian with some amplitude, width, center, and offset to use with opt.curve_fit
def lorentzian(x, amplitude, width, center, offset):
    return (-(amplitude*(.5*width)**2)/((x-center)**2+(.5*width)**2))+offset

# saves the esr_data to a timestamped file in the dirpath with a tag
def save_esr(esr_data, dirpath, tag = "", saveImage = True):
    df = pd.DataFrame(esr_data)
    start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    filepathCSV = dirpath + "\\" + start_time + '_' + tag + '.csv'
    df.to_csv(filepathCSV)

#EXAMPLE ESR CODE

#sample usage to scan 800 frequency points between 2.82 and 2.92 GHz
#test_freqs = np.linspace(2820000000,2920000000,800)
#esr_data, fit_params = run_esr(-40,test_freqs, num_avg=10)
#dirpath = 'Z:\\Lab\\Cantilever\\Measurements'
#tag = ''
#save_esr(esr_data, dirpath, tag)