def plot_fluorescence(image_data, extent, axes):
    """

    Args:
        image_data: 2D - array
        extent: vector of length 4, i.e. [x_min, x_max, y_max, y_min]
        axes: axes object on which to plot

    Returns:

    """
    axes.imshow(image_data, cmap='pink', interpolation="nearest", extent=extent)
    axes.set_xlabel('Vx')
    axes.set_ylabel('Vy')
    axes.set_title('Confocal Image')



