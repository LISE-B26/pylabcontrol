import numpy as np
from scipy import optimize


# ========= Gaussian fit functions =============================
#===============================================================
def fit_gaussian(x_values, y_values, starting_params=None, bounds=None):
    """

    Args:
        x_values: domain of fit function
        y_values: y-values to fit
        starting_params: reasonable guesses for where to start the fitting optimization of the parameters. This is a
        length 4 list of the form [constant_offset, amplitude, center, width].
        bounds: Optionally, include bounds for the parameters in the gaussian fitting, in the following form:
                ([offset_lb, amplitude_lb, center_lb, width_lb],[offset_ub, amplitude_ub, center_ub, width_ub])

    Returns:
        a length-4 list of [fit_parameters] in the form [constant_offset, amplitude, center, width]

    """

    if bounds:
        fit_params = optimize.curve_fit(gaussian, x_values, y_values, p0=starting_params, bounds=bounds, max_nfev=2000)[0]
    else:
        fit_params = optimize.curve_fit(gaussian, x_values, y_values, p0=starting_params)[0]

    # todo: catch if fit is not successful and return all zeros

    return fit_params
def gaussian(x, constant_offset, amplitude, center, width):
    return constant_offset + amplitude * np.exp(-1.0 * (np.square((x - center)) / (2 * (width ** 2))))
def guess_gaussian_parameter(x_values, y_values):
    """
    guesses the parameters for a Gaussian dataset
    Args:
        x_values:
        y_values:

    Returns: estimated fit parameters for Gaussian fit
    """
    # todo: find a smarter algorith, in particular for the width, for now this function is only used in autofocus, but might be good to generalize
    noise_guess = np.min(y_values)
    amplitude_guess = np.max(y_values) - noise_guess
    center_guess = x_values[np.argmax(y_values)]
    width_guess = 0.8

    return [noise_guess, amplitude_guess, center_guess, width_guess]



# ========= Lorenzian fit functions =============================
#===============================================================
def fit_lorentzian(x_values, y_values, starting_params=None, bounds=None):
    """

    Args:
        x_values: domain of fit function
        y_values: y-values to fit
        starting_params: reasonable guesses for where to start the fitting optimization of the parameters. This is a
        length 4 list of the form [constant_offset, amplitude, center, full_width_half_max].
        bounds: Optionally, include bounds for the parameters in the gaussian fitting, in the following form:
                [(offset_lb, amplitude_lb, center_lb, fwhm_lb), (offset_ub, amplitude_ub, center_ub, fwhm_ub)]

    Returns:
        a length-4 list of [fit_parameters] in the form [constant_offset, amplitude, center, fwhm]

    """

    # defines a lorentzian with amplitude, width, center, and offset to use with opt.curve_fit
    if bounds:
        return optimize.curve_fit(lorentzian, x_values, y_values, p0=starting_params, bounds=bounds, max_nfev=2000)[0]
    else:
        return optimize.curve_fit(lorentzian, x_values, y_values, p0=starting_params)[0]
def lorentzian(x, constant_offset, amplitude, center, fwhm):
    return constant_offset + amplitude * np.square(0.5 * fwhm) / (np.square(x - center) + np.square(0.5 * fwhm))

# ========= Cose fit functions =============================
#===============================================================
def get_ampfreqphase_FFT(qx, dt, n0 = 0, f_range = None, return_Spectra = False):
    '''
    returns estimate of amplitdue, frequency and phase from FFT

    [ax, fx, phi] = get_ampfreqphase_FFT(qx, dt,n0 = 0, f_range=None, return_Spectra = False)
    [ax, fx, phi], [Fx, Ax] = get_ampfreqphase_FFT(qx, dt,n0 = 0, f_range=None, return_Spectra = True)
    input:
        qx: time trace  sampled at intervals dt
        dt: sampling interval

    input (optional):
        n0 = t0/dt: index of time zero
        f_range = [f_x, df]: frequency is looked in intervals f_x +-df respectively
        return_Spectra = True/False: returns spectra over range f_range in addition to [phi, ax, fx]

    output:
        dominant frequency, amplitude at that frequency and phase
        method: get fourier component of max signals
    '''

    n = len(qx)
    f = np.fft.fftfreq(n, dt)[0:int(n/2)]

    # look for max frequencies only in certain range
    if f_range is None:
        irange_x = np.arange(int(n/2))
    else:
        [f_x, df] = f_range
        imin = np.argwhere(f >= f_x-df)[0,0]
        imax = np.argwhere(f <= f_x+df)[-1,0] + 1
        irange_x = np.arange(imax-imin+1)+imin

    # convert to int (from float)
    irange_x = [int(x) for x in irange_x]

    # Fourier transforms (remove offset, in case there is a large DC)
    Ax = np.fft.fft(qx-np.mean(qx))[irange_x] / n*2
    Fx = f[irange_x]

    # frequency and amplitude x
    i_max_x = np.argmax(np.abs(Ax))
    fx = Fx[i_max_x]
    ax = np.abs(Ax[i_max_x])
    # phase
    phi = np.angle(Ax[i_max_x] * np.exp(-1j *2 * np.pi * fx * n0))

    if return_Spectra == True:
        return [ax, 2*np.pi*fx, phi], [Fx, Ax]
    else:
        return [ax, 2*np.pi*fx, phi]


def guess_cose_parameter(t, y):
    """
    guesses the parameters for a cosinus dataset
    Args:
        t: time vector, here we assume that t is sampled evenly
        y: data vector

    Returns: estimated fit parameters for Sine fit
    """
    dt = np.mean(np.diff(t))
    offset = float(max(y) + min(y)) / 2
    [ax, wx, phi] = get_ampfreqphase_FFT(y-offset, dt)

    return [ax, wx, phi, offset]


def cose(t, a0, w0, phi0, offset):
    """
        cosine function
    """
    return a0*np.cos(w0*t+phi0)+ offset

def fit_cose_parameter(t, y):
    """
    fits the data to a cosine
    Args:
        t:
        y:

    Returns:

    """

    # todo: implement working fit algorithm, for now just take the estimate
    [ax, wx, phi, offset] = guess_cose_parameter(t, y)

    return [ax, wx, phi, offset]