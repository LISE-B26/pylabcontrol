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
def A_fun(qx, w, dt):
    '''
    Ak = A_fun(qx, w, fs)
    input:
        xx: input signal vector length N
        w: omega, w = 2*pi*k*fs / M  vector length K
        dt: sampling interval
    output:
        Ak: spectrum at frequencies w
    '''

    N = len(qx)
    j = 1j

    nn = np.array( [ np.arange(N) ] ).transpose()

    Ak = (1./N) * np.dot(np.array([qx]),  np.exp(-j * np.dot( nn, np.array([w]) ) * dt) )

    return Ak[0]

def guess_cose_parameter(t, y):
    """
    guesses the parameters for a cosinus dataset
    Args:
        t: time vector, here we assume that t is sampled evenly
        y: data vector

    Returns: estimated fit parameters for Sine with offset fit
    """
    dt = np.mean(np.diff(t))
    offset = float(max(y) + min(y)) / 2
    [ax, wx, phi] = get_ampfreqphase_FFT(y-offset, dt)

    # if the oscillation is less than a peroiod we take the average of the min and max as the offset otherwise we take the mean


    if max(t)<2*np.pi/wx:
        offset = float(max(y) + min(y)) / 2
    else:
        offset = np.mean(y)

    return [ax, wx, phi, offset]


def cose(t, a0, w0, phi0, offset):
    """
        cosine function
    """
    return a0*np.cos(w0*t+phi0)+ offset

def fit_cose_parameter(t, y, verbose = False):
    """
    fits the data to a cosine
    Args:
        t:
        y:

    Returns:

    """

    [ax, wx, phi, offset] = guess_cose_parameter(t, y)
    if verbose:
        print('initial estimates [ax, wx, phi, offset]:', [ax, wx, phi, offset])
    def cost_function_fit(x):
        """
        cost function for fit to sin
        """
        ao, wo, po, offset = x
        #         sig = sine(x, t)
        sig = ao * np.cos(wo * t + po) + offset
        return np.sum((sig - y)**2)

    opt = optimize.minimize(cost_function_fit, [ax, wx, phi, offset])
    if verbose:
        print('optimization result:', opt)
    [ax, wx, phi, offset] = opt.x

    return [ax, wx, phi, offset]

def cose_with_decay(t, a0, w0, phi0, offset, tau):
    """
        cosine function
    """
    return a0*np.exp(-t/tau)*np.cos(w0*t+phi0)+ offset


def get_decay_data(t, y, wo, verbose=False):
    """
        average the data y over a oscillation period to smoothout oscillations
    returns: averaged data

    """

    period = 2 * np.pi / wo
    dt = np.mean(np.diff(t))
    index_per_interval = int(period / dt)

    number_of_oscillations = int(np.floor(len(y) / index_per_interval))

    if verbose:
        print(
        'initial estimates [index_per_interval, number_of_oscillations]:', [index_per_interval, number_of_oscillations])

    decay_y = np.array(
        [np.std(y[index_per_interval * i:index_per_interval * (i + 1)]) for i in range(number_of_oscillations)])
    decay_t = np.array(
        [np.mean(t[index_per_interval * i:index_per_interval * (i + 1)]) for i in range(number_of_oscillations)])
    return np.array(decay_t), np.array(decay_y)

def fit_exp_decay(t, y, offset = False, verbose=False):
    """
    fits the data to a decaying exponential, with or without an offset
    Args:
        t: x data
        y: y data
        offset: False if fit should decay to y=0, True otherwise
        verbose: prints results to screen

    Returns: fit parameters, either [ao, tau, offset] if offset is True, or or [ao, tau] if offset is False
            ao: amplitude above offset (or zero if offset is False)
            tau: decay parameter
            offset: asymptotic value as t->INF

    """
    if verbose:
        print(' ======= fitting exponential decay =======')

    init_params = estimate_exp_decay_parameters(t, y, offset)
    if offset:
        [ao, tau, offset] = optimize.curve_fit(exp_offset, t, y, p0=init_params)[0]
    else:
        [ao, tau] = optimize.curve_fit(exp, t, y, p0=init_params)[0]

    if offset:
        if verbose:
            print('optimization result:', [ao, tau, offset])
        return [ao, tau, offset]
    else:
        if verbose:
            print('optimization result:', [ao, tau])
        return [ao, tau]

def estimate_exp_decay_parameters(t,y,offset):
    '''
    Returns an initial estimate for exponential decay parameters. Meant to be used with optimize.curve_fit.
    Args:
        t: x data
        y: y data
        offset: False if fit should decay to y=0, True otherwise

    Returns: fit parameter estimate, either [ao, tau, offset] if offset is True, or or [ao, tau] if offset is False
            ao: amplitude above offset (or zero if offset is False)
            tau: decay parameter
            offset: asymptotic value as t->INF

    '''
    if offset:
        offset = y[-1]
    else:
        offset = 0
    total_amp = y[0]
    ao = total_amp-offset
    decay = t[np.argmin(np.abs(y - (total_amp+offset)/2))] #finds time at which the value is closest to midway between the max and min
    if offset:
        return [ao, decay, offset]
    else:
        return [ao, decay]

def exp(t, ao, tau):
    '''
    Exponential decay: ao*E^(t/tau)
    '''
    return np.exp(-t / tau) * ao

def exp_offset(t, ao, tau, offset):
    '''
    Exponential decay with offset: ao*E^(t/tau) + offset
    '''
    return np.exp(-t / tau) * ao + offset


def fit_rabi_decay(t, y, varibale_phase=False, verbose=False):
    """
    fit to a cosine with an exponential envelope
    Args:
        t: time in ns
        y: counts in kilocounts
        varibale_phase: if true the phase is a free parameter if false the phase is 0 (cosine)

    """

    [ax, wx, phi, offset] = guess_cose_parameter(t, y)

    # estimate the decay constant
    t_decay, y_decay = get_decay_data(t, y, wx, verbose)
    [_, to] = fit_exp_decay(t_decay, y_decay)

    if varibale_phase:
        initial_parameter = [ax, wx, phi, offset, to]
    else:
        initial_parameter = [ax, wx, offset, to]

    if verbose:
        if varibale_phase:
            print('initial estimates [ax, wx, phi, offset, tau]:', initial_parameter)
        else:
            print('initial estimates [ax, wx, offset, tau]:', initial_parameter)

    def cost_function_fit(x):
        """
        cost function for fit to exponentially decaying cosine
        """
        if varibale_phase:
            ao, wo, po, offset, to = x
            sig = ao * np.exp(-t / to) * np.cos(wo * t + po) + offset
        else:
            ao, wo, offset, to = x
            sig = ao * np.exp(-t / to) * np.cos(wo * t) + offset
        return np.sum((sig - y) ** 2)

    opt = optimize.minimize(cost_function_fit, initial_parameter)
    #     opt = optimize.minimize(cost_function_fit, [ax, wx, phi, offset, to],
    #                             bounds=[(None, None), (1.1*wx, 2*wx), (None, None), (None, None), (None, None)])

    #
    # [ax, wx, phi, offset, tau] = opt.x

    if verbose:
        print('optimization result:', opt)

    return opt.x
