import numpy as np


def plot_psd(freq, psd,  axes, clear = True):
    '''
    plots the power spectral density on to the canvas axes
    :param freq: x-values array of length N
    :param psd: y-values array of length N
    :param axes: target axes object
    :return: None
    '''
    if clear is True:
        print('CLEAR')
        axes.clear()

    if np.mean(freq) > 1e6:
        freq /= 1e6
        unit = 'MHz'
    elif np.mean(freq) > 1e3:
        freq /= 1e3
        unit = 'kHz'

    axes.semilogy(freq, psd)

    axes.set_xlabel('frequency ({:s})'.format(unit))