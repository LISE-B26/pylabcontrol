from copy import deepcopy

import numpy as np
import scipy.signal as signal
from peakutils.peak import indexes # package required https://pypi.python.org/pypi/PeakUtils

from b26_toolkit.src.data_processing.fit_functions import fit_lorentzian, guess_lorentzian_parameter


def fit_esr(freq, ampl):
    freqs_peaks, ampl_peaks = find_nv_peaks(freq, ampl)

    # figure out if one or two peaks
    if freqs_peaks[0] == freqs_peaks[1]:
        start_vals = guess_lorentzian_parameter(freq, ampl)
    elif freqs_peaks[0] == 0:
        print('data too noisy!!')
        # later we can extend this to fit a Lorenzian to each peak, for now we assume it's noisy data..
    else:
        center_freq = np.mean(freqs_peaks)
        start_vals = []
        start_vals.append(guess_lorentzian_parameter(freq[freq < center_freq], ampl[freq < center_freq]))
        start_vals.append(guess_lorentzian_parameter(freq[freq > center_freq], ampl[freq > center_freq]))
        # we already have a good estimate for the peak position, so update that
        start_vals[0][2], start_vals[1][2] = freqs_peaks

    try:
        fit = fit_lorentzian(freq, ampl, starting_params=start_vals)
    except:
        print('XXX ESR fit failed!')
        fit = None

    return fit

def find_nv_peaks(freq, data, width_Hz=0.005e9, initial_threshold = 0.00, steps_size = 0.05, ax=None):
    """
    finds the single peak or double peak frequencies of esr spectrum
    Args:
        freq: frequnency points of esr spectrum
        data: data points of esr spectrum
        width_Hz: expected width of peak
        ax: optional axes object to plot processed data

    Returns:
        freq_max: peak frequency(ies)
        data_max: esr signal at peak frequency(ies)

    """


    freq_to_mag = 1. / (2 * 2.8e6)  # conversion factor from frequency to magentic field in Gauss (1/(2*gyromag ratio))

    def find_peaks_pts(data, width, initial_threshold, steps_size):
        """
        find the maximum points in data
        Args:
            data: processed data that has one or two Gaussian like features
            width: expected width of features

        Returns:
            idx, data[idx]
            index and value of peaks

        """

        threshold = initial_threshold  # initial threshold
        continue_search = True
        # number of peaks of previous attempt
        number_peaks_previous = -1


        while continue_search:
            idx = indexes(np.array(data), thres=threshold, min_dist=width)
            #             print(idx)
            if len(idx) > 2:
                threshold += steps_size
            elif len(idx) == 2:
                # double peak detected, maybe need to check if reasonable here
                continue_search = False
            elif len(idx) == 1:
                # single peak detected
                continue_search = False
            elif len(idx) == 0:
                # peak detection in this iteration but was successful before
                # this means that we should go back and raise the threshold slower
                if number_peaks_previous >0:
                    threshold -= steps_size # go back to previous threshold that was successful
                    steps_size /= 2. # reduce stepsize by factor 2
                else:
                    # search failed
                    continue_search = False

            number_peaks_previous = len(idx)

        return idx, data[idx]

    def check_double_peak(freq_max, peak_max):
        """
        checks if double peak is physical of not return the frequency and value of the physical peak
        Args:
            freq_max: vector of length 2 with the frequencies of the two peaks
            peak_max: value of two peaks

        Returns:
            freq_max, peak_max
            vectors of length one or two that contain the frequencies and values of the peak(s)

        """
        assert len(freq_max) == 2

        fo = 2.878  # NV center frequency without Zeeman shift

        # calculate symmetry with respect to expected center freq
        df = np.abs(freq_max - fo)
        asymmetry_f = max(df) / min(df) - 1
        # calculate symmetry with respect to peak height
        asymmetry_p = np.abs(np.diff(peak_max) / np.mean(peak_max))[0]
        #
        # print('freq_o', np.mean(freq_max),
        #       'asymmetry f', asymmetry_f,
        #       'asymmetry p', asymmetry_p)

        if asymmetry_p > 1:
            freq_max = [freq_max[np.argmax(peak_max)]]

        return freq_max

    #         check symmetry with respect to unshifted NV center symmetry


    # get width in pts
    df = np.mean(np.diff(freq))
    width_pts = int(width_Hz / df)

    #
    sig = deepcopy(data)
    sig /= np.mean(sig)
    sig -= 1
    sig *= -1.0

    # smooth signal with filter
    # int(width_pts/2)*2*3+1: to get a window size about three times the width and odd number
    win = signal.gaussian(int(width_pts / 2) * 2 * 3 + 1, std=width_pts)

    sig_filtered = signal.convolve(sig, win, mode='same') / sum(win)
    max_idx, max_pts = find_peaks_pts(sig_filtered, width_pts, initial_threshold, steps_size)

    if len(max_idx) == 2:
        freq_max = check_double_peak(freq[max_idx], max_pts)
        if len(freq_max) == 1:
            data_max = [dx for (fx, dx) in zip(freq, data) if fx == freq_max]
            max_pts = [dx for (fx, dx) in zip(freq, sig_filtered) if fx == freq_max]
        else:
            data_max = data[max_idx]
    elif len(max_idx) == 1:
        freq_max = freq[max_idx]
        data_max = data[max_idx]
    else:
        freq_max = [0, 0]
        data_max = [0, 0]
        max_pts = [0, 0]
        print('No peak found!!!')

    # for a single peak we still return two (identical) values, this makes further processing easier
    if len(freq_max) == 1:
        freq_max = [freq_max[0], freq_max[0]]
        max_pts = [max_pts[0], max_pts[0]]
        data_max = [data_max[0],data_max[0]]

    if ax is not None:
        ax.plot(freq, sig)
        ax.plot(freq, sig_filtered)
        if freq_max[1] != 0:
            ax.plot(freq_max, max_pts, 'o')

        if freq_max[0] == freq_max[1] and freq_max[1] != 0:
            ax.set_title('single: {:e}'.format(freq_max[0]))
        else:
            ax.set_title('mag field: {:e} Gauss'.format(freq_to_mag * np.abs(freq_max[0] - freq_max[1])))

    return freq_max, data_max
