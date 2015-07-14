from scripts import ESR
import numpy as np

import json
import time
from functions import Focusing

import matplotlib.pyplot as plt

from  hardware_modules.GalvoMirrors import SetGalvoPoint

def get_points_on_a_grid(pos_left_bottom, pos_right_top, xpts, ypts):
    dx = 1.*(pos_right_top[0] - pos_left_bottom[0]) / (xpts - 1)
    dy = 1.*(pos_right_top[1] - pos_left_bottom[1]) / (ypts - 1)
    print dx, dy
    xy = np.zeros([xpts, ypts, 2])

    for ix in np.arange(xpts):
        for iy in np.arange(xpts):
            xy[ix, iy] = pos_left_bottom[0] + 1.*ix * dx, pos_left_bottom[1] + iy * dy


    return xy.reshape(xpts * ypts,2)


# #####################################################################################################
# script begins
#######################################################################################################
DIR_PATH = 'Z:/Lab/Cantilever/Measurements/20150713_Diamond_Ramp_Over_Mags/ESR_Map/'
TAG = 'Co'

ROI = {
        "xo": 0.23, 'yo': -0.22,
        "dx": 0.05, 'dy': 0.05,
        'xPts': 101, 'yPts': 101
    }


ROI_Focus = {
        "xo": 0.26, 'yo': -0.22,
        "dx": 0.015, 'dy': 0.015,
        'xPts': 20, 'yPts': 20
    }


ESR_grid_points = get_points_on_a_grid([0.21, -0.24], [0.25, -0.20], 10, 10)

RF_Power = -12
avg = 200
test_freqs = np.linspace(2820000000, 2920000000, 200)


zo = float(46)
dz = float(5)
zPts = float(10)
zMin, zMax = zo - dz/2., zo + dz/2.



for xy in ESR_grid_points:

#     for y_offset in y_offsets:
#         for x_offset in x_offsets:
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    # set laser
    ROI.update({'x_laser':xy[0], 'y_laser': xy[1]})
    SetGalvoPoint(ROI['x_laser'], ROI['y_laser'])



    # run ESR
    esr_data, fit_params, fig = ESR.run_esr(RF_Power, test_freqs, num_avg=avg, int_time=.002)

    # save
    tag = 'NV1_RFPower_{:03d}mdB_NumAvrg_{:03d}_xL_{:00.3f}_xL_{:00.3f}V'.format(RF_Power, avg, ROI['x_laser'], ROI['y_laser'])

    print('saving ESR spectrum {:s} '.format(tag))
    ESR.save_esr(esr_data, fig, DIR_PATH, tag)

    full_filename = '{:s}/{:s}_{:s}'.format(DIR_PATH, start_time, tag)
    with open('{:s}.roi'.format(full_filename), 'w') as outfile:
        json.dump(ROI, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

    plt.close()


    # refocus
    voltage_focus = Focusing.Focus.scan(zMin, zMax, zPts, 'Z', waitTime = .1, APD=True, scan_range_roi = ROI_Focus, blocking = False)
    plt.close()



