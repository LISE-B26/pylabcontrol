from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
import numpy as np
import matplotlib.patches as patches
from src.scripts.galvo_scan import GalvoScan
from scipy import signal

class Correlate_Images(Script):
    _DEFAULT_SETTINGS = Parameter([
        Parameter('baseline_image_path', '', str, 'path for data'),
        Parameter('baseline_image_tag', '', str, 'some_name'),
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/__test_data_for_coding/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {'GalvoScan': GalvoScan}

    def __init__(self, instruments = None, name = None, settings = None, scripts = None, log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_output = log_output)
        self.data = {'x_shift': None, 'y_shift': None}

    def _function(self):
        """
        # Tracks drift by correlating new and old images, and returns shift in pixels
        """
        # subtracts mean to sharpen each image and sharpen correlation
        baseline_image = Script.load_data(self.settings['baseline_image_path'], data_name_in='image_data')
        bounds = Script.load_data(self.settings['baseline_image_path'], data_name_in='bounds')
        baseline_image_sub = baseline_image - baseline_image.mean()

        x_min = bounds[0][0]
        x_max = bounds[1][0]
        y_min = bounds[2][0]
        y_max = bounds[3][0]
        x_len = baseline_image.shape[1]
        y_len = baseline_image.shape[0]
        x_pixel_to_voltage= (self.x_max-self.x_min)/x_len
        y_pixel_to_voltage= (self.y_max-self.y_min)/y_len

        self.scripts['GalvoScan'].settings['point_a']['x'] = x_min
        self.scripts['GalvoScan'].settings['point_b']['x'] = x_max
        self.scripts['GalvoScan'].settings['point_a']['y'] = y_min
        self.scripts['GalvoScan'].settings['point_b']['y'] = y_max

        self.scripts['GalvoScan'].run()
        self.scripts['GalvoScan'].wait()  #wait for scan to complete
        new_image = self.scripts['GalvoScan'].data['image_data']

        new_image_sub = new_image - new_image.mean()

        #takes center part of baseline image
        x_len = len(baseline_image_sub[0])
        y_len = len(baseline_image_sub)
        old_image = baseline_image_sub[(x_len/4):(x_len*3/4),(y_len/4):(y_len*3/4)]

        # correlate with new image. mode='valid' ignores all correlation points where an image is out of bounds. if baseline
        # and new image are NxN, returns a (N/2)x(N/2) correlation
        self.corr_image = signal.correlate2d(new_image_sub, baseline_image_sub)
        y, x = np.unravel_index(np.argmax(self.corr_image), self.corr_image.shape)

        # finds shift by subtracting center of initial coordinates, x_shift = x + (x_len/4) - (x_len/2)
        self.data['x_shift'] = (x - (x_len))*x_pixel_to_voltage
        self.data['y_shift'] = (y - (y_len))*y_pixel_to_voltage

        print('xshift', self.data['x_shift'], 'xshift', self.data['x_shift'])

    def shift_coordinates(self, coordinates):
        new_coordinates = list()
        for coor in coordinates:
            new_x = coor[0] + self.data['x_shift']
            new_y = coor[1] + self.data['y_shift']
            new_coordinates.append((new_x,new_y))


    def plot(self, axes):
        axes.imshow(self.corr_image, cmap = 'pink', interpolation = 'nearest')


if __name__ == '__main__':
    script, failed, instr = Script.load_and_append({'Correlate_Images': 'Correlate_Images'})

    print(script)
    print(failed)
    print(instr)
