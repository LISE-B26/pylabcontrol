import numpy as np
from PIL import Image as im
from scipy import signal
import trackpy as tp
from skimage.filters import sobel

def find_image_shift(reference_image, reference_image_extent, shifted_image, shifted_image_extent, correlation_padding = False):
    """
    Takes two images and finds the necessary translation of the second image to match the first.

    Args:
        reference_image: numpy 2D array of pixel values
        reference_image_bounds: numpy array with 4 elements containing the voltage bounds of the reference image
        shifted_image: numpy 2D array of pixel values
        shifted_image_bounds: numpy array with 4 elements containing the voltage bounds of the shifted image
        correlation_padding: Allows the correlation to overlap images beyond their respective edges, filling
                                outside pixels with value 0.

    Returns: ordered pair (x_shift, y_shift) of pixel values

    """

    # get pixel-to-voltage conversion for each image
    # print('shifted_image', shifted_image)
    shifted_img_pix2vol = pixel_to_voltage_conversion_factor(shifted_image.shape, shifted_image_extent)
    ref_img_pix2vol = pixel_to_voltage_conversion_factor(reference_image.shape, reference_image_extent)

    # subtract average from images for later correlation calculations
    shifted_image = shifted_image - shifted_image.mean()
    reference_image = reference_image - reference_image.mean()

    # make images commensurate, i.e., match image pixel lengths by scaling shifted_image
    if shifted_img_pix2vol != ref_img_pix2vol:

        # find new size for shifted img
        scaled_shifted_img_x_size = int(round(shifted_image.shape[0] * (shifted_img_pix2vol[0]/ref_img_pix2vol[0])))
        scaled_shifted_img_y_size = int(round(shifted_image.shape[1] * (shifted_img_pix2vol[1]/ref_img_pix2vol[1] )))
        scaled_shifted_img_size = (scaled_shifted_img_x_size, scaled_shifted_img_y_size)

        # use PIL package to do resizing
        scaled_shifted_image_PIL = im.fromarray(shifted_image).resize(scaled_shifted_img_size)
        scaled_shifted_image_pixels = list(scaled_shifted_image_PIL.getdata())
        scaled_width, scaled_height = scaled_shifted_image_PIL.size
        shifted_image = np.array([scaled_shifted_image_pixels[i * scaled_width:(i + 1) * scaled_width] for i in xrange(scaled_height)])

    # get correlation function, find max, return it

    if correlation_padding:
        correlation_image = signal.correlate2d(reference_image, shifted_image, mode='full')
    else:
        correlation_image = signal.correlate2d(reference_image, shifted_image, mode='valid')

    dy_pixel, dx_pixel = np.unravel_index(np.argmax(correlation_image), correlation_image.shape) - np.array(correlation_image.shape)/2

    dx_voltage = -1.0 * ref_img_pix2vol[0] * dx_pixel - (np.mean(reference_image_extent[0:2]) - np.mean(shifted_image_extent[0:2]))
    dy_voltage = -1.0 * ref_img_pix2vol[1] * dy_pixel - (np.mean(reference_image_extent[2:4]) - np.mean(shifted_image_extent[2:4]))
    return dx_voltage, dy_voltage, correlation_image

def pixel_to_voltage_conversion_factor(image_shape, image_extent):
    # COMMENT_ME
    image_x_len, image_y_len = image_shape
    image_x_min, image_x_max, image_y_max, image_y_min = image_extent
    x_voltage = (image_x_max - image_x_min) / image_x_len
    y_voltage = (image_y_max - image_y_min) / image_y_len
    return x_voltage, y_voltage

def _create_nv_image(image, nv_size, created_pt_size = 3):
    # COMMENT_ME
    y_len, x_len = image.shape
    f = tp.locate(image, nv_size)

    new_image = np.zeros((y_len, x_len))
    nv_locs = f.values
    for pt in nv_locs:
        for i in range(-created_pt_size, created_pt_size+1):
            for j in range(-created_pt_size, created_pt_size+1):
                if pt[1] + j < y_len and pt[1] - j >= 0 and pt[0] + i < x_len and pt[0] - i >= 0:
                    new_image[pt[1] + j, pt[0] + i] = 10
    return new_image

