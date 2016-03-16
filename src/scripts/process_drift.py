import glob

import matplotlib.pyplot  as plt
import numpy as np
import pandas as pd
import scipy.optimize
from helper_functions import reading_writing as rw

from src import functions as track


def process_images():
    xVmin = 0.0138
    yVmin = -0.1108
    xVmax = 0.0380
    yVmax = -0.0854
    x_factor = (xVmax-xVmin)/120
    y_factor = (yVmax-yVmin)/120

    path = 'Z:\\Lab\\Cantilever\\Measurements\\20150828_RFDrift\\16dBm\\*.csv'
    files = glob.glob(path)
    files.sort()
    im_list = list()
    for f in files:
        im_list.append(pd.read_csv(f, header=-1))
    print('finished reading')

    cur_x = 0
    cur_y = 0
    n_list = []
    d_list = []
    offset_x = 0
    offset_y = 0
    image1 = np.array(im_list[0])
    for n in xrange(0, len(im_list) - 1):
        if n % 5 == 0:
            #offset_x = cur_x
            #offset_y = cur_y
            #image1 = np.array(im_list[n])
            print(n)
            #print(offset_x)
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

    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150828_RFDrift\\16dBm'
    tag = 'processed'
    rw.save_data([n_list, d_list], dirpath, tag)

    plt.plot(n_list, d_list)
    plt.show()

def fit_plot():
    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run3\\2015-08-10_15-38-53-processed.csv'
    #dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run3\\2015-08-10_15-38-53-processed.csv'
    #dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run3\\2015-08-10_15-38-53-processed.csv'
    #dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run4\\2015-08-11_18-41-56-processed.csv'

    df = pd.read_csv(dirpath, header = -1)
    num = df.values[0][0:20]
    dist = df.values[1][0:20]/.1*5

    def linear(x, a, b):
        return a*x + b

    (a_fit, b_fit), pcov = scipy.optimize.curve_fit(linear, num, dist, p0=[.001, 0])
    err = np.sqrt(np.diag(pcov))
    print('Slope: {:0.9f} +- {:0.9f}'.format(a_fit, err[0]))
    print('Intercept: {:0.9f} +- {:0.9f}'.format(b_fit, err[1]))
    residual = dist - linear(num, a_fit, b_fit)
    print('Max deviation: ' + str(np.max(np.abs(residual))))

    plt.plot(num, dist, 'b.', num, linear(num, a_fit, b_fit), 'g-')
    plt.xlabel('Steps')
    plt.ylabel('Shift (um)')

    #plt.plot(num, residual)
    #plt.xlabel('Steps')
    #plt.ylabel('Residual (um)')



    fig_x = plt.figure()
    plt.hist(np.diff(dist), 10)
    plt.xlabel('Distance Per Push (um)')
    plt.ylabel('Number of Pushes')
    print(np.mean(np.diff(dist)))
    plt.show()

def fit_all_plots():
    dirpath = ['Z:\\Lab\\Cantilever\\Measurements\\20150828_RFDrift\\1dBm\\2015-09-04_11-11-26-processed.csv', 'Z:\\Lab\\Cantilever\\Measurements\\20150828_RFDrift\\11dBm\\2015-09-04_11-13-34-processed.csv', 'Z:\\Lab\\Cantilever\\Measurements\\20150828_RFDrift\\16dBm\\2015-09-04_11-16-10-processed.csv']
    index_array = [1, 11, 16]
    color_array_pts = ['b.','g.','r.']


    for idx, f in enumerate(dirpath):
        df = pd.read_csv(f, header = -1)
        num = (df.values[0][0:30] + 1)*35
        dist = df.values[1][0:30]
        np.insert(num,0,0)
        np.insert(dist,0,0)

        plt.plot(num, dist, color_array_pts[idx], label = str(index_array[idx]) + 'dBm')

    plt.xlabel('Time (s)')
    plt.ylabel('Shift (um)')
    plt.legend(bbox_to_anchor=(1, .5))
    plt.show()

#process_images()
fit_all_plots()
