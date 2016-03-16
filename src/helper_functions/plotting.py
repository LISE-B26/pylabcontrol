__author__ = 'Experiment'
'''
    here we collect all the functions for plotting. These functions can then be used in the GUI or in ipython notebooks
'''

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

from src import helper_functions as mesh

def plot_scan_image(axes, image_data, region, title=None):
    '''

    :param axes: axes object where to plot
    :param image_data: image data to be plotted
    :param region: dictionary specifying extent of image
    :param title: plot title
    :return:
    '''

    extent = mesh.roi_to_extent(region)
    xmin, xmax, ymin, ymax = mesh.roi_to_min_max(region)

    axes.imshow(image_data, extent=extent, interpolation = 'none', cmap = 'RdYlBu', aspect='auto')
    if not title == None:
        axes.set_title(title)
    axes.set_aspect(1)
    axes.set_xlabel('x Voltage [V]')
    axes.set_ylabel('y Voltage [V]')

    # axes.set_xlim([xmin, xmax])
    # axes.set_ylim([ymax, ymin])


def plot_cont_img1_col_img2(axes, image_data_1, image_data_2, region, threshold = [30, 40], title=None):
    '''

    :param axes:
    :param image_data_1:  image data used for contour
    :param image_data_2:   image data used for color plot
    :param region:
    :param threshold:
    :param title:
    '''

    extent = mesh.roi_to_extent(region)
    xmin, xmax, ymin, ymax = mesh.roi_to_min_max(region)

    axes.imshow(image_data_2 * (1-np.logical_and(image_data_1>threshold[0], image_data_1<threshold[1])), extent=extent, interpolation = 'none', cmap = 'RdYlBu', aspect='auto')

    if not title == None:
        axes.set_title(title)
    axes.set_aspect(1)
    axes.set_xlabel('x Voltage [V]')
    axes.set_ylabel('y Voltage [V]')

    # axes.set_xlim([xmin, xmax])
    # axes.set_ylim([ymax, ymin])


def plot_esr_plot(axes, esr_freq, esr_data, title='Image'):
    '''
    :param axes:  axes object where to plot
    :param esr_freq: 1d array with frequenies
    :param esr_data: 1d array with esr data
    :param title: plot title
    '''
    axes.plot(esr_freq*1e-9, esr_data)
    axes.set_title(title)
    axes.set_xlabel('frequency (MHz)')
    axes.set_ylabel('esr signal (kCounts /sec)')
    axes.set_xlim([min(esr_freq*1e-9), max(esr_freq*1e-9)])


def plot_esr_data_and_pos(img_data_reflect, img_data_fluor, region, esr_freq, esr_data, pt, size = 0.02):
    '''
    :param img_data_reflect: fluoresence image  data to be plotted
    :param img_data_fluor: reflection image data to be plotted
    :param region:  dictionary specifying extent of image
    :param pt: point to be plotted on top of images to show the laser position
    :param size:  size of dot
    :return: figure
    '''
    fig = plt.figure(figsize=(15,10))
    gs = gridspec.GridSpec(2, 2)
    ax_reflect = plt.subplot(gs[0, 0])
    ax_fluor = plt.subplot(gs[0,1])
    ax_esr = plt.subplot(gs[1, :])


    plot_scan_image(ax_reflect, img_data_reflect, region, title='reflect')
    patch = patches.Circle((pt[0], pt[1]), 2*size, fc = 'y')
    ax_reflect.add_patch(patch)

    plot_cont_img1_col_img2(ax_fluor, img_data_reflect, img_data_fluor, region, threshold = [30, 40], title='fluor')
    # plot_scan_image(ax_fluor, img_data_fluor, region, title='fluor')
    plt.setp(ax_fluor.get_yticklabels(), visible=False)
    ax_fluor.set_ylabel('')

    patch = patches.Circle((pt[0], pt[1]), 2*size, fc = 'y')
    ax_fluor.add_patch(patch)

    plot_esr_plot(ax_esr, esr_freq, esr_data, title='esr')
    return fig
