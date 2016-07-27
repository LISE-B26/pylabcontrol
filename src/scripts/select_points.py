import numpy as np
import scipy.spatial
import time
from matplotlib import patches

from PyLabControl.src.core import Script, Parameter

class SelectPoints(Script):
    # COMMENT_ME
    _DEFAULT_SETTINGS = [Parameter('patch_size', 0.003)]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, instruments = None, scripts = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Select points by clicking on an image
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)

        self.data = {'nv_locations': []}
        self.patches = []

    def _function(self):
        """
        Waits until stopped to keep script live. Gui must handle calling of Toggle_NV function on mouse click.
        """

        self.data = {'nv_locations': []}

        self.progress = 50
        self.updateProgress.emit(self.progress)
        # keep script alive while NVs are selected
        while not self._abort:
            time.sleep(1)

    #must be passed figure with galvo plot on first axis
    def plot(self, figure_list):
        '''
        Plots a dot on top of each selected NV, with a corresponding number denoting the order in which the NVs are
        listed.
        Precondition: must have an existing image in figure_list[0] to plot over
        Args:
            figure_list:
        '''
        axes = figure_list[0].axes[0]
        patch_size = self.settings['patch_size']

        #first clear all old patches (circles and numbers), then redraw all
        if not self.patches == []:
            try: #catch case where plot has been cleared, so old patches no longer exist. Then skip clearing step.
                for patch in self.patches:
                    patch.remove()
            except ValueError:
                pass

        self.patches = []

        for index, pt in enumerate(self.data['nv_locations']):
            # axes.plot(pt, fc='b')

            circ = patches.Circle((pt[0], pt[1]), patch_size, fc='b')
            axes.add_patch(circ)
            self.patches.append(circ)

            text = axes.text(pt[0], pt[1], '{:d}'.format(index),
                    horizontalalignment='center',
                    verticalalignment='center',
                    color='white'
                    )
            self.patches.append(text)

    def toggle_NV(self, pt):
        '''
        If there is not currently a selected NV within self.settings[patch_size] of pt, adds it to the selected list. If
        there is, removes that point from the selected list.
        Args:
            pt: the point to add or remove from the selected list

        Poststate: updates selected list

        '''
        if not self.data['nv_locations']: #if self.data is empty so this is the first point
            self.data['nv_locations'].append(pt)

        else:
            # use KDTree to find NV closest to mouse click
            tree = scipy.spatial.KDTree(self.data['nv_locations'])
            #does a search with k=1, that is a search for the nearest neighbor, within distance_upper_bound
            d, i = tree.query(pt,k = 1, distance_upper_bound = self.settings['patch_size'])

            # removes NV if previously selected
            if d is not np.inf:
                self.data['nv_locations'].pop(i)
            # adds NV if not previously selected
            else:
                self.data['nv_locations'].append(pt)


if __name__ == '__main__':


    script, failed, instr = Script.load_and_append({'SelectPoints':'SelectPoints'})

    print(script)
    print(failed)
    print(instr)