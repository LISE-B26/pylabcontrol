import json
import os.path
import time

import src.old_helper_functions.reading_writing as ReadWriteCommands
import src.old_helper_functions.test_types as test_types
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.old_scripts import ESR
from src.old_functions import track_NVs as track
from src.old_functions import ScanAPD
from src.old_hardware_modules import GalvoMirrors as DaqOut
from src.old_hardware_modules import PiezoController as PC

from src.old_functions import Focusing as F
from src.old_functions import ScanAPD
from src.old_functions import regions
from src.old_functions import track_NVs as track
from src.old_scripts import ESR


def setDaqPt(xVolt,yVolt):
    initPt = np.transpose(np.column_stack((xVolt, yVolt)))
    initPt = (np.repeat(initPt, 2, axis=1))
    # move galvo to first point in line
    pointthread = DaqOut.DaqOutputWave(initPt, 1 / .001, "Dev1/ao0:1")
    pointthread.run()
    pointthread.waitToFinish()
    pointthread.stop()


def find_NVs(roi):
    scanner = ScanAPD.ScanNV(roi['xo'] - roi['dx'] / 2, roi['xo'] + roi['dx'] / 2, roi['xPts'], roi['yo'] - roi['dy'] / 2, roi['yo'] + roi['dy'] / 2, roi['yPts'], .001)
    img = scanner.scan()
    setDaqPt(0,0)

    coor = track.locate_NVs(img, roi['dx'])
    print(coor)
    plt.imshow(img, cmap=plt.cm.gray)
    plt.autoscale(False)
    plt.plot(coor[:, 1], coor[:, 0], 'r.')
    plt.show()


def ESR_NVs(coor):
    RF_Power = -12
    avg = 50
    test_freqs = np.linspace(2820000000, 2920000000, 200)
    dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150707_Diamond_Ramp_Over_Mags'
    pt_num = 1
    for pt in coor:
        esr_data, fit_params = ESR.run_esr(RF_Power, test_freqs, (pt[0], pt[1]), num_avg=avg, int_time=.002)
        tag = 'NV{:00d}_RFPower_{:03d}mdB_NumAvrg_{:03d}'.format(pt_num, RF_Power, avg)
        ESR.save_esr(esr_data, dirpath, tag)
        pt_num += 1







def ESR_load_param(filename_or_json):
    '''
    loads esr parameter from json file
    '''

    esr_param = {}
    # check if input is path to json file or dictionary itself
    if os.path.isfile(filename_or_json):
        esr_param = ReadWriteCommands.load_json(filename_or_json)
    elif test_types.is_ESR_param(filename_or_json):
        esr_param = json.loads(filename_or_json)

    else:
        raise ValueError('AF: no valid parameter filename or dictionary')
        print 'no valid parameter filename or dictionary'

    return esr_param

def ESR_map(points, esr_param, canvas, queue = None):
    '''
        gets the ESR at points defined by points
    '''
    print esr_param
    RF_Power = float(esr_param['RF_Power'])
    avg = int(esr_param['ESR_avg'])
    freqs = np.linspace(int(esr_param['RF_Min']), int(esr_param['RF_Max']), int(esr_param['RF_N_Points']))

    dirpath = esr_param['ESR_path']
    tag = esr_param['ESR_tag']
    int_time = esr_param['ESR_integration_time']

    pt_num = 1
    print dirpath
    print(points)
    for pt in points:

        print '{:s}_NV_pt_{:00d}'.format(tag, pt_num)
        esr_data, fit_params, fig = ESR.run_esr(RF_Power, freqs, (pt[0], pt[1]), num_avg=avg, int_time=int_time, canvas = canvas, queue = queue)
        print pt_num
        ESR.save_esr(esr_data, fig, dirpath, '{:s}_NV_pt_{:00d}'.format(tag, pt_num))


        pt_num += 1
    #fig.clf()

def ESR_map_focus(points, roi, esr_param, canvas):
    '''
        gets the ESR at points defined by points
    '''
    print esr_param
    RF_Power = float(esr_param['RF_Power'])
    avg = int(esr_param['ESR_avg'])
    freqs = np.linspace(int(esr_param['RF_Min']), int(esr_param['RF_Max']), int(esr_param['RF_N_Points']))

    dirpath = esr_param['ESR_path']
    tag = esr_param['ESR_tag']
    int_time = esr_param['ESR_integration_time']
    runs_between_focusing = esr_param['runs_between_focusing']

    current_focus = PC.MDT693B('Z').getVoltage()

    start_time = time.strftime("%Y-%m-%d_%H-%M-%S")

    'save points'
    df = pd.DataFrame(points)
    df.to_csv(dirpath + "\\" + start_time + '_' + tag + '_points.csv', index = False, header=False)
    'save roi'
    ReadWriteCommands.save_json(roi, filename =  dirpath + "\\" + start_time + '_' + tag + '_roi.json')
    'save esr_param'
    ReadWriteCommands.save_json(esr_param, filename =  dirpath + "\\" + start_time + '_' + tag + '_esr_param.json')

    pt_num = 1
    print dirpath
    for pt in points:

        print '{:s}_NV_pt_{:00d}'.format(tag, pt_num)
        esr_data, fit_params, fig = ESR.run_esr(RF_Power, freqs, (pt[0], pt[1]), num_avg=avg, int_time=int_time, canvas = canvas)
        print pt_num
        print fig
        ESR.save_esr(esr_data, fig, dirpath, '{:s}_NV_pt_{:00d}'.format(tag, pt_num))
        if ((pt_num % runs_between_focusing) == 0):


            roi['xPts'] = 40
            roi['yPts'] = 40

            current_focus, voltRange, ydata = F.Focus.scan(current_focus - 3, current_focus + 3, 18, 'Z', waitTime = 1, scan_range_roi = roi, blocking = False, return_data = True)
            filepathCSV = dirpath + "\\" + start_time + '_' + tag + '_af.csv'
            df = pd.DataFrame([voltRange, ydata])
            df.to_csv(filepathCSV, index = False, header=False)

            xMin, xMax, yMin, yMax = regions.roi_to_min_max(roi)
            scanner = ScanAPD.ScanNV(xMin, xMax, 120, yMin, yMax, 120, .001)
            image_data = scanner.scan(queue = None)
            plt.close()
            implot = plt.imshow(image_data, interpolation="nearest", extent = [xMin, xMax, yMin, yMax])
            implot.set_cmap('pink')
            plt.colorbar()

            filepathPNG = dirpath + "\\" + start_time + '_' + tag + '.png'
            plt.savefig(filepathPNG, format='png')
            df = pd.DataFrame(image_data)
            filepathCSV = dirpath + "\\" + start_time + '_' + tag + '.csv'
            df.to_csv(filepathCSV, index = False, header=False)
        pt_num += 1
    fig.clf()


# roi = {
#     "dx": 0.10,
#     "dy": 0.10,
#     "xPts": 120,
#     "xo": 0.0,
#     "yPts": 120,
#     "yo": 0.0,
# }
# #find_NVs(roi)
#
# img = np.zeros((120,120))
# coor = np.array([[ 14,  65], [ 60,  60]], dtype = float)
# coor_v = track.pixel_to_voltage(coor, img, roi)
# print(coor_v)
# ESR_NVs(coor_v)