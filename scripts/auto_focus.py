__author__ = 'Experiment'

import json
import os.path
import numpy as np

import functions.Focusing as focusing
import helper_functions.reading_writing as ReadWriteCommands
import helper_functions.test_types as test_types
import hardware_modules.GalvoMirrors as DaqOut
import pandas as pd
import time

def AF_load_param(filename_or_json):
    '''
    loads af parameter from json file
    '''
    filename_or_json = str(filename_or_json)

    af_param = {}
    # check if input is path to json file or dictionary itself
    if os.path.isfile(filename_or_json):
        af_param = ReadWriteCommands.load_json(filename_or_json)
    elif test_types.is_autofocus_param(filename_or_json):
        af_param = json.loads(filename_or_json)

    else:
        raise ValueError('AF: no valid parameter filename or dictionary')

    return af_param

def AF_load_param_grid(filename_or_json):
    '''
    loads af parameter from json file
    '''
    filename_or_json = str(filename_or_json)

    af_param = {}
    # check if input is path to json file or dictionary itself
    if os.path.isfile(filename_or_json):
        af_param = ReadWriteCommands.load_json(filename_or_json)
    else:
        af_param = json.loads(filename_or_json)

    return af_param


def autofocus_RoI(af_parameter, roi_focus, axis, focPlot = None, return_data = False, queue = None):

    zo = float(af_parameter['zo'])
    dz = float(af_parameter['dz'])
    zPts = float(af_parameter['zPts'])
    xyPts = float(af_parameter['xyPts'])
    # axis = str(af_parameter['axis'])
    #axis = 'Z'

    zMin, zMax = zo - dz/2., zo + dz/2.
    roi_focus['xPts'] = xyPts
    roi_focus['yPts'] = xyPts
    print roi_focus
    voltage_focus, voltage_range, y_data = focusing.Focus.scan(zMin, zMax, zPts, axis, waitTime = .1, APD=True, scan_range_roi = roi_focus, canvas = focPlot, return_data=True, queue = queue)

    if return_data:
        return voltage_focus, voltage_range, y_data
    else:
        return voltage_focus

def autofocus_RoI_attocube(af_parameter, roi_focus, focPlot = None, return_data = False, queue = None):

    min_pos = float(af_parameter['min_pos'])
    max_pos = float(af_parameter['max_pos'])
    center_position = float(af_parameter['center_position'])
    max_deviation = float(af_parameter['max_deviation'])
    cont_voltage = float(af_parameter['cont_voltage'])
    step_voltage = float(af_parameter['step_voltage'])
    atto_frequency = float(af_parameter['atto_frequency'])
    xyPts = float(af_parameter['xyPts'])


    roi_focus['xPts'] = xyPts
    roi_focus['yPts'] = xyPts
    print roi_focus
    pos_focus, xdata, y_data = focusing.Focus.scan_attocube(min_pos, max_pos, center_position, max_deviation, cont_voltage = cont_voltage, step_voltage=step_voltage, atto_frequency = atto_frequency, waitTime = .1, APD=True, scan_range_roi = roi_focus, canvas = focPlot, return_data=True, queue = queue)

    if return_data:
        return pos_focus, xdata, y_data
    else:
        return pos_focus

def autofocus_RoI_mean(af_parameter, roi_focus, axis, focPlot = None, return_data = False, queue = None):

    zo = float(af_parameter['zo'])
    dz = float(af_parameter['dz'])
    zPts = float(af_parameter['zPts'])
    xyPts = float(af_parameter['xyPts'])
    # axis = str(af_parameter['axis'])
    #axis = 'Z'

    zMin, zMax = zo - dz/2., zo + dz/2.
    roi_focus['xPts'] = xyPts
    roi_focus['yPts'] = xyPts
    print roi_focus
    voltage_focus, voltage_range, y_data = focusing.Focus.scan(zMin, zMax, zPts, axis, waitTime = .1, APD=True, scan_range_roi = roi_focus, canvas = focPlot, return_data=True, queue = queue, std = False)

    if return_data:
        return voltage_focus, voltage_range, y_data
    else:
        return voltage_focus

def autofocus_ROI_mean_map(points, af_parameter, roi_focus, axis, focPlot = None, return_data = False, queue = None, imPlot = None):
    '''
    '''
    zo = float(af_parameter['zo'])
    dz = float(af_parameter['dz'])
    zPts = float(af_parameter['zPts'])
    time_per_pt = float(af_parameter['time_per_pt'])
    zMin, zMax = zo - dz/2., zo + dz/2.

    dirpath = af_parameter['AF_path']
    tag = af_parameter['AF_tag']

    if not imPlot == None:
        ReadWriteCommands.save_image(imPlot.fig, dirpath, tag)

    pt_num = 1
    for pt in points:
        scan_range_roi = {
            "dx": 0,
            "dy": 0,
            "xPts": 1,
            "xo": pt[0],
            "yPts": 1,
            "yo": pt[1]
        }
        print '{:s}_pt_{:00d}'.format(tag, pt_num)
        voltage_focus, voltage_range, y_data = focusing.Focus.scan(zMin, zMax, zPts, axis, waitTime = .1, APD=True, scan_range_roi = scan_range_roi, canvas = focPlot, return_data=True, queue = queue, std = False, timePerPt=time_per_pt)
        print pt_num
        save_focus(np.array((voltage_range,y_data)), dirpath, '{:s}_pt_{:00d}'.format(tag, pt_num), fig = focPlot.fig)

        pt_num += 1
    #fig.clf()

def move_to_pt((pt_x,pt_y)):
    if(abs(pt_x) > .5 or abs(pt_y) > .5):
        raise ValueError("Invalid nv coordinate, galvo voltages must not exceed +- .5 V")
    initPt = np.transpose(np.column_stack((pt_x,pt_y)))
    initPt = (np.repeat(initPt, 2, axis=1))
    # move galvo to first point in line
    pointthread = DaqOut.DaqOutputWave(initPt, 1 / .001, "Dev1/ao0:1")
    pointthread.run()
    pointthread.waitToFinish()
    pointthread.stop()

def save_focus(af_data, dirpath, tag, fig = None):
    df = pd.DataFrame(af_data)
    start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    filepathCSV = dirpath + "\\" + start_time + '_' + tag + '.csv'
    df.to_csv(filepathCSV)
    filepathPNG = dirpath + "\\" + start_time + '_' + tag + '.png'


    if (fig == None) == False:
        fig.savefig(filepathPNG, format='png')