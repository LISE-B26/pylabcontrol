def plot_psd(freq, psd, axes, clear = True):
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


def plot_esr(fit_params, frequency, data, axes):

    def lorentzian(x, amplitude, width, center, offset):
        return (-(amplitude*(.5*width)**2)/((x-center)**2+(.5*width)**2))+offset

    if not fit_params[0] == -1:  # check if fit failed
        fit_data = lorentzian(frequency, fit_params[0], fit_params[1], fit_params[2], fit_params[3])
    else:
        fit_data = None
    if fit_data is not None:  # plot esr and fit data
        axes.plot(frequency, data, 'b', frequency, fit_data, 'r')
        axes.set_title('ESR fo = {:0.2e}, wo = {:0.2e}'.format(fit_params[2], fit_params[1]))
        axes.set_xlabel('Frequency (Hz)')
        axes.set_ylabel('Kcounts/s')
    else:  # plot just esr data
        axes.plot(frequency, data, 'b')
        axes.set_title('ESR')
        axes.set_xlabel('Frequency (Hz)')
        axes.set_ylabel('Kcounts/s')