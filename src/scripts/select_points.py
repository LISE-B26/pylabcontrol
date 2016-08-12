"""
    This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
    Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell


    PyLabControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyLabControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.

"""
import numpy as np
import scipy.spatial
import time
from matplotlib import patches

from PyLabControl.src.core import Script, Parameter

class SelectPoints(Script):
    """
Script to select points on an image. The selected points are saved and can be used in a superscript to iterate over.
    """
    _DEFAULT_SETTINGS = [Parameter('patch_size', 0.003)]

    _INSTRUMENTS = {}
    _SCRIPTS = {}

    def __init__(self, instruments = None, scripts = None, name = None, settings = None, log_function = None, data_path = None):
        """
        Select points by clicking on an image
        """
        Script.__init__(self, name, settings = settings, instruments = instruments, scripts = scripts, log_function= log_function, data_path = data_path)

        self.patches = []
        self.plot_settings = {}

    def _function(self):
        """
        Waits until stopped to keep script live. Gui must handle calling of Toggle_NV function on mouse click.
        """

        self.data = {'nv_locations': [], 'image_data': None}

        self.progress = 50
        self.updateProgress.emit(self.progress)
        # keep script alive while NVs are selected
        while not self._abort:
            time.sleep(1)


    def plot(self, figure_list):
        '''
        Plots a dot on top of each selected NV, with a corresponding number denoting the order in which the NVs are
        listed.
        Precondition: must have an existing image in figure_list[0] to plot over
        Args:
            figure_list:
        '''
        print('aaaa', self.data)
        # if there is not image data get it from the current plot
        if not self.data == {} and self.data['image_data'] is  None:
            axes = figure_list[0].axes[0]
            if len(axes.images)>0:
                self.data['image_data'] = np.array(axes.images[0].get_array())
                self.data['extent'] = np.array(axes.images[0].get_extent())
                self.plot_settings['cmap'] = axes.images[0].get_cmap().name
                self.plot_settings['xlabel'] = axes.get_xlabel()
                self.plot_settings['ylabel'] = axes.get_ylabel()
                self.plot_settings['title'] = axes.get_title()
                self.plot_settings['interpol'] = axes.images[0].get_interpolation()

        Script.plot(self, figure_list)

    #must be passed figure with galvo plot on first axis
    def _plot(self, axes_list):
        '''
        Plots a dot on top of each selected NV, with a corresponding number denoting the order in which the NVs are
        listed.
        Precondition: must have an existing image in figure_list[0] to plot over
        Args:
            figure_list:
        '''

        axes = axes_list[0]

        if self.plot_settings:
            axes.imshow(self.data['image_data'], cmap=self.plot_settings['cmap'], interpolation=self.plot_settings['interpol'], extent=self.data['extent'])
            axes.set_xlabel(self.plot_settings['xlabel'])
            axes.set_ylabel(self.plot_settings['ylabel'])
            axes.set_title(self.plot_settings['title'])

        self._update(axes_list)

    def _update(self, axes_list):

        axes = axes_list[0]

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
            self.data['image_data'] = None # clear image data

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