from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
import numpy as np
import matplotlib.patches as patches
from src.scripts.galvo_scan import GalvoScan
from scipy import signal
from PIL import Image as im

from PySide.QtCore import Signal, QThread


class Correlate_Images(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('baseline_image_path', '', str, 'path for data'),
        Parameter('baseline_image_tag', '', str, 'some_name'),
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/__test_data_for_coding/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('new_image_center', ((0,0)), tuple, 'Center of new image to acquire for correlation'),
        Parameter('new_image_width', 0.1, float, 'Height and Width in V of new image to take')
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
        QThread.__init__(self)

        self.data = {'baseline_image': [], 'new_image': [], 'x_shift': 0, 'y_shift': 0}
        #forward the galvo scan progress to the top layer
        self.scripts['GalvoScan'].updateProgress.connect(lambda x: self.updateProgress.emit(x))

        self._plot_type = 2

    def _function(self):
        """
        # Tracks drift by correlating new and old images, and returns shift in pixels
        """
        # subtracts mean to sharpen each image and sharpen correlation
        assert(self.settings['new_image_width'] < 1)

        self.baseline_image = Script.load_data(self.settings['baseline_image_path'], data_name_in='image_data')
        bounds = Script.load_data(self.settings['baseline_image_path'], data_name_in='bounds')
        baseline_image_sub = self.baseline_image - self.baseline_image.mean()

        #compute new guess of where the POI should be based on last known shift
        center_guess = ((self.settings['new_image_center'][0] + self.data['x_shift'],self.settings['new_image_center'][1] + self.data['x_shift']))

        x_min = bounds[0][0]
        x_max = bounds[1][0]
        y_min = bounds[2][0]
        y_max = bounds[3][0]
        x_len = self.baseline_image.shape[1]
        y_len = self.baseline_image.shape[0]
        x_pixel_to_voltage= (x_max-x_min)/x_len
        y_pixel_to_voltage= (y_max-y_min)/y_len

        new_x_min = center_guess[0]-(self.settings['new_image_width']/2)
        new_x_max = center_guess[0]+(self.settings['new_image_width']/2)
        new_y_min = center_guess[1]-(self.settings['new_image_width']/2)
        new_y_max = center_guess[1]+(self.settings['new_image_width']/2)

        if new_x_min < -.5:
            new_x_max += (-.5 - new_x_min)
            new_x_min = -.5
            self.log('Correlation: Left Boundary Reached')
        elif new_x_max > .5:
            new_x_min += (.5 - new_x_max)
            new_x_min = .5
            self.log('Correlation: Right Boundary Reached')
        if new_y_min < -.5:
            new_y_max += (-.5 - new_y_min)
            new_y_min = -.5
            self.log('Correlation: Lower Boundary Reached')
        elif new_y_max > .5:
            new_y_min += (.5 - new_y_max)
            new_y_min = .5
            self.log('Correlation: Upper Boundary Reached')

        self.scripts['GalvoScan'].settings['point_a']['x'] = new_x_min
        self.scripts['GalvoScan'].settings['point_b']['x'] = new_x_max
        self.scripts['GalvoScan'].settings['point_a']['y'] = new_y_min
        self.scripts['GalvoScan'].settings['point_b']['y'] = new_y_max

        self.scripts['GalvoScan'].run()
        self.scripts['GalvoScan'].wait()  #wait for scan to complete
        self.new_image = self.scripts['GalvoScan'].data['image_data']

        new_x_len = self.new_image.shape[1]
        new_y_len = self.new_image.shape[0]
        new_x_pixel_to_voltage = (new_x_max-new_x_min)/new_x_len
        new_y_pixel_to_voltage = (new_y_max-new_y_min)/new_y_len

        new_image_sub = self.new_image - self.new_image.mean()

        if x_pixel_to_voltage > new_x_pixel_to_voltage:
            size = int(round(baseline_image_sub.shape[0]*(new_x_pixel_to_voltage/x_pixel_to_voltage)))
            size = (size,size)
            baseline_image_sub_PIL = im.fromarray(baseline_image_sub)
            baseline_image_sub_PIL.resize(size, im.ANTIALIAS)
            baseline_image_sub = np.reshape(np.array(list(baseline_image_sub_PIL.getdata())), size)
        elif x_pixel_to_voltage < new_x_pixel_to_voltage:
            size = int(round(new_image_sub.shape[0]*(x_pixel_to_voltage/new_x_pixel_to_voltage)))
            size = (size,size)
            new_image_sub_PIL = im.fromarray(new_image_sub)
            new_image_sub_PIL.resize(size, im.ANTIALIAS)
            new_image_sub = np.reshape(np.array(list(new_image_sub_PIL.getdata())), size)

        #takes center part of baseline image
        # x_len = len(baseline_image_sub[0])
        # y_len = len(baseline_image_sub)
        # old_image = baseline_image_sub[(x_len/4):(x_len*3/4),(y_len/4):(y_len*3/4)]

        # correlate with new image. mode='valid' ignores all correlation points where an image is out of bounds. if baseline
        # and new image are NxN, returns a (N/2)x(N/2) correlation
        self.corr_image = signal.correlate2d(new_image_sub, baseline_image_sub)
        y, x = np.unravel_index(np.argmax(self.corr_image), self.corr_image.shape)

        x_expected_location = (self.settings['new_image_center'][0] - x_min)/x_pixel_to_voltage
        y_expected_location = (y_max - self.settings['new_image_center'][1])/y_pixel_to_voltage

        #correct shift for change with respect to guess
        self.data['x_shift'] = self.data['x_shift'] + (x-x_expected_location)*x_pixel_to_voltage
        self.data['y_shift'] = self.data['y_shift'] + (y-y_expected_location)*y_pixel_to_voltage

        # self.data['x_shift'] = self.data['x_shift'] + ((x+1) - (x_len))*x_pixel_to_voltage
        # self.data['y_shift'] = self.data['y_shift'] + ((y+1) - (y_len))*y_pixel_to_voltage

        self.data['baseline_image'] = baseline_image_sub
        self.data['new_image'] = new_image_sub

    def shift_coordinates(self, coordinates):
        new_coordinates = list()
        for coor in coordinates:
            new_x = coor[0] + self.data['x_shift']
            new_y = coor[1] + self.data['y_shift']
            new_coordinates.append((new_x,new_y))

    def plot(self, axes, axes_2):
        # axes.imshow(self.corr_image, cmap = 'pink', interpolation = 'nearest')
        axes.imshow(self.baseline_image, cmap = 'pink', interpolation = 'nearest')
        new_center = ((self.settings['new_image_center'][0] + self.data['x_shift'], self.settings['new_image_center'][1] + self.data['y_shift']))
        patch = patches.Rectangle(new_center, self.settings['new_image_width'], self.settings['new_image_width'], fill = False)
        axes.add_patch(patch)
        axes_2.imshow(self.new_image, cmap = 'pink', interpolation = 'nearest')

if __name__ == '__main__':
    script, failed, instr = Script.load_and_append({'Correlate_Images': 'Correlate_Images'})

    print(script)
    print(failed)
    print(instr)
