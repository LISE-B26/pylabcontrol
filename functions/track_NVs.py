from scipy import signal
import numpy as np
import scipy.optimize as opt
from scipy import ndimage
import matplotlib.pyplot as plt
import skimage.feature
from skimage import data, img_as_float
import pandas as pd


class track_NVs():
    def __init__(self, image, point):
        self.baseline_image = image
        self.NV_location = self.locate_NV(image,5)

    def locate_NV(self, image, min_separation):
        self.coordinates = skimage.feature.peak_local_max(image, min_separation, exclude_border=False)

    def get_NVs(self):
        return self.coordinates



#image = pd.read_csv("C:\\Users\\Aaron\\Desktop\\NVTrainingData\\2015-06-29_18-43-58-NVBaselineTests.csv")
image = pd.read_csv("C:\\Users\\Aaron\\Desktop\\NVTrainingData\\2015-06-27_16-53-09-NVBaseline.csv")
image_np = image.as_matrix()
image_gaussian = ndimage.gaussian_filter(image_np, 1.5, mode='reflect')
tracker = track_NVs(image_gaussian, (1,1))
coordinates = tracker.get_NVs()
fig, ax = plt.subplots(1, 3, figsize=(8, 3))
ax1, ax2, ax3 = ax.ravel()
ax1.imshow(image_np, cmap=plt.cm.gray)
ax1.axis('off')
ax1.set_title('Original')

ax2.imshow(image_gaussian, cmap=plt.cm.gray)
ax2.axis('off')
ax2.set_title('Maximum filter')

ax3.imshow(image_np, cmap=plt.cm.gray)
ax3.autoscale(False)
ax3.plot(coordinates[:, 1], coordinates[:, 0], 'r.')
ax3.axis('off')
ax3.set_title('Peak local max')

print(coordinates)

plt.show()
