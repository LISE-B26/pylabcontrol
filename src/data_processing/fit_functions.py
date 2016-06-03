import numpy as np
from scipy import optimize

def fit_gaussian(x_values, y_values, starting_params=None, bounds=None):
    """

    Args:
        x_values: domain of fit function
        y_values: y-values to fit
        starting_params: reasonable guesses for where to start the fitting optimization of the parameters. This is a
        length 4 list of the form [constant_offset, amplitude, center, width].
        bounds: Optionally, include bounds for the parameters in the gaussian fitting, in the following form:
                [(offset_lb, amplitude_lb, center_lb, width_lb), (offset_ub, amplitude_ub, center_ub, width_ub)]

    Returns:
        a length-4 list of [fit_parameters] in the form [constant_offset, amplitude, center, width]

    """

    if bounds:
        return optimize.curve_fit(gaussian, x_values, y_values, p0=starting_params, bounds=bounds, max_nfev=2000)[0]
    else:
        return optimize.curve_fit(gaussian, x_values, y_values, p0=starting_params)[0]


def gaussian(x, constant_offset, amplitude, center, width):
    return constant_offset + amplitude * np.exp(-1.0 * (np.square((x - center)) / (2 * (width ** 2))))


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


