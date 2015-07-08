from scipy import signal
import numpy as np
import scipy.optimize as opt
from scipy import ndimage
import matplotlib.pyplot as plt
import skimage.feature
from skimage import data, img_as_float
import pandas as pd
from matplotlib.patches import Rectangle

#Baseline Values chosen for Nikon 100x, NA=.9 objective, may need to be adjusted for other objectives
MIN_SEPARATION = 5
GAUSSIAN_SIGMA = 1
REF_VOLTAGE_RANGE = .15

def locate_NVs(image, voltage_range):
    """
    # Locates NVs in an image by smoothing with a gaussian filter and finding intensity maxima. Returns coordinates of
    # NVs in pixels
    :param image: an intensity image
    :param voltage_range: size of image in volts so filter can be scaled
    :return: coordinates of NVs in pixels
    """
    # scales Gaussian filter size based on current pixel to voltage scaling
    scaling = REF_VOLTAGE_RANGE/voltage_range

    # convolves image with a gaussian filter to smooth peaks and prevent many local maxima
    image_gaussian = ndimage.gaussian_filter(image, GAUSSIAN_SIGMA*scaling, mode='reflect')

    #finds local maxima in smoothed images, corresponding to center of NVs
    coordinates = skimage.feature.peak_local_max(image_gaussian, MIN_SEPARATION*scaling, exclude_border=False)
    return np.array(coordinates,dtype=float)


def corr_NVs(baseline_image, new_image):
    """
    # Tracks drift by correlating new and old images, and returns shift in pixels
    :param baseline_image: original image
    :param new_image: new (drifted) image. Should be same size as baseline_image in pixels
    :return: shift from baseline image to new image in pixels
    """
    # subtracts mean to sharpen each image and sharpen correlation
    baseline_image -= baseline_image.mean()
    new_image -= new_image.mean()

    #takes center part of baseline image
    x_len = len(baseline_image[0])
    y_len = len(baseline_image)
    old_image = baseline_image[(x_len/4):(x_len*3/4),(y_len/4):(y_len*3/4)]

    # correlate with new image. mode='valid' ignores all correlation points where an image is out of bounds. if baseline
    # and new image are NxN, returns a (N/2)x(N/2) correlation
    corr = signal.correlate2d (new_image, old_image, boundary='fill', mode='valid')
    y, x = np.unravel_index(np.argmax(corr), corr.shape) # find the match

    # finds shift by subtracting center of initial coordinates, x_shift = x + (x_len/4) - (x_len/2)
    x_shift = x - (x_len/4)
    y_shift = y - (y_len/4)

    return (x_shift, y_shift) #, corr, old_image --- test outputs


def update_roi(roi, (x_shift, y_shift)):
    """
    Updates region of interest dict to account for drift
    :param roi: input region of interest
    :param shift: tuple of x and y shift of images in pixels
    :return: updated (shifted) region of interest
    """
    # convert shift from pixels to volts
    x_shift_v = x_shift * roi['dx'] / roi['xPts']
    y_shift_v = y_shift * roi['dy'] / roi['yPts']

    roi['xo'] += x_shift_v
    roi['yo'] += y_shift_v

    return roi

def shift_points(points, (x_shift, y_shift)):
    """
    Shifts a point or array of points by the input shift values, all in pixels
    :param points: input point or array of points
    :param shift: tuple of x and y shift of images in pixels
    :return: shifted point(s) in pixels
    """
    points[:,0] += x_shift
    points[:,1] += y_shift
    return points

def shift_points_v(points, roi, (x_shift, y_shift)):
    """
    Shifts a point or array of points by the input shift values, with the point input and output in volts
    :param points: input point or array of points in volts
    :param shift: tuple of x and y shift of images in pixels
    :return: shifted point(s) in volts
    """
    x_shift_v = x_shift * roi['dx'] / roi['xPts']
    y_shift_v = y_shift * roi['dy'] / roi['yPts']

    points[:,0] += x_shift_v
    points[:,1] += y_shift_v
    return points


def pixel_to_voltage(points, image, roi):
    # convert shift from pixels to volts
    points[:,0] = (points[:,0] - len(image[0])/2) * roi['dx'] / roi['xPts'] + roi['xo']
    points[:,1] = (points[:,1] - len(image)/2) * roi['dy'] / roi['yPts'] + roi['yo']
    return points

def locate_shifted_NVs(image, coordinates, (x_shift, y_shift), new_roi):
    x_shift_v = x_shift * new_roi['dx'] / new_roi['xPts']
    y_shift_v = y_shift * new_roi['dy'] / new_roi['yPts']

    coordinates[:,0] += x_shift_v
    coordinates[:,1] += y_shift_v

    new_NVs = locate_NVs(image, new_roi['dx'])


#image = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-29_18-43-58-NVBaselineTests.csv")
#image = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-27_16-53-09-NVBaseline.csv")
#image = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-29_18-51-59-NVBaselineTests.csv")
#image2 = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-29_19-11-24-NVBaselineTests.csv")
#image = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-29_17-33-14-NVBaselineTests.csv")
#image2 = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-29_17-41-10-NVBaselineTests.csv")


#image_np = image.as_matrix()
#image2_np = image2.as_matrix()

#image_np -= image_np.mean()
#image2_np -= image2_np.mean()

#(x_shift,y_shift), corr, orig = corr_NVs(image_np, image2_np)
#print(x_shift)
#print(y_shift)

#fig, ax = plt.subplots(1, 4, figsize=(8, 4))
#ax1, ax2, ax3, ax4 = ax.ravel()
#ax1.imshow(orig, cmap=plt.cm.gray)
#coor = locate_NVs(orig, .05)
#ax1.autoscale(False)
#ax1.plot(coor[:, 1], coor[:, 0], 'r.')
#ax2.imshow(corr, cmap=plt.cm.gray)
#ax3.imshow(image2_np,cmap = plt.cm.gray)
#ax3.add_patch(Rectangle((30+x_shift, 30+y_shift), 60, 60, edgecolor="red", fill = False))
#ax4.imshow(image2_np[(30+y_shift):(y_shift+90),(x_shift+30):(x_shift+90)], cmap=plt.cm.gray)
#coor2 = locate_NVs(image2_np[(30+y_shift):(y_shift+90),(x_shift+30):(x_shift+90)], .05)
#ax4.autoscale(False)
#ax4.plot(coor2[:, 1], coor2[:, 0], 'r.')

#print(coor)
#shifted_coor = shift_points(coor, (x_shift, y_shift))
#print(shifted_coor)

#plt.show()