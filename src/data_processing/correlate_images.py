import numpy as np
from PIL import Image as im
from scipy import signal
from src.core import Script
import matplotlib.pyplot as plt

def find_image_shift(reference_image, reference_image_bounds, shifted_image, shifted_image_bounds, correlation_padding = False):
    """
    Takes two images and finds the necessary translation of the second image to match the first.

    Args:
        reference_image: numpy 2D array of pixel values
        new_image: numpy 2D array of pixel values

    Returns: ordered pair (x_shift, y_shift) of pixel values

    """

    # get pixel-to-voltage conversion for each image
    shifted_img_pix2vol = pixel_to_voltage_conversion_factor(shifted_image.shape, shifted_image_bounds)
    ref_img_pix2vol = pixel_to_voltage_conversion_factor(reference_image.shape, reference_image_bounds)

    # subtract average from images for later correlation calculations
    shifted_image = shifted_image - shifted_image.mean()
    reference_image = reference_image - reference_image.mean()

    # make images commensurate, i.e., match image pixel lengths by scaling shifted_image
    if shifted_img_pix2vol != ref_img_pix2vol:

        # find new size for shifted img
        scaled_shifted_img_x_size = int(round(shifted_image.shape[0] * (shifted_img_pix2vol[0]/ref_img_pix2vol[0])))
        scaled_shifted_img_y_size = int(round(shifted_image.shape[1] * (shifted_img_pix2vol[1]/ref_img_pix2vol[1] )))
        print scaled_shifted_img_x_size
        print scaled_shifted_img_y_size
        scaled_shifted_img_size = (scaled_shifted_img_x_size, scaled_shifted_img_y_size)

        # use PIL package to do resizing
        scaled_shifted_image_PIL = im.fromarray(shifted_image).resize(scaled_shifted_img_size)
        scaled_shifted_image_pixels = list(scaled_shifted_image_PIL.getdata())
        scaled_width, scaled_height = scaled_shifted_image_PIL.size
        shifted_image = np.array([scaled_shifted_image_pixels[i * scaled_width:(i + 1) * scaled_width] for i in xrange(scaled_height)])

    # get correlation function, find max, return it

    if correlation_padding:
        correlation = signal.correlate2d(reference_image, shifted_image, mode='full')
    else:
        correlation = signal.correlate2d(reference_image, shifted_image, mode='valid')

    dy_pixel, dx_pixel = np.unravel_index(np.argmax(correlation), correlation.shape) - np.array(correlation.shape)/2

    dx_voltage = -1.0 * ref_img_pix2vol[0] * dx_pixel - (np.mean(reference_image_bounds[0:2]) - np.mean(shifted_image_bounds[0:2]))
    dy_voltage = -1.0 * ref_img_pix2vol[1] * dy_pixel - (np.mean(reference_image_bounds[2:4]) - np.mean(shifted_image_bounds[2:4]))
    return dx_voltage, dy_voltage

def pixel_to_voltage_conversion_factor(image_shape, image_bounds):
    image_x_len, image_y_len = image_shape
    image_x_min, image_x_max, image_y_min, image_y_max = image_bounds
    x_voltage = (image_x_max - image_x_min) / image_x_len
    y_voltage = (image_y_max - image_y_min) / image_y_len
    return x_voltage, y_voltage


data3 = Script.load_data(path = 'Z:\\Lab\\Cantilever\\Measurements\\__test_data_for_coding\\160524-18_52_29_magn_on_center_beam\\')
data4 = Script.load_data(path = 'Z:\\Lab\\Cantilever\\Measurements\\__test_data_for_coding\\160524-18_50_46_magn_on_center_beam\\')


ref_image_bounds = np.array(data4['bounds']).flatten()
shifted_image_bounds = np.array(data4['bounds']).flatten()

ref_image = data4['image_data']
shifted_image = data4['image_data']

print find_image_shift(np.array(ref_image), ref_image_bounds, np.array(shifted_image), shifted_image_bounds)
