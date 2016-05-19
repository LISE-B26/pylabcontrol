from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
import numpy as np
import matplotlib.patches as patches

class Correlate_Images(Script):
    _DEFAULT_SETTINGS = Parameter([
        Parameter('baseline_image_path', '', str, 'path for data'),
        Parameter('baseline_image_tag', '', str, 'some_name'),
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/__test_data_for_coding/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('new_image', np.array([]), np.ndarray, 'Numpy array with new image')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, instruments = None, name = None, settings = None, scripts = None, log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_output = log_output)

    def _function(self):
        """
        # Tracks drift by correlating new and old images, and returns shift in pixels
        """
        # subtracts mean to sharpen each image and sharpen correlation
        baseline_image_sub = baseline_image - baseline_image.mean()
        new_image_sub = new_image - new_image.mean()

        #takes center part of baseline image
        x_len = len(baseline_image_sub[0])
        y_len = len(baseline_image_sub)
        old_image = baseline_image_sub[(x_len/4):(x_len*3/4),(y_len/4):(y_len*3/4)]

        # correlate with new image. mode='valid' ignores all correlation points where an image is out of bounds. if baseline
        # and new image are NxN, returns a (N/2)x(N/2) correlation
        corr = signal.correlate2d(new_image_sub, baseline_image_sub)
        y, x = np.unravel_index(np.argmax(corr), corr.shape)

        # finds shift by subtracting center of initial coordinates, x_shift = x + (x_len/4) - (x_len/2)
        x_shift = x - (x_len)
        y_shift = y - (y_len)

        #return (x_shift, y_shift) #, corr, old_image --- test outputs
        return (x_shift, y_shift, corr, old_image) # --- test outputs



    def plot(self, axes):
        image  = self.data['image']


if __name__ == '__main__':
    script, failed, instr = Script.load_and_append({'Correlate_Images': 'Correlate_Images'})

    print(script)
    print(failed)
    print(instr)
