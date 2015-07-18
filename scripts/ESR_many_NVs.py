from scripts import ESR
from functions import track_NVs as track
from functions import ScanAPD
from hardware_modules import GalvoMirrors as DaqOut

import numpy as np
import matplotlib.pyplot as plt
import functions.ReadWriteCommands as ReadWriteCommands
import json
import os.path

def setDaqPt(xVolt,yVolt):
    initPt = np.transpose(np.column_stack((xVolt, yVolt)))
    initPt = (np.repeat(initPt, 2, axis=1))
    # move galvo to first point in line
    pointthread = DaqOut.DaqOutputWave(initPt, 1 / .001, "Dev1/ao0:1")
    pointthread.run()
    pointthread.waitToFinish()
    pointthread.stop()


def find_NVs(roi):
    scanner = ScanAPD.ScanNV(roi['xo']-roi['dx']/2,roi['xo']+roi['dx']/2,roi['xPts'],roi['yo']-roi['dy']/2,roi['yo']+roi['dy']/2,roi['yPts'],.001)
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
        esr_data, fit_params = ESR.run_esr(RF_Power, test_freqs, (pt[0],pt[1]), num_avg=avg, int_time=.002)
        tag = 'NV{:00d}_RFPower_{:03d}mdB_NumAvrg_{:03d}'.format(pt_num, RF_Power, avg)
        ESR.save_esr(esr_data, dirpath, tag)
        pt_num += 1




def is_ESR_param(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False

    assert 'RF_Power' in json_object.keys()
    assert 'ESR_avg' in json_object.keys()
    assert 'RF_Min' in json_object.keys()
    assert 'RF_Max' in json_object.keys()
    assert 'RF_N_Points' in json_object.keys()
    assert 'ESR_path' in json_object.keys()
    assert 'ESR_tag' in json_object.keys()
    assert 'ESR_integration_time' in json_object.keys()


    return True


def ESR_load_param(filename_or_json):
    '''
    loads esr parameter from json file
    '''

    esr_param = {}
    # check if input is path to json file or dictionary itself
    if os.path.isfile(filename_or_json):
        esr_param = ReadWriteCommands.load_json(filename_or_json)
    elif is_ESR_param(filename_or_json):
        esr_param = json.loads(filename_or_json)

    else:
        raise ValueError('ESR: no valid parameter filename or dictionary')

    return esr_param

def ESR_map(points, esr_param):
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
    for pt in points:

        print '{:s}_NV_pt_{:00d}'.format(tag, pt_num)
        esr_data, fit_params, fig = ESR.run_esr(RF_Power, freqs, (pt[0],pt[1]), num_avg=avg, int_time=int_time)
        print pt_num
        print fig
        ESR.save_esr(esr_data, fig, dirpath, '{:s}_NV_pt_{:00d}'.format(tag, pt_num))


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