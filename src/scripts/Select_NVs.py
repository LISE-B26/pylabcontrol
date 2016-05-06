from src.core import Script, Parameter
from src.scripts import Find_Points
import time
import scipy.spatial
import numpy as np
from matplotlib import patches


class Select_NVs(Script):
    _DEFAULT_SETTINGS = Parameter([
        Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
        Parameter('tag', 'dummy_tag', str, 'tag for data'),
        Parameter('save', True, bool, 'save data on/off'),
        Parameter('nv_locations', [], list, 'list of NV locations')
    ])

    _INSTRUMENTS = {}
    _SCRIPTS = {
        'Find_Points': Find_Points
    }

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.

    def __init__(self, instruments = None, name = None, settings = None,  log_output = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        self._abort = False
        Script.__init__(self, name, settings = settings, instruments = instruments, log_output = log_output)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self.scripts['Find_Points'].run()
        self.coordinates = self.scripts['Find_Points'].data['coordinates']
        self.patches = []

        while not self._abort:
            time.sleep(1)

        self.save(save_data=True, save_instrumets=False, save_log=False, save_settings=False)

    def stop(self):
        self._abort = True

    def plot(self, axes):
        self.scripts['Find_Points'].plot(axes)

    def toggle_NV(self, pt, axes):
        #use KDTree to find NV closest to mouse click
        tree = scipy.spatial.KDTree(self.coordinates)
        _, i = tree.query(pt)
        nv_pt = self.coordinates[i].tolist()

        # removes NV if previously selected
        if (nv_pt in self.settings['nv_locations']):
            self.settings['nv_locations'].remove(nv_pt)
            for circ in self.patches:
                if (nv_pt == np.array(circ.center)).all():
                    self.patches.remove(circ)
                    circ.remove()
                    break
        # adds NV if not previously selected
        else:
            self.self.settings['nv_locations'].append(nv_pt)
            circ = patches.Circle((nv_pt[0], nv_pt[1]), 2, fc='b')
            axes.add_patch(circ)
            self.patches.append(circ)


if __name__ == '__main__':
    script, failed, instr = Script.load_and_append({'Select_NVs':'Select_NVs'})

    print(script)
    print(failed)
    print(instr)