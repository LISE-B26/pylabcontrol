from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
import numpy as np
import matplotlib.patches as patches


# from scipy import signal
# import numpy as np
# import scipy.optimize as opt
from scipy import ndimage
# import matplotlib.pyplot as plt
import skimage.feature as feature
# from skimage import data, img_as_float
# import pandas as pd
# from matplotlib.patches import Rectangle
# import scipy.spatial

# #Baseline Values chosen for Nikon 100x, NA=.9 objective, may need to be adjusted for other objectives
# MIN_SEPARATION = 5
# GAUSSIAN_SIGMA = 1
# REF_VOLTAGE_RANGE = .15
# REF_PIXEL_NUM = 120
# MIN_NV_CNTS = 15

from src.core.plotting import plot_fluorescence

class Find_Points(Script):
    _DEFAULT_SETTINGS = Parameter([
        Parameter('image_path', 'Z:/Lab/Cantilever/Measurements/__test_data_for_coding/', str, 'path for data'),
        Parameter('image_tag', 'some_name', str, 'some_name'),
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/__test_data_for_coding/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('fit_values',[
            Parameter('min_separation', 2.0, float, 'minimum seperation between adjacent points in um'),
            Parameter('point_size', 0.5, float, 'size of point in um'),
            Parameter('min_NV_counts', 0.015, float, 'the minimum of NV counts (in kCounts) to be considered a valid NV'),
            Parameter('image_size', 15.0, float, 'size of image in (um)')
        ])
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, instruments = None, name = None, settings = None,  log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, log_output = log_output)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        def locate_Points(image):
            """
            # Locates NVs in an image by smoothing with a gaussian filter and finding intensity maxima. Returns coordinates of
            # NVs in pixels
            # scales Gaussian filter size based on current pixel to voltage scaling
            Args:
                image: an intensity image

            Returns:  coordinates of NVs in pixels

            """

            numPts = len(image) # size of image in pixels
            scaling_pixel_um = self.settings['fit_values']['image_size'] / numPts # scaling factor to convert from pixel to um
            gaussian_sigma_px = int(self.settings['fit_values']['point_size'] / scaling_pixel_um) # size of point in pixel
            separation_px = int(self.settings['fit_values']['min_separation'] / scaling_pixel_um) # minimum seperation between adjacent points in pixel
            min_NV_counts  = self.settings['fit_values']['min_NV_counts']

            print('scaling_pixel_um',scaling_pixel_um)
            print('gaussian_sigma_px', gaussian_sigma_px)
            print('separation_px', separation_px)


            # convolves image with a gaussian filter to smooth peaks and prevent many local maxima
            image_gaussian = ndimage.gaussian_filter(image, gaussian_sigma_px, mode='reflect')
            # image_gaussian = ndimage.gaussian_filter(image, gaussian_sigma_px)

            # finds local maxima in smoothed images, corresponding to center of NVs
            coordinates = feature.peak_local_max(image_gaussian, min_distance=separation_px, exclude_border=False,
                                                 threshold_rel=0, threshold_abs = min_NV_counts)

            return np.array(coordinates, dtype=float), image_gaussian
        # load image
        image_data=Script.load_data(self.settings['image_path'], data_name_in='image_data')
        bounds = Script.load_data(self.settings['image_path'], data_name_in='bounds')
        self.log('loaded image {:s}'.format(self.settings['image_path']))
        self.x_min = bounds[0][0]
        self.x_max = bounds[1][0]
        self.y_min = bounds[2][0]
        self.y_max = bounds[3][0]
        x_len = image_data.shape[1]
        y_len = image_data.shape[0]
        x_pixel_to_voltage= (self.x_max-self.x_min)/x_len
        y_pixel_to_voltage= (self.y_max-self.y_min)/y_len

        coordinates, image_gaussian = locate_Points(image_data)
        # peak_local_max flips x and y for each point, need to flip it back
        coordinates = zip(*np.flipud(zip(*coordinates)))
        for index, pt in enumerate(coordinates):
            xcoor = pt[0]*x_pixel_to_voltage + self.x_min
            ycoor = pt[1] * y_pixel_to_voltage + self.y_min
            coordinates[index] = [xcoor, ycoor]

        self.data = {'NV_positions':coordinates, 'image':image_data, 'image_gaussian':image_gaussian}

        #self.save_data()

    def plot(self, axes):
        image  = self.data['image']
        extend = [self.x_min, self.x_max, self.y_max, self.y_min]
        plot_fluorescence(image, extend, axes)

        for x in self.data['NV_positions']:
            patch = patches.Circle((x[0],x[1]), .0005, fc = 'r')
            axes.add_patch(patch)



if __name__ == '__main__':
    script, failed, instr = Script.load_and_append({'Find_Points': 'Find_Points'})

    print(script)
    print(failed)
    print(instr)
    # fp = Find_Points(settings={'path': 'Z:/Lab/Cantilever/Measurements/__tmp__', 'tag':'nvs'})
    # fp.run()

    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # plt.pcolor(fp.data['image'])
    # print(fp.data['image_gaussian'].shape)
    # plt.pcolor(fp.data['image'])
    # plt.imshow(fp.data['image'], cmap = 'pink', interpolation = 'nearest')
    #
    #
    # for x in fp.data['NV_positions']:
    #     plt.plot(x[0],x[1],'ro')
    #
    # plt.show()

    # plt.figure()
    # plt.imshow(fp.data['image_gaussian'])
    # Axes3D.plot(fp.data['image_gaussian'])
    # plt.show()
    # print(max(fp.data['image']))
    # print(max(fp.data['image_gaussian'].flatten()))
    # print('NV_positions', fp.data['NV_positions'])

