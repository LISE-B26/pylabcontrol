


def plot_psd(freq, psd,  axes):
    '''
    plots the power spectral density on to the canvas axes
    :param freq: x-values array of length N
    :param psd: y-values array of length N
    :param axes: target axes object
    :return: None
    '''
    axes.clear()

    axes.semilogy(freq, psd)

    axes.set_xlabel('frequency (Hz)')
