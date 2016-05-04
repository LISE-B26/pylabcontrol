from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread

import numpy as np





# from scipy import signal
# import numpy as np
# import scipy.optimize as opt
# from scipy import ndimage
# import matplotlib.pyplot as plt
# import skimage.feature
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

# def locate_NVs(image, voltage_range, numPts):
#     """
#     # Locates NVs in an image by smoothing with a gaussian filter and finding intensity maxima. Returns coordinates of
#     # NVs in pixels
#     :param image: an intensity image
#     :param voltage_range: size of image in volts so filter can be scaled
#     :return: coordinates of NVs in pixels
#     """
#     # scales Gaussian filter size based on current pixel to voltage scaling
#     scaling = (REF_VOLTAGE_RANGE/voltage_range)*(numPts/REF_PIXEL_NUM)
#     print('scaling:' + str(scaling))
#
#     # convolves image with a gaussian filter to smooth peaks and prevent many local maxima
#     image_gaussian = ndimage.gaussian_filter(image, GAUSSIAN_SIGMA*scaling, mode='reflect')
#
#     #finds local maxima in smoothed images, corresponding to center of NVs
#     coordinates = skimage.feature.peak_local_max(image_gaussian, MIN_SEPARATION*scaling, exclude_border=False, threshold_rel=0, threshold_abs=MIN_NV_CNTS)
#     return np.array(coordinates,dtype=float)
#
#
#



class Find_Points(Script):

    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(int)
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

        def calc_progress():
            pass

        # self.save(save_data=True, save_instrumets=False, save_log=False, save_settings=False)

        # progress = calc_progress()
        #
        # self.updateProgress.emit(progress)
        #
        # self.updateProgress.emit(100)
        x =  []
        y = []
        import random
        for i in range(10):
            x.append(random.random())
            y.append(random.random())

        self.data = {'x':x, 'y':y}
        self.save_data()

        print(self.settings)

    def plot(self, axes):
        for (x, y) in self.data['points']:
            print(x, y)
            axes.plot(x,y,'x')

        axes.set_xlim([-1,1])
        axes.set_ylim([-1, 1])



class Select_Points(Script):

    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(int)
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

        def calc_progress():
            pass

        # self.save(save_data=True, save_instrumets=False, save_log=False, save_settings=False)

        # progress = calc_progress()
        #
        # self.updateProgress.emit(progress)
        #
        # self.updateProgress.emit(100)
        x =  []
        y = []
        import random
        for i in range(10):
            x.append(random.random())
            y.append(random.random())

        self.data = {'x':x, 'y':y}
        self.save_data()

        print(self.settings)

    def plot(self, axes):
        for (x, y) in self.data['points']:
            print(x, y)
            axes.plot(x,y,'x')

        axes.set_xlim([-1,1])
        axes.set_ylim([-1, 1])

if __name__ == '__main__':
    fp = Find_Points(settings={'path': 'Z:/Lab/Cantilever/Measurements/__tmp__', 'tag':'nvs'})
    fp.run()

    print(fp.data)
