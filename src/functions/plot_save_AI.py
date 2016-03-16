import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import hardware_modules as ReadAI


# Plots analog imput signal using pyplot
def plot_AI(device, freq, run_time):
    '''
    :param device: Device name in standard NI format ex. 'Dev1/AI0'
    :param freq: Sampling frequency (Hz). Greatly exceeding 100 kHz will result in data being written faster than it can be read and will crash program
    :param run_time: Time for which to sample (s). Reading for more than a minute or so (depending on sampling rate) will overload matplotlib
    :return: None
    '''
    ai = ReadAI.ReadAI(device, freq)
    ai.run()
    plotting = 0
    num_samps_read = 0
    while num_samps_read < freq*run_time:
        new_data = ai.read()
        num_samps_read += new_data.__len__()
        if(plotting == 0):
            fig = plt.figure(1)
            plt.ion()
            plt.clf()
            data = new_data
            time_mat = np.linspace(0,float(num_samps_read)/freq, num_samps_read)
            plt.plot(time_mat, data, 'b')
            plt.grid(True)
            plt.autoscale()
            plt.show(block = False)
            plotting = 1
            plt.pause(.1)
        else:
            plt.clf
            data = np.append(data, new_data)
            time_mat = np.linspace(0,float(num_samps_read)/freq, num_samps_read)
            plt.plot(time_mat, data,'b')
            plt.draw()
            plt.pause(.1)
    ai.stop()

# Saves AI input to file
def save_AI(device, freq, run_time, dirpath, tag):
    '''
    :param device: Device name in standard NI format ex. 'Dev1/AI0'
    :param freq: Sampling frequency (Hz). Greatly exceeding 100 kHz will result in data being written faster than it can be read and will crash program
    :param run_time: Time for which to sample (s). Reading for more than a minute or so (depending on sampling rate) will overload matplotlib
    :param dirpath: Path in which to save data
    :param tag: tag for file
    :return: None
    '''
    ai = ReadAI.ReadAI(device, freq)
    ai.run()
    num_samps_read = 0
    header = False
    day = time.strftime("%d")
    month = time.strftime("%m")
    year = time.strftime("%Y")
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    filename = '\\' + year + '-' + month + '-' + day + '_' + hour + '-' + minute + '-' + second  +'-' + str(tag)
    filepathCSV = dirpath + filename + '.csv'
    while num_samps_read < freq*run_time:
        new_data = ai.read()
        num_samps_read += new_data.__len__()
        time_mat = np.arange(float(num_samps_read-new_data.__len__())/freq,float(num_samps_read)/freq, step=1/float(freq))
        array = [time_mat, new_data]
        df = pd.DataFrame(array)
        df.to_csv(filepathCSV, index = False, header=header, mode = 'a')
    ai.stop()

# Saves AI input to file, keeping all data in memory until after reading in order to prevent slowdown due to disk access
# and allow higher frequency reads
def save_AI_toRAM(device, freq, run_time, dirpath, tag):
    '''
    :param device: Device name in standard NI format ex. 'Dev1/AI0'
    :param freq: Sampling frequency (Hz). Greatly exceeding 100 kHz will result in data being written faster than it can be read and will crash program
    :param run_time: Time for which to sample (s). Reading for more than a minute or so (depending on sampling rate) will overload matplotlib
    :param dirpath: Path in which to save data
    :param tag: tag for file
    :return: None
    '''
    ai = ReadAI.ReadAI(device, freq)
    ai.run()
    num_samps_read = 0
    header = False
    day = time.strftime("%d")
    month = time.strftime("%m")
    year = time.strftime("%Y")
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    filename = '\\' + year + '-' + month + '-' + day + '_' + hour + '-' + minute + '-' + second  +'-' + str(tag)
    filepathCSV = dirpath + filename + '.csv'
    data = []
    while num_samps_read < freq*run_time:
        data = np.append(data, ai.read())
        num_samps_read = data.__len__()
        print(num_samps_read)
    time_mat = np.arange(0,float(num_samps_read)/freq, step=1/float(freq))
    array = np.row_stack((time_mat, data))
    np.savetxt(filepathCSV, array, delimiter=',') # direct save instead of pandas to prevent copying array into dataframe/reduce memory
    ai.stop()

# Corresponds to running both plot_AI and save_AI as above
def save_and_plot_AI(device, freq, run_time, dirpath, tag):
    '''
    :param device: Device name in standard NI format ex. 'Dev1/AI0'
    :param freq: Sampling frequency (Hz). Greatly exceeding 100 kHz will result in data being written faster than it can be read and will crash program
    :param run_time: Time for which to sample (s). Reading for more than a minute or so (depending on sampling rate) will overload matplotlib
    :param dirpath: Path in which to save data
    :param tag: tag for file
    :return: None
    '''
    ai = ReadAI.ReadAI(device, freq)
    ai.run()
    plotting = 0
    num_samps_read = 0
    header = False
    day = time.strftime("%d")
    month = time.strftime("%m")
    year = time.strftime("%Y")
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    filename = '\\' + year + '-' + month + '-' + day + '_' + hour + '-' + minute + '-' + second  +'-' + str(tag)
    filepathCSV = dirpath + filename + '.csv'
    filepathJPG = dirpath + filename + '.jpg'
    while num_samps_read < freq*run_time:
        new_data = ai.read()
        num_samps_read += new_data.__len__()
        if(plotting == 0):
            fig = plt.figure(1)
            plt.ion()
            plt.clf()
            data = new_data
            time_mat = np.linspace(0,float(num_samps_read)/freq, num_samps_read)
            plt.plot(time_mat, data, '.b')
            plt.title('%s Voltage' % device)
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            plt.grid(True)
            plt.autoscale()
            plt.show(block = False)
            plotting = 1
            plt.pause(.1)
        else:
            plt.clf
            data = np.append(data, new_data)
            time_mat_new = np.linspace(float(time_mat.__len__())/freq,float(num_samps_read)/freq, num_samps_read)
            plt.plot(time_mat, data,'.b')
            plt.draw()
            plt.pause(.1)
        time_mat_save = np.arange(float(num_samps_read-new_data.__len__())/freq,float(num_samps_read)/freq, step=1/float(freq))
        array = [time_mat, new_data]
        df = pd.DataFrame(array)
        df.to_csv(filepathCSV, index = False, header=header, mode = 'a')
    fig.savefig(str(filepathJPG), format = 'jpg')
    ai.stop()

save_AI('Dev1/AI2', 1000, 30000, "Z:/Lab/Cantilever/Measurements/20160301_ResonatorDrift", 'PLL')
