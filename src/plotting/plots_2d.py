import numpy as np


def plot_fluorescence(image_data, extent, axes_image, implot=None, cbar=None, max_counts=-1, axes_colorbar=None):
    """

    Args:
        image_data: 2D - array
        extent: vector of length 4, i.e. [x_min, x_max, y_max, y_min]
        axes: axes object on which to plot
        implot: reference to image plot
    Returns:

    """
    fig = axes_image.get_figure()

    if axes_colorbar is None:
        # try to figure out if there is a axis for the colorbar
        fig = axes_image.get_figure()
        number_of_axes = len(fig.axes)
        for index in range(number_of_axes):
            if fig.axes[index] == axes_image and index < number_of_axes - 1:
                axes_colorbar = fig.axes[index + 1]

    if implot is None:
        if max_counts > 0:
            implot = axes_image.imshow(image_data, cmap='pink', interpolation="nearest", extent=extent, vmax=max_counts)
        else:
            implot = axes_image.imshow(image_data, cmap='pink', interpolation="nearest", extent=extent)
        axes_image.set_xlabel('Vx [V]')
        axes_image.set_ylabel('Vy [V]')
        axes_image.set_title('Confocal Image')
    else:
        implot.set_data(image_data)

    if not max_counts > 0:
        implot.autoscale()

    if axes_colorbar is None and cbar is None:
        cbar = fig.colorbar(implot, label='kcounts/sec')
    elif cbar is None:
        cbar = fig.colorbar(implot, cax=axes_colorbar, label='kcounts/sec')
    else:
        cbar.update_bruteforce(implot)

    fig.tight_layout()

    return implot, cbar
