import glob

import numpy as np
from scipy import misc

from src import old_functions as track


def process_images():
    x_factor = .25/536
    y_factor = .25/536


    path = 'Z:\\Lab\\Cantilever\\Measurements\\20151117_2DPushing\\2D_stepping_NA0.28\\*.bmp'
    files = glob.glob(path)
    files.sort()
    im_list = list()
    for f in files:
        im_list.append(misc.imread(f, flatten = 1))
    print('finished reading')

    cur_x = 0
    cur_y = 0
    n_list = []
    d_list = []
    offset_x = 0
    offset_y = 0
    image1 = np.array(im_list[0])
    for n in xrange(0, len(im_list) - 1):
        if n % 2 == 0:
            offset_x = cur_x
            offset_y = cur_y
            image1 = np.array(im_list[n])
            print(n)
            print(offset_x)
        n_list.append(n)
        image2 = np.array(im_list[n+1])
        x, y, corr, old_im = track.corr_NVs_no_subset(image1, image2)
        #print(x)
        #print(y)
        #plt.imshow(corr)
        #plt.show()
        cur_x = x * x_factor + offset_x
        cur_y = y * y_factor + offset_y
        d_list.append(np.sqrt(cur_x**2 + cur_y**2))