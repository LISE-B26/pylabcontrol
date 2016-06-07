import scipy.signal as signal
from copy import deepcopy
import numpy as np
from peakutils.peak import indexes # package required https://pypi.python.org/pypi/PeakUtils



def find_nv_peaks(freq, data, width_Hz=0.005e9, ax=None):
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
    def find_peaks_pts(data, width):
        """
        find the maximum points in data
        Args:
            data: processed data that has one or two Gaussian like features
            width: expected width of features

        Returns:
            idx, data[idx]
            index and value of peaks

        """

        threshold = 0.05  # initial threshold
        continue_search = True
        while continue_search:
            idx = indexes(np.array(data), thres=threshold, min_dist=width)
            #             print(idx)
            if len(idx) > 2:
                threshold = threshold + 0.05
            elif len(idx) == 2:
                # double peak detected, maybe need to check if reasonable here
                continue_search = False
            elif len(idx) == 1:
                # single peak detected
                continue_search = False
            elif len(idx) == 0:
                # peak detection failed
                continue_search = False
        return idx, data[idx]

    def check_double_peak(freq_max, peak_max):
        """
        checks if double peak is physical of not return the frequency and value of the physical peak
        Args:
            freq_max: vector of length 2 with the frequencies of the two peaks
            peak_max: value of two peaks

        Returns:
            freq_max, peak_max
            vectors of length one or two that contain the frequncies and values of the peak(s)

        """
        assert len(freq_max) == 2

        fo = 2.878  # NV center frequency without Zeeman shift

        # calculate symmetry with respect to expected center freq
        df = np.abs(freq_max - fo)
        asymmetry_f = max(df) / min(df) - 1
        # calculate symmetry with respect to peak height
        asymmetry_p = np.abs(np.diff(peak_max) / np.mean(peak_max))[0]

        print('freq_o', np.mean(freq_max),
              'asymmetry f', asymmetry_f,
              'asymmetry p', asymmetry_p)

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
    max_idx, max_pts = find_peaks_pts(sig_filtered, width_pts)

    if len(max_idx) == 2:
        freq_max = check_double_peak(freq[max_idx], max_pts)
        if len(freq_max) == 1:
            data_max = [dx for (fx, dx) in zip(freq, data) if fx == freq_max]
            max_pts = [dx for (fx, dx) in zip(freq, sig_filtered) if fx == freq_max]
        else:
            data_max = data[max_idx]

    else:
        freq_max = freq[max_idx]
        data_max = data[max_idx]

    if ax is not None:
        ax.plot(freq, sig)
        ax.plot(freq, sig_filtered)
        ax.plot(freq_max, max_pts, 'o')

        if len(freq_max) == 1:
            ax.set_title('single: {:e}'.format(freq_max[0]))
        if len(freq_max) == 2:
            ax.set_title('double diff: {:e}'.format(max_pts[1] - max_pts[0]))

    return freq_max, data_max