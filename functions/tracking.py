__author__ = 'Experiment'

from scipy import signal
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
import sys

def plot_region(plt, roi, color = 'r'):
    '''
        draw a box that marks the region of interest
    :param plt: plot in which to draw box
    :param roi:  region of interest
    :param color: color of box
    :return:
    '''
    plt.plot([roi['xo']-roi['dx']/2, roi['xo']-roi['dx']/2], [roi['yo']-roi['dy']/2, roi['yo']+roi['dy']/2], color)
    plt.plot([roi['xo']+roi['dx']/2, roi['xo']+roi['dx']/2], [roi['yo']-roi['dy']/2, roi['yo']+roi['dy']/2], color)
    plt.plot([roi['xo']-roi['dx']/2, roi['xo']+roi['dx']/2], [roi['yo']-roi['dy']/2, roi['yo']-roi['dy']/2], color)
    plt.plot([roi['xo']-roi['dx']/2, roi['xo']+roi['dx']/2], [roi['yo']+roi['dy']/2, roi['yo']+roi['dy']/2], color)



# class RIO:
#     '''
#     class which contains the region of interest speciified by
#      center point x,y and dimensions dx, dy
#     '''
#     def __init__(self, x, y, dx, dy):
#         self.x = x
#         self.y = y
#         self.dx = dx
#         self.dy = dy
#
#     def __repr__(self):
#         return 'x: {:0.2f}, y: {:0.2f}, dx: {:0.2f}, dy: {:0.2f}'.format(self.x, self.y, self.dx, self.dy)

def roi_to_galvoparameter(roi):
    '''
    takes a dictionary with the region of interest and returns the parameter for galvo scan
    '''
    xVmin, xVmax = roi['xo'] - roi['dx']/2., roi['xo'] + roi['dx']/2.
    yVmin, yVmax = roi['yo'] - roi['dy']/2., roi['yo'] + roi['dy']/2.
    return xVmin, xVmax, roi['xPts'], yVmin, yVmax, roi['yPts']



def find_beam_position(img_old, img_new, roi):
    '''
        takes two images of equal size and returns the new roi (changes the center position)
        if the two images are identical the roi should be unchanged
    '''
    
    cor = signal.correlate2d (img_new, img_old, mode='same')
    max_y, max_x = np.unravel_index(np.argmax(cor),cor.shape)


    def twoD_Gaussian((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
        xo = float(xo)
        yo = float(yo)
        a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
        b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
        c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
        g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo)
                                + c*((y-yo)**2)))
        return g.ravel()
    
    x = np.linspace(roi['xo'] - roi['dx'], roi['xo'] + roi['dx'], roi['xPts'])
    y = np.linspace(roi['yo'] - roi['dy'], roi['yo'] + roi['dy'], roi['yPts'])
    x, y = np.meshgrid(x, y)

    initial_guess = (np.max(cor), x[0,max_x], y[max_y,0], roi['dx']/2, roi['dy']/2,0,0)
    
    popt, pcov = opt.curve_fit(twoD_Gaussian, (x, y), cor.flatten(), p0=initial_guess)

    roi_new = roi.copy()

    x_shift = popt[1] - roi['xo']
    y_shift = popt[2] - roi['yo']

    roi_new.update({
        'xo': roi['xo']- x_shift/2.,
        'yo': roi['yo']- y_shift/2.
    })

    # roi_new['xo'] += 1.* shift_x  / roi['xPts'] * (roi['dx'])
    # roi_new['yo'] += 1.* shift_y  / roi['yPts'] * (roi['dy'])

    return roi_new


def get_frequency_interval(freqStart, interval_sampleNum, freq_df, n_block):
    '''
    calculates the frequency interval in block n

    '''
    interval_freqStart =  freqStart + n_block * interval_sampleNum * freq_df
    interval_freqEnd  =  freqStart + ((n_block+1) * interval_sampleNum-1) * freq_df
    return interval_freqStart, interval_freqEnd