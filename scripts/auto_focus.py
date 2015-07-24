__author__ = 'Experiment'

import json
import os.path

import functions.Focusing as focusing
import helper_functions.reading_writing as ReadWriteCommands
import helper_functions.test_types as test_types


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


def autofocus_RoI(af_parameter, roi_focus):

    zo = float(af_parameter['zo'])
    dz = float(af_parameter['dz'])
    zPts = float(af_parameter['zPts'])
    xyPts = float(af_parameter['xyPts'])

    zMin, zMax = zo - dz/2., zo + dz/2.
    roi_focus['xPts'] = xyPts
    roi_focus['yPts'] = xyPts
    print roi_focus
    voltage_focus = focusing.Focus.scan(zMin, zMax, zPts, 'Z', waitTime = .1, APD=True, scan_range_roi = roi_focus)

    return voltage_focus