import json
import time
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from hardware_modules import GalvoMirrors as DaqOut
from hardware_modules import PiezoController as PC

from src.old_functions import Focusing as f
from src.old_functions import ScanAPD
from src.old_functions import track_NVs as track

"""
Tests track_NVs.py by getting a baseline image, then cycling through waiting, checking shift, refocusing, rechecking
shift, then saving final image to later manually check how it has shifted relative to the initial image and see
how well the correlations work
"""


PATH = 'Z:\\Lab\\Cantilever\\Measurements\\150707_NV_Tracking_Test'
TAG = 'TEST_OVERNIGHT'
WAIT_TIME = 1800
FOCUS_DEVIATION = 5

def writeArray(img, roi, dirpath, tag, columns = None):
    df = pd.DataFrame(img, columns = columns)
    if(columns == None):
        header = False
    else:
        header = True
    start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    filepathCSV = dirpath + "\\" + start_time + '_' + tag + '.csv'
    filepathPNG = dirpath + "\\" + start_time + '_' + tag + '.png'
    df.to_csv(filepathCSV, index = False, header=header)
    plt.imshow(img)
    plt.savefig(str(filepathPNG), format = 'png')

    filepathROI = dirpath + "\\" + start_time + '_' + tag + '.roi'
    with open(filepathROI, 'w') as outfile:
        json.dump(roi, outfile, indent = 4)


def setDaqPt(xVolt,yVolt):
    initPt = np.transpose(np.column_stack((xVolt, yVolt)))
    initPt = (np.repeat(initPt, 2, axis=1))
    # move galvo to first point in line
    pointthread = DaqOut.DaqOutputWave(initPt, 1 / .001, "Dev1/ao0:1")
    pointthread.run()
    pointthread.waitToFinish()
    pointthread.stop()


def run_test():
    roi = {
        "dx": 0.10,
        "dy": 0.10,
        "xPts": 120,
        "xo": 0.0,
        "yPts": 120,
        "yo": 0.0,
        "focus": 36.5
    }

    focus_roi = {
        "dx": 0.02,
        "dy": 0.02,
        "xPts": 20,
        "xo": 0.0,
        "yPts": 20,
        "yo": 0.0
    }

    scanner = ScanAPD.ScanNV(roi['xo'] - roi['dx'] / 2, roi['xo'] + roi['dx'] / 2, roi['xPts'], roi['yo'] - roi['dy'] / 2, roi['yo'] + roi['dy'] / 2, roi['yPts'], .001)
    baseline_img = scanner.scan()
    setDaqPt(0,0)
    writeArray(baseline_img,roi, PATH, TAG)

    while True:
        print("waiting")
        time.sleep(WAIT_TIME)

        print("scanning")
        scanner = ScanAPD.ScanNV(roi['xo'] - roi['dx'] / 2, roi['xo'] + roi['dx'] / 2, roi['xPts'], roi['yo'] - roi['dy'] / 2, roi['yo'] + roi['dy'] / 2, roi['yPts'], .001)
        new_img = scanner.scan()
        setDaqPt(0,0)

        print("correlating")
        shift = track.corr_NVs(baseline_img,new_img)
        roi = track.update_roi(roi, shift)
        focus_roi = track.update_roi(focus_roi, shift)

        print("focusing")
        zController = PC.MDT693A('Z')
        current_focus = zController.getVoltage()
        roi['focus'] = f.Focus.scan(current_focus - FOCUS_DEVIATION, current_focus + FOCUS_DEVIATION, 10, 'Z', scan_range_roi=focus_roi, plotting=False)

        print("scanning2")
        scanner = ScanAPD.ScanNV(roi['xo'] - roi['dx'] / 2, roi['xo'] + roi['dx'] / 2, roi['xPts'], roi['yo'] - roi['dy'] / 2, roi['yo'] + roi['dy'] / 2, roi['yPts'], .001)
        new_img2 = scanner.scan()
        setDaqPt(0,0)

        ("correlating2")
        shift2 = track.corr_NVs(baseline_img, new_img2)
        roi = track.update_roi(roi, shift2)
        focus_roi = track.update_roi(focus_roi, shift2)

        ("scanning3")
        scanner = ScanAPD.ScanNV(roi['xo'] - roi['dx'] / 2, roi['xo'] + roi['dx'] / 2, roi['xPts'], roi['yo'] - roi['dy'] / 2, roi['yo'] + roi['dy'] / 2, roi['yPts'], .001)
        shifted_img = scanner.scan()
        setDaqPt(0,0)

        writeArray(shifted_img, roi, PATH, TAG)

def process_results():
    xarray = []
    yarray = []
    files = [f.split('.dat')[0] for f in listdir(PATH) if isfile(join(PATH, f)) and f.endswith('TEST_OVERNIGHT.roi')]
    for f in files:
        filename = PATH + '\\' + f
        with open(filename, 'r') as infile:
            roi = json.load(infile)
        xarray.append(roi['xo'])
        yarray.append(roi['yo'])
    time = np.linspace(0,26*22,27)
    plt.plot(time, xarray,'k', label = 'x drift')
    plt.plot(time, yarray,'r', label = 'y drift')
    plt.ylim([-.03,.001])
    plt.title('Drift over Time')
    plt.xlabel('time (s)')
    plt.ylabel('drift (V)')
    plt.legend(loc = 'right')
    plt.show()

if __name__ == '__main__':
    process_results()