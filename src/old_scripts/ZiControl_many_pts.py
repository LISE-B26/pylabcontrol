import json
import os.path
import time

import src.old_helper_functions.reading_writing as ReadWriteCommands
import src.old_helper_functions.test_types as test_types
import matplotlib.pyplot as plt
import pandas as pd
from src.old_hardware_modules import PiezoController as PC
from src.old_hardware_modules import ZiControl as ZC

from src.old_functions import Focusing as F
from src.old_functions import ScanAPD
from src.old_functions import regions


def ZI_map(points, ZI_param, canvas):
    '''
        gets the ESR at points defined by points
    '''
    print ZI_param
    amp = float(ZI_param['Amplitude'])
    offset = int(ZI_param['Offset'])
    freq_low = int(ZI_param['Minimum Frequency'])
    freq_high = int(ZI_param['Maximum Frequency'])
    sample_num = int(ZI_param['Number of Samples'])
    ave_per_pt = int(ZI_param['Averages Per Point'])
    x_scale = int(ZI_param['Log Scale'])

    dirpath = ZI_param['ZI_path']
    tag = ZI_param['ZI_tag']

    pt_num = 1
    print dirpath
    for pt in points:

        print '{:s}_pt_{:00d}'.format(tag, pt_num)
        zi = ZC.ZIHF2(amp, offset, freq_low, canvas = canvas)
        ZI_data, fig = zi.sweep(freq_low, freq_high, sample_num, ave_per_pt, xScale = x_scale)
        zi.save_ZI(ZI_data, fig, dirpath, tag = '{:s}_pt_{:00d}'.format(tag, pt_num))

        pt_num += 1
    #fig.clf()

def ZI_map_focus(points, roi, ZI_param, canvas):
    '''
        gets the ESR at points defined by points
    '''
    print ZI_param
    amp = float(ZI_param['Amplitude'])
    offset = int(ZI_param['Offset'])
    freq_low = int(ZI_param['Minimum Frequency'])
    freq_high = int(ZI_param['Maximum Frequency'])
    sample_num = int(ZI_param['Number of Samples'])
    ave_per_pt = int(ZI_param['Averages Per Point'])
    x_scale = int(ZI_param['Log Scale'])
    runs_between_focusing = ZI_param['runs_between_focusing']

    dirpath = ZI_param['ZI_path']
    tag = ZI_param['ZI_tag']

    current_focus = PC.MDT693B('X').getVoltage()

    start_time = time.strftime("%Y-%m-%d_%H-%M-%S")

    'save points'
    df = pd.DataFrame(points)
    df.to_csv(dirpath + "\\" + start_time + '_' + tag + '_points.csv', index = False, header=False)
    'save roi'
    ReadWriteCommands.save_json(roi, filename =  dirpath + "\\" + start_time + '_' + tag + '_roi.json')
    'save esr_param'
    ReadWriteCommands.save_json(ZI_param, filename =  dirpath + "\\" + start_time + '_' + tag + '_esr_param.json')

    pt_num = 1
    print dirpath
    for pt in points:

        print '{:s}_NV_pt_{:00d}'.format(tag, pt_num)
        zi = ZC.ZIHF2(amp, offset, freq_low, canvas = canvas)
        ZI_data, fig = zi.sweep(freq_low, freq_high, sample_num, ave_per_pt, xScale = x_scale)
        zi.save_ZI(ZI_data, fig, dirpath, '{:s}_pt_{:00d}'.format(tag, pt_num))
        print pt_num
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

def ZI_load_param(filename_or_json):
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