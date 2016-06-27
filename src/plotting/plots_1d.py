import collections
import matplotlib.pyplot as plt
import time

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
        lines = axes.plot(frequency, data, 'b', frequency, fit_data, 'r')
        axes.set_title('ESR fo = {:0.2e}, wo = {:0.2e}'.format(fit_params[2], fit_params[1]))
        axes.set_xlabel('Frequency (Hz)')
        axes.set_ylabel('Kcounts/s')
    else:  # plot just esr data
        lines = axes.plot(frequency, data, 'b')
        axes.set_title('ESR')
        axes.set_xlabel('Frequency (Hz)')
        axes.set_ylabel('Kcounts/s')
    return lines



def plot_pulses(axis, pulse_collection):
    """
    creates a visualization of pulses (in pulse_collection) on a matplotlib axis (axis)

    Args:
        axis: The axis for the matplotlib plot
        pulse_collection: a collection of pulses, named tuples (pulse_name, start_time, duration)

    Returns:

    """

    # create a list of unique instruments from the pulses
    instrument_names = sorted(list(set([pulse.instrument_name for pulse in pulse_collection])))

    # find the maximum time from the list of pulses
    max_time = max([pulse.start_time + pulse.duration for pulse in pulse_collection])

    # set axis boundaries
    axis.set_ylim(-0.5, len(instrument_names))
    axis.set_xlim(0, 1.1 * max_time)

    # label y axis with pulse names
    axis.set_yticks(range(len(instrument_names)))
    axis.set_yticklabels(instrument_names)

    # create horizontal lines for each pulse
    for i in range(0, len(instrument_names)):
        axis.axhline(i, 0.0, max_time)

    # create rectangles for the pulses
    for pulse in pulse_collection:
        axis.add_patch(patches.Rectangle((pulse.start_time, instrument_names.index(pulse.instrument_name)), pulse.duration, 0.5))

    # label the axis
    axis.set_title('Pulse Visualization')
    axis.set_xlabel('time [s]')
    axis.set_ylabel('pulse destination')

def plot_counts(axis, data):
    axis.plot(data)

    axis.set_xlabel('time')
    axis.set_ylabel('kCounts/sec')

