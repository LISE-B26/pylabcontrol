import numpy as np
import scipy.spatial
import time
from matplotlib import patches

from src.core import Script, Parameter

from src.scripts import Find_Points


#DEPRECIATED: use Select_NVs_Simple below
# class Select_NVs(Script, QThread):
#     updateProgress = Signal(int)
#
#     _DEFAULT_SETTINGS = Parameter([
#         Parameter('path', 'Z:/Lab/Cantilever/Measurements/', str, 'path for data'),
#         Parameter('tag', 'dummy_tag', str, 'tag for data'),
#         Parameter('save', True, bool, 'save data on/off')
#     ])
#
#     _INSTRUMENTS = {}
#     _SCRIPTS = {
#         'Find_Points': Find_Points
#     }
#
#     #This is the signal that will be emitted during the processing.
#     #By including int as an argument, it lets the signal know to expect
#     #an integer argument when emitting.
#
#     def __init__(self, instruments = None, scripts = None, name = None, settings = None, log_function = None, data_path = None):
#         """
#         Example of a script that emits a QT signal for the gui
#         Args:
#             name (optional): name of script, if empty same as class name
#             settings (optional): settings for this script, if empty same as default settings
#         """
#         Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)
#
#         QThread.__init__(self)
#
#         self._plot_type = 'main'
#
#     def _function(self):
#         """
#         This is the actual function that will be executed. It uses only information that is provided in the settings property
#         will be overwritten in the __init__
#         """
#         self.scripts['Find_Points'].start()
#         self.coordinates = self.scripts['Find_Points'].data['NV_positions']
#         self.patches = []
#         self.data = {'nv_locations': []}
#
#         self.updateProgress.emit(50)
#         while not self._abort:
#             time.sleep(1)
#
#         if self.settings['save']:
#             self.save_b26()
#             self.save_data()
#             self.log('saving')
#
#         self.updateProgress.emit(100)
#         self._abort = False
#
#     def stop(self):
#         self._abort = True
#
#     def plot(self, axes):
#         if not self.data['nv_locations']:
#             self.scripts['Find_Points'].plot(axes)
#         else:
#             image = self.scripts['Find_Points'].data['image']
#             extend = [self.scripts['Find_Points'].x_min, self.scripts['Find_Points'].x_max, self.scripts['Find_Points'].y_max, self.scripts['Find_Points'].y_min]
#             plot_fluorescence(image, extend, axes)
#
#             for x in self.data['nv_locations']:
#                 patch = patches.Circle((x[0], x[1]), .001, fc='b')
#                 axes.add_patch(patch)
#
#     def toggle_NV(self, pt, axes):
#         #use KDTree to find NV closest to mouse click
#         tree = scipy.spatial.KDTree(self.coordinates)
#         _, i = tree.query(pt)
#         nv_pt = self.coordinates[i]
#
#         # removes NV if previously selected
#         if (nv_pt in self.data['nv_locations']):
#             self.data['nv_locations'].remove(nv_pt)
#             for circ in self.patches:
#                 if (nv_pt == np.array(circ.center)).all():
#                     self.patches.remove(circ)
#                     circ.remove()
#                     break
#         # adds NV if not previously selected
#         else:
#             self.data['nv_locations'].append(nv_pt)
#             circ = patches.Circle((nv_pt[0], nv_pt[1]), .001, fc='b')
#             axes.add_patch(circ)
#             self.patches.append(circ)

# todo: rename script to Select_NVs (first make sure it works with the new plotting)
class Select_NVs_Simple(Script):
    _DEFAULT_SETTINGS = [Parameter('patch_size', 0.003)]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.

    def __init__(self, instruments = None, scripts = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Example of a script that emits a QT signal for the gui
        Args:
            name (optional): name of script, if empty same as class name
            settings (optional): settings for this script, if empty same as default settings
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)

        self.data = {'nv_locations': []}

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self._abort = False

        self.patches = []
        self.data = {'nv_locations': []}

        self.updateProgress.emit(50)
        # keep script alive while NVs are selected
        while not self._abort:
            time.sleep(1)
        print('FINISEHD selection .... ')


    def stop(self):
        self._abort = True

    #must be passed figure with galvo plot on first axis
    def plot(self, figure_list):
        axes = figure_list[0].axes[0]
        patch_size = self.settings['patch_size']

        # delete all previous patches
        self.patches  = []

        for index, pt in enumerate(self.data['nv_locations']):
            # axes.plot(pt, fc='b')

            circ = patches.Circle((pt[0], pt[1]), patch_size, fc='b')
            axes.add_patch(circ)
            self.patches.append(circ)

            axes.text(pt[0], pt[1], '{:d}'.format(index),
                    horizontalalignment='center',
                    verticalalignment='center',
                    color='white'
                    )

    def toggle_NV(self, pt, figure):
        # patch_size = self.settings['patch_size']
        print(pt)

        axes = figure.axes
        if type(axes) is list:
            axes = axes[0]

        if not self.data['nv_locations']:
            self.data['nv_locations'].append(pt)
        # circ = patches.Circle((nv_pt[0], nv_pt[1]), patch_size, fc='b')
        # axes.add_patch(circ)
        # self.patches.append(circ)

        else:
            # use KDTree to find NV closest to mouse click
            tree = scipy.spatial.KDTree(self.data['nv_locations'])
            d, i = tree.query(pt,k = 1, distance_upper_bound = self.settings['patch_size'])

            # removes NV if previously selected
            if d is not np.inf:
                nv_pt = self.data['nv_locations'][i]
                # print(nv_pt)
                # self.data['nv_locations'].remove(np.array(nv_pt))
                # for circ in self.patches:
                #     if (nv_pt == np.array(circ.center)).all():
                #         self.patches.remove(circ)
                #         circ.remove()
                #         break
            # adds NV if not previously selected
            else:
                self.data['nv_locations'].append(pt)
                circ = patches.Circle((pt[0], pt[1]), .001, fc='b')
                axes.add_patch(circ)
                self.patches.append(circ)

        self.plot(figure)


if __name__ == '__main__':


    script, failed, instr = Script.load_and_append({'Select_NVs':'Select_NVs'})

    print(script)
    print(failed)
    print(instr)