# Author: Jan Gieseler
# Date: 03/03/2016
# This is a collection of script that use the ZI HF2  Lock-in amplifier
import time

import helper_functions.reading_writing as rw
import matplotlib.pyplot as plt
import numpy as np

from src import old_hardware_modules as ZI


def find_peak_and_measure(zi, f_min, f_max, df_coarse, df_fine, N_fine, samplesPerPt = 1):
    '''
    searches for a peak in the frequency range [f_min, f_max] by performing a quick scan
    and subsequentially takes a high resolution scan of the peak
    :param zi ZIHF2 object
    :param f_min lower bound of frequency range
    :param f_max upper bound of frequency range
    :param df_coarse frequency step size for quick scan
    :param df_fine frequency step size for high resolution scan
    :param N_fine number of point for high resolution scan
    :param samplesPerPt number of samples to take at each point
    :return:
    '''


    # perform fast sweep
    sampleNum = int((f_max- f_min) / df_coarse)
    zi.sweep(f_min, f_max, sampleNum, samplesPerPt)
    # find maximum value
    data_coarse = np.array(zi.dataFinal)

    # calculate range for high resolution scan
    f= data_coarse[:,0]
    r2 = data_coarse[:,1]**2 + data_coarse[:,2]**2
    fo = f[np.argmax(r2)]

    f_min_high_res, f_max_high_res = fo- df_fine*N_fine/2, fo+ df_fine*N_fine/2
    # perform high resolution sweep
    zi.sweep(f_min_high_res, f_max_high_res, N_fine, 1)
    data_high_res = np.array(zi.dataFinal)
    return data_coarse, data_high_res

def find_peak(zi, f_min, f_max, df, samplesPerPt = 1):
    '''
    searches for a peak in the frequency range [f_min, f_max]
    :param zi ZIHF2 object
    :param f_min lower bound of frequency range
    :param f_max upper bound of frequency range
    :param df frequency step
    :param samplesPerPt number of samples to take at each point
    :return: fo the frequency of the max value in the specified range
    '''


    # perform sweep
    sampleNum = int((f_max- f_min) / df)
    zi.sweep(f_min, f_max, sampleNum, samplesPerPt)
    # find maximum value
    data = np.array(zi.dataFinal)

    # calculate range for high resolution scan
    f= data[:,0]
    r2 = data[:,1]**2 + data[:,2]**2
    fo = f[np.argmax(r2)]

    return fo


if __name__ == '__main__':

    zi_settings = {
        'amplitude' : 0.1e-3,
        'offset' : 1,
        'freq' : 1.88e6,
        'ACCoupling':1,
        'inChannel' : 0,
        'outChannel' : 0,
        'auxChannel' : 0,
        'add' : 1,
        'range' : 10e-3
    }


    peak_search_settings = {
        'f_min': 1875.0e3,
        'f_max': 1878.0e3,
        'df_coarse' : 5,
        'df_fine': 1,
        'N_fine': 101,
        'samplesPerPt' : 1
    }

    find_peak_settings = {
        'f_min': 1875.0e3,
        'f_max': 1878.0e3,
        'df' : 5,
        'samplesPerPt' : 1
    }

    ## TEST SCRIPT TO Track Peak

    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20160302_Resonator_2.2\\20160303_Cold_Resonator_2.2\\data_track_peak\\'
    tag = 'resonator_2.2'


    zi = ZI.ZIHF2(**zi_settings)
    max_frequencies = []
    f_range = find_peak_settings['f_max'] - find_peak_settings['f_min']
    recording = True
    i = 0
    while recording:
        fo = find_peak(zi, **find_peak_settings)
        max_frequencies.append([time.strftime("%Y-%m-%d_%H-%M-%S"), fo])
        find_peak_settings.update({'f_min': fo-f_range/2, 'f_max' : fo+f_range/2})
        i+=1
        if i>10:
            recording = False
        print(i, fo)


    # save data
    rw.save_data(max_frequencies, dirpath, tag + '_frequencies')


    rw.save_json(zi_settings, dirpath + rw.date_prefix() + tag + '_zi_settings.json')
    rw.save_json(find_peak_settings, dirpath + rw.date_prefix() + tag + '_peak_settings.json')

    plt.show()

    ## ====================  TEST SCRIPT T FIND PEAK ========================

    # dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20160302_Resonator_2.2\\20160303_Cold_Resonator_2.2\\data\\'
    # tag = 'resonator_2.2'
    #
    #
    # zi = ZI.ZIHF2(**zi_settings)
    #
    # data_coarse, data_high_res = find_peak_and_measure(zi, **peak_search_settings)
    #
    # f= data_coarse[:,0]
    # r2 = data_coarse[:,1]**2 + data_coarse[:,2]**2
    # plt.plot(f, r2)
    #
    # f= data_high_res[:,0]
    # r2 = data_high_res[:,1]**2 + data_high_res[:,2]**2
    # plt.plot(f, r2)
    #
    # # save data
    # rw.save_data(data_coarse, dirpath, tag + '_coarse')
    # rw.save_data(data_high_res, dirpath, tag + '_high_res')
    #
    #
    # rw.save_json(zi_settings, dirpath + rw.date_prefix() + tag + '_zi_settings.json')
    # rw.save_json(peak_search_settings, dirpath + rw.date_prefix() + tag + '_search_settings.json')
    #
    # plt.show()