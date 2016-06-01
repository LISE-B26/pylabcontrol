def plot_fluorescence(image_data, extent, axes_image, max_counts = -1, axes_colorbar = None):
    """

    Args:
        image_data: 2D - array
        extent: vector of length 4, i.e. [x_min, x_max, y_max, y_min]
        axes: axes object on which to plot

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

    if max_counts > 0:
        implot = axes_image.imshow(image_data, cmap='pink', interpolation="nearest", extent=extent, vmax = max_counts)
    else:
        implot = axes_image.imshow(image_data, cmap='pink', interpolation="nearest", extent=extent)
    axes_image.set_xlabel('Vx')
    axes_image.set_ylabel('Vy')
    axes_image.set_title('Confocal Image')

    if axes_colorbar is None:
        fig.colorbar(implot, label='kcounts/sec')
    else:
        fig.colorbar(implot, cax=axes_colorbar, label='kcounts/sec')


    fig.tight_layout()



