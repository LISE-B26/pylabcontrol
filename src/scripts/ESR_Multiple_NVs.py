from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
from src.scripts import StanfordResearch_ESR, Find_NVs
from collections import deque
import time
import numpy as np
from copy import deepcopy

class ESR_Multiple_NVs(Script, QThread):

    # NOTE THAT THE ORDER OF Script and QThread IS IMPORTANT!!
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('nv_locations', [], list, 'list of NV locations')
    ])

    _SCRIPTS = {
        'esr': StanfordResearch_ESR,
        'Find_NVs': Find_NVs
    }

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
        QThread.__init__(self)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        def calc_progress():
            pass

        self.save(save_data=True, save_instrumets=False, save_log=False, save_settings=False)

        progress = calc_progress()

        self.updateProgress.emit(progress)

        self.updateProgress.emit(100)

if __name__ == '__main__':
    script = {}
    instr = {}
    script, failed, instr = Script.load_and_append({'ESR_Multiple_NVs':'ESR_Multiple_NVs'}, script, instr)

    print(script)
    print(failed)
    print(instr)