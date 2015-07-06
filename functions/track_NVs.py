from scipy import signal
import numpy as np
import scipy.optimize as opt
from scipy import ndimage
import matplotlib.pyplot as plt
import skimage.feature
from skimage import data, img_as_float
import pandas as pd
from matplotlib.patches import Rectangle


class track_NVs():
    def __init__(self, image, point = None):
        self.baseline_image = image
        self.NV_location = self.locate_NV(image,5)

    def locate_NV(self, image, min_separation):
        self.coordinates = skimage.feature.peak_local_max(image, min_separation, exclude_border=False)

    def get_NVs(self):
        return self.coordinates

    def corr_NVs(self, new_image):
        x_len = len(self.baseline_image[0])
        y_len = len(self.baseline_image)
        old_image = self.baseline_image[(x_len/4):(x_len*3/4),(y_len/4):(y_len*3/4)]
        corr = signal.correlate2d (new_image, old_image, boundary='symm', mode='same')
        y, x = np.unravel_index(np.argmax(corr), corr.shape) # find the match
        return old_image,corr,x,y



    def twoD_Gaussian((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
        xo = float(xo)
        yo = float(yo)
        a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
        b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
        c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
        g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo)
                                + c*((y-yo)**2)))
        return g.ravel()



#image = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-29_18-43-58-NVBaselineTests.csv")
#image = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-27_16-53-09-NVBaseline.csv")
image = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-29_18-51-59-NVBaselineTests.csv")
image2 = pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-29_19-11-24-NVBaselineTests.csv")

image_np = image.as_matrix()
image2_np = image2.as_matrix()
tracker = track_NVs(image_np)
orig,corr,x,y = tracker.corr_NVs(image2_np)
print(x)
print(y)

fig, ax = plt.subplots(1, 3, figsize=(8, 3))
ax1, ax2, ax3 = ax.ravel()
ax1.imshow(orig, cmap=plt.cm.gray)
ax2.imshow(corr, cmap=plt.cm.gray)
ax3.imshow(image2_np,cmap = plt.cm.gray)
ax3.add_patch(Rectangle((x-30, y-30), 60, 60, edgecolor="red", fill = False))

plt.show()





'''
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
ax2.set_title('Gaussian filter')

ax3.imshow(image_np, cmap=plt.cm.gray)
ax3.autoscale(False)
ax3.plot(coordinates[:, 1], coordinates[:, 0], 'r.')
ax3.axis('off')
ax3.set_title('Peak local max')

print(coordinates)

plt.show()
'''
