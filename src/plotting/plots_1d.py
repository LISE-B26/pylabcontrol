import collections
import matplotlib.pyplot as plt
import time
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches
import numpy as np

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


def plot_esr(axes, frequency, data, fit_params=None):
    """
    plots the esr
    Args:
        axes:
        fit_params:
        frequency: mw frequency
        data:


    Returns:

    """
    def lorentzian(x, amplitude, width, center, offset):
        return (-(amplitude*(.5*width)**2)/((x-center)**2+(.5*width)**2))+offset

    if fit_params is None:
        fit_data = None
    elif not fit_params[0] == -1:  # check if fit failed
        fit_data = lorentzian(frequency, fit_params[0], fit_params[1], fit_params[2], fit_params[3])
    else:
        fit_data = None

    if fit_data is not None:  # plot esr and fit data
        lines = axes.plot(frequency, data, 'b', frequency, fit_data, 'r')
        axes.set_title('ESR fo = {:0.4e}, wo = {:0.2e}'.format(fit_params[2], fit_params[1]))
        axes.set_xlabel('Frequency (Hz)')
        axes.set_ylabel('Kcounts/s')
    else:  # plot just esr data
        lines = axes.plot(frequency, data, 'b')
        axes.set_title('ESR')
        axes.set_xlabel('Frequency (Hz)')
        axes.set_ylabel('Kcounts/s')
    axes.hold(False)
    return lines


def plot_pulses(axis, pulse_collection, pulse_colors=None):
    """
    creates a visualization of pulses (in pulse_collection) on a matplotlib axis (axis)

    Args:
        axis: The axis for the matplotlib plot
        pulse_collection: a collection of pulses, named tuples (channel_id, start_time, duration)
        pulse_colors: a dictionary of {channel_id:matplotlib_color} that maps channels to colors

    Returns:

    """

    # create a list of unique instruments from the pulses
    instrument_names = sorted(list(set([pulse.channel_id for pulse in pulse_collection])))

    # assign colors for certain specific channels
    if pulse_colors is None:
        pulse_colors = {'laser': 'g', 'microwave_i': 'r', 'apd_readout': 'k'}

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

    # create a vertical line denoting the end of the pulse sequence loop
    axis.axvline(max_time, -0.5, len(instrument_names), color='r')

    # create rectangles for the pulses
    patch_list = []
    for pulse in pulse_collection:
        patch_list.append(
            patches.Rectangle((pulse.start_time, instrument_names.index(pulse.channel_id)), pulse.duration, 0.5,
                              fc=pulse_colors.get(pulse.channel_id, 'b')))

    patch_collection = PatchCollection(patch_list, match_original=True)
    axis.add_collection(patch_collection)

    # label the axis
    axis.set_title('Pulse Visualization')
    axis.set_xlabel('time [ns]')
    axis.set_ylabel('pulse destination')


def update_pulse_plot(axis, pulse_collection, pulse_colors=None):
    """
    updates a previously created plot of pulses, removing the previous ones and adding ones corresponding to
    pulse_collection. The new pulse collection must only contain channel_ids already present on the passed axis

    Args:
        axis: The axis for the matplotlib plot
        pulse_collection: a collection of pulses, named tuples (channel_id, start_time, duration)
        pulse_colors: a dictionary of {channel_id:matplotlib_color} that maps channels to colors

    Returns:

    """

    # assign colors for certain specific channels
    if pulse_colors is None:
        pulse_colors = {'laser': 'g', 'microwave_i': 'r', 'apd_readout': 'k'}

    # get a list of unique instruments from the pulses
    instrument_names = [str(label.get_text()) for label in axis.get_yticklabels()]

    # find the maximum time from the list of pulses
    max_time = max([pulse.start_time + pulse.duration for pulse in pulse_collection])

    # axis.set_xlim(0, 1.1 * max_time)

    # remove the previous pulses
    [child.remove() for child in axis.get_children() if isinstance(child, PatchCollection)]

    # create rectangles for the pulses
    patch_list = []
    for pulse in pulse_collection:
        patch_list.append(
            patches.Rectangle((pulse.start_time, instrument_names.index(pulse.channel_id)), pulse.duration, 0.5,
                              fc=pulse_colors.get(pulse.channel_id, 'b')))

    patch_collection = PatchCollection(patch_list, match_original=True)
    axis.add_collection(patch_collection)

def plot_counts(axis, data):
    axis.plot(data)
    axis.hold(False)

    axis.set_xlabel('time')
    axis.set_ylabel('kCounts/sec')


def plot_1d_simple(axis, times, counts_list, x_label='time (ns)', y_label='kCounts/sec', title=None):
    for counts in counts_list:
        axis.plot(times, counts)

    axis.hold(False)

    axis.set_xlabel(x_label)
    axis.set_ylabel(y_label)
    if title:
        axis.set_title(title)
    axis.set_xlim([min(times), max(times)])


def update_1d_simple(axis, times, counts_list):
    """

    Args:
        axis: axes object
        times: JG: THIS IS NOT USED! WHAT IS IT? => add comment, e.g. for future purpose or delete!
        counts_list: list of

    Returns:

    """
    if len(axis.lines) != len(counts_list):
        counts_list = np.transpose(counts_list)

    assert len(axis.lines) == len(counts_list)
    for index, counts in enumerate(counts_list):
        axis.lines[index].set_ydata(counts)
    axis.relim()
    axis.autoscale_view()
