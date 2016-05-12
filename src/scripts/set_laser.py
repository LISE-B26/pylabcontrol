from src.core import Script, Parameter
from src.scripts import StanfordResearch_ESR
from src.instruments.NIDAQ import DAQ
import time
import scipy.spatial
import numpy as np
from matplotlib import patches
from PySide.QtCore import Signal, QThread
from src.core.plotting import plot_fluorescence




class SetLaser(Script):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('point_laser',
                  [Parameter('x', -0.4, float, 'x-coordinate'),
                   Parameter('y', -0.4, float, 'y-coordinate')
                   ])
    ])

    _INSTRUMENTS = {'daq':  DAQ}

    _SCRIPTS = {}

    #updateProgress = Signal(int)

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.

    def __init__(self, instruments = None, scripts = None, name = None, settings = None,  log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_output = log_output)

        self._plot_type = 1

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        pt = (self.settings['point_laser']['x'], self.settings['point_laser']['y'])
        pt = np.transpose(np.column_stack((pt[0],pt[1])))
        pt = (np.repeat(pt, 2, axis=1))

        self.instruments['daq']['instance'].AO_init(["ao0","ao1"], pt)
        self.instruments['daq']['instance'].AO_run()
        self.instruments['daq']['instance'].AO_waitToFinish()
        self.instruments['daq']['instance'].AO_stop()

    def plot(self, axes_Image):
        patch = patches.Circle((self.settings['point_laser']['x'], self.settings['point_laser']['y']), .0005, fc='r')
        axes_Image.add_patch(patch)


if __name__ == '__main__':
    from src.core import Instrument

    instruments, instruments_failed = Instrument.load_and_append({'daq':  'DAQ'})

    script, failed, instruments = Script.load_and_append(script_dict={'SetLaser':'SetLaser'}, instruments = instruments)

    print(script)
    print(failed)
    # print(instruments)