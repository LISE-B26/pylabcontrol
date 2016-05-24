# ==========================================================================================================
# ==========================================================================================================
#
#
# ==========================================================================================================
# ==========================================================================================================

from src.core import Script
from src.core import plotting
import matplotlib.pyplot as plt


def galvo_images(data_path, target_path = None):
    """
    save load data from galvo scans and save images to target directory
    Args:
        data_path: path to image data
        target_path: target path to save images

    Returns:

    """
    if target_path == None:
        target_path = DATA_PATH

    data  = Script.load_data(DATA_PATH)
    number_of_images = len([k for k in data.keys() if len(k.split('image'))>1])

    for c in range(number_of_images):
        k  = 'image_{:d}'.format(c)
        fig = plt.figure()
        ax = plt.subplot(111)
        plotting.plot_fluorescence(data[k], extent =[0.02, 0.17, 0.05, -0.10],  axes = ax)
        fig.savefig('{:s}/{:s}.png'.format(TARGET_PATH, k))
        fig.close()

if __name__ == '__main__':

    DATA_PATH = 'Z:\\Lab\\Cantilever\\Measurements\\20160524_Focsing\\160524-15_18_51_reflection\\'

    galvo_images(DATA_PATH)