def _create_edge_image(image):
    '''
    Creates an image identifying the edges in the input image using Sobel's algorithm. This convolves the original image
    with the kernels Gx = {{1,2,1},{0,0,0},{-1,-2,-1}} and Gy = {{-1,0,1},{-2,0,2},{-1,0,1}} to create an image that is
    the discrete gradient of the original. It responds strongest to vertical or horizonal features.
    This was originally necessary to track resonators in reflection images, as the significant changes in brightness
    as we pushed the resonators (massively changed background, magnet coming into and out of focus and thus going from
    bright to dark) made a naive correlation fail. Looking instead for the edges, and thus basically creating a
    brightness-independent resonator image, allowed correlation to succeed.
    Args:
        image: image to find edges of
    '''
    return sobel(image)

def correlation(baseline_image, baseline_image_extent, new_image, new_image_extent, use_trackpy = False, use_edge_detection = False, nv_size = 11):
    '''

    Args:
        baseline_image: original image before shifting
        baseline_image_extent: extent of that image
        new_image: final image after shifting
        new_image_extent: extent of that image
        use_trackpy: if true, creates a 'dummy image' of just NVs (a pixel block where trackpy find each NV)
            which filters out the background and allows determination of NV shift even if the structure on which the
            diamond rests is moving
        use_edge_detection: if true, creates a 'dummy image' that identifies the edges of the image. Used to filter out
            backgrounds that drastically change in brightness, or highlight features that change in brightness but keep
            the same shape
        nv_size: only used if use_trackpy is selected, gives the expected NV size in

    Returns: the x and y shifts in voltage, and the correlation image

    '''
    if use_edge_detection:
        baseline_image = _create_edge_image(baseline_image)
        new_image = _create_edge_image(new_image)

    if use_trackpy:
        baseline_image = _create_nv_image(baseline_image, nv_size)
        new_image = _create_nv_image(new_image, nv_size)

    dx_voltage, dy_voltage, correlation_image = find_image_shift(baseline_image, baseline_image_extent, new_image, new_image_extent, correlation_padding=True)

    return dx_voltage, dy_voltage, correlation_image

def shift_NVs(dx_voltage, dy_voltage, nv_pos_list):
    '''
    Takes voltage shifts as found from the correlation function
    Args:
        dx_voltage:
        dy_voltage:
        nv_pos_list:

    Returns:

    '''
    return [[pos[0]+dx_voltage, pos[1]+dy_voltage] for pos in nv_pos_list]


'''
data3 = Script.load_data(path = 'Z:\\Lab\\Cantilever\\Measurements\\__test_data_for_coding\\160524-18_52_29_magn_on_center_beam\\')
data4 = Script.load_data(path = 'Z:\\Lab\\Cantilever\\Measurements\\__test_data_for_coding\\160524-18_50_46_magn_on_center_beam\\')


ref_image_bounds = np.array(data3['bounds']).flatten()
shifted_image_bounds = np.array(data4['bounds']).flatten()

ref_image = data3['image_data']
shifted_image = data4['image_data']

print find_image_shift(np.array(ref_image), ref_image_bounds, np.array(shifted_image), shifted_image_bounds)

'''

# data5 = Script.load_data(path = 'Z:\\Lab\\Cantilever\\Measurements\\__test_data_for_coding\\160525-12_05_06_center_beam_on_magnet\\')
# ref_image_bounds = np.array(data5['extent']).flatten()
# shifted_image_bounds = np.array(data5['extent']).flatten()
#
# ref_image = np.array(data5['image_data'])
# shifted_image = np.array(data5['image_data_2'])
#
# print find_image_shift(np.array(ref_image), ref_image_bounds, np.array(shifted_image), shifted_image_bounds, correlation_padding = True)
#
#
# plt.imshow(ref_image - shifted_image)
# plt.show()
#

