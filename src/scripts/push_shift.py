import glob

import matplotlib.pyplot  as plt
import numpy as np
import pandas as pd
import scipy.optimize
from helper_functions import reading_writing as rw

from src import functions as track


def process_images():
    xVmin = -0.0805
    yVmin = -0.0730
    xVmax = -0.0399
    yVmax = -0.0317
    x_factor = (xVmax-xVmin)/120
    y_factor = (yVmax-yVmin)/120
    print(x_factor)
    print(y_factor)


    path = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\Run4\\*.csv'
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

    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\Run4'
    tag = 'processed'
    rw.save_data([n_list, d_list], dirpath, tag)

    plt.plot(n_list, d_list)
    plt.show()

def fit_plot():
    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run3\\2015-08-10_15-38-53-processed.csv'
    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run3\\2015-08-10_15-38-53-processed.csv'
    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run3\\2015-08-10_15-38-53-processed.csv'
    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run4\\2015-08-11_18-41-56-processed.csv'

    df = pd.read_csv(dirpath, header = -1)
    num = df._probes[0][0:20]
    dist = df._probes[1][0:20] / .1 * 5

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
    dirpath = ['Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run2\\2015-08-10_15-00-29-processed.csv', 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run1\\2015-08-10_14-05-45-processed.csv', 'Z:\\Lab\\Cantilever\\Measurements\\20150806_PushingDiamonds\\run3\\2015-08-07_14-01-48-processed.csv', 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run3\\2015-08-10_15-38-53-processed.csv', 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds\\run4\\2015-08-11_18-41-56-processed.csv']
    index_array = [0.01, .02, .05, .1, 1]
    color_array_pts = ['b.','g.','r.','k.','m.']
    color_array_line = ['b-','g-','r-','k-','m-']


    for idx, f in enumerate(dirpath):
        min_val = 1/index_array[idx]
        max_val = 10/index_array[idx]
        df = pd.read_csv(f, header = -1)
        num = df._probes[0][min_val:max_val + 1] * index_array[idx]
        dist = df._probes[1][min_val - 1:max_val] / .1 * 5

        def linear(x, a, b):
            return a*x + b

        (a_fit, b_fit), pcov = scipy.optimize.curve_fit(linear, num, dist, p0=[.001, 0])

        plt.plot(num, dist, color_array_pts[idx], label = str(index_array[idx]) + 'V')
        plt.plot(num, linear(num, a_fit, b_fit), color_array_line[idx])

    plt.xlabel('Distance (V)')
    plt.ylabel('Shift (um)')
    plt.legend(bbox_to_anchor=(1, .5))
    plt.show()

if __name__ == '__main__':
    #process_images()
    fit_all_plots()
