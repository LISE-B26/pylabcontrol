__author__ = 'Experiment'

from scipy import signal
import numpy as np

def plot_region(plt, rio, color = 'r'):
    '''
        draw a box that marks the region of interest
    :param plt: plot in which to draw box
    :param rio:  region of interest
    :param color: color of box
    :return:
    '''
    plt.plot([rio['xo']-rio['dx']/2, rio['xo']-rio['dx']/2], [rio['yo']-rio['dy']/2, rio['yo']+rio['dy']/2], color)
    plt.plot([rio['xo']+rio['dx']/2, rio['xo']+rio['dx']/2], [rio['yo']-rio['dy']/2, rio['yo']+rio['dy']/2], color)
    plt.plot([rio['xo']-rio['dx']/2, rio['xo']+rio['dx']/2], [rio['yo']-rio['dy']/2, rio['yo']-rio['dy']/2], color)
    plt.plot([rio['xo']-rio['dx']/2, rio['xo']+rio['dx']/2], [rio['yo']+rio['dy']/2, rio['yo']+rio['dy']/2], color)



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

def rio_to_galvoparameter(rio):
    '''
    takes a dictionary with the region of interest and returns the parameter for galvo scan
    '''
    xVmin, xVmax = rio['xo'] - rio['dx']/2., rio['xo'] + rio['dx']/2.
    yVmin, yVmax = rio['yo'] - rio['dy']/2., rio['yo'] + rio['dy']/2.
    return xVmin, xVmax, rio['xPts'], yVmin, yVmax, rio['yPts']



def find_beam_position(img_old, img_new, rio):
    '''
        takes two images of equal size and returns the new rio (changes the center position)
        if the two images are identical the rio should be unchanged
    '''


    cor = signal.correlate2d (img_old, img_old, mode='same')
    initial_max_y, initial_max_x = np.unravel_index(np.argmax(cor),cor.shape)

    cor = signal.correlate2d (img_new, img_new, mode='same')
    max_y, max_x = np.unravel_index(np.argmax(cor),cor.shape)

    shift_x = initial_max_x - max_x
    shift_y = initial_max_y - max_y

    rio_new = rio.copy()

    rio_new['xo'] += 1.* shift_x  / rio['xPts'] * (rio['dx'])
    rio_new['yo'] += 1.* shift_y  / rio['yPts'] * (rio['dy'])

    return rio_new