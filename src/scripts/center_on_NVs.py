from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
import numpy as np
import matplotlib.patches as patches
from src.scripts.galvo_scan import GalvoScan
from scipy import signal

class Center_On_NVs(Script):
    _DEFAULT_SETTINGS = Parameter([
        Parameter('baseline_image_path', '', str, 'path for data'),
        Parameter('baseline_image_tag', '', str, 'some_name'),
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/__test_data_for_coding/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {'GalvoScan': GalvoScan}

    def __init__(self, instruments = None, name = None, settings = None, scripts = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)


    def _function(self):
        """
        # Tracks drift by correlating new and old images, and returns shift in pixels
        """
        # subtracts mean to sharpen each image and sharpen correlation



    def plot(self, axes):
        axes.imshow(self.corr_image, cmap = 'pink', interpolation = 'nearest')


if __name__ == '__main__':
    script, failed, instr = Script.load_and_append({'Center_On_NVs': 'Center_On_NVs'})

    print(script)
    print(failed)
    print(instr)
