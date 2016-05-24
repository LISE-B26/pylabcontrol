import numpy as np
from PIL import Image as im

def find_image_shift(reference_image, shifted_image):
    """
    Takes two images and finds the necessary translation of the second image to match the first.

    Args:
        reference_image: numpy 2D array of pixel values
        new_image: numpy 2D array of pixel values

    Returns: ordered pair (x_shift, y_shift) of pixel values

    """

    # get pixel-to-voltage conversion for each image
    shifted_img_pix2vol = pixel_to_voltage_conversion(shifted_image)
    ref_img_pix2vol = pixel_to_voltage_conversion(reference_image)

    # subtract average from images for later correlation calculations
    shifted_subimage_zero_average = shifted_image - shifted_image.mean()
    shifted_subimage_zero_average = shifted_image - shifted_image.mean()

    # make images commensurate, i.e., match image pixel lengths by scaling shifted_image

    if shifted_img_pix2vol != ref_img_pix2vol:
        new_shifted_img_size = size = int(round(baseline_image_sub.shape[0]/(new_x_pixel_to_voltage/x_pixel_to_voltage)))


def pixel_to_voltage_conversion(image):
    image_x_len = image.shape[1]
    image_y_len = image.shape[0]
    image_x_min, image_x_max = np.min(image[:,0]), np.max(image[:,0])
    image_y_min, image_y_max = np.min(image[0, :]), np.max(image[0, :])
    x_pixel_to_voltage = (image_x_max - image_x_min) / image_x_len
    y_pixel_to_voltage = (image_y_max - image_y_min) / image_y_len
    return (x_pixel_to_voltage, y_pixel_to_voltage)
