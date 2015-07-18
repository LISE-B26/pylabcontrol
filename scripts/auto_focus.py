__author__ = 'Experiment'

import functions.Focusing as focusing
import functions.ReadWriteCommands as ReadWriteCommands


def AF_load_param(filename):
    '''
    loads af parameter from json file
    need to add assert functions here!!
    '''
    af_param = ReadWriteCommands.load_json(filename)

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