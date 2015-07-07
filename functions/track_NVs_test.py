from hardware_modules import GalvoMirrors as DaqOut
from functions import ScanAPD
from functions import track_NVs as track
from functions import Focusing as f
from hardware_modules import PiezoController as PC

import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import json

PATH = 'Z:\\Lab\\Cantilever\\Measurements\\150707_NV_Tracking_Test'
TAG = 'TEST_1'
WAIT_TIME = 600
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
    plt.implot(img)
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



roi = {
    "dx": 0.05,
    "dy": 0.05,
    "xPts": 120,
    "xo": 0.0,
    "yPts": 120,
    "yo": 0.0
}

focus_roi = {
    "dx": 0.02,
    "dy": 0.02,
    "xPts": 20,
    "xo": 0.0,
    "yPts": 20,
    "yo": 0.0
}

scanner = ScanAPD.ScanNV(roi['x0']-roi['dx']/2,roi['x0']+roi['dx']/2,roi['xPts'],roi['y0']-roi['dy']/2,roi['y0']+roi['dy']/2,roi['yPts'],.001)
baseline_img = scanner.scan()
setDaqPt(0,0)
writeArray(baseline_img,roi, PATH, TAG)

while True:
    time.sleep(WAIT_TIME)

    scanner = ScanAPD.ScanNV(roi['x0']-roi['dx']/2,roi['x0']+roi['dx']/2,roi['xPts'],roi['y0']-roi['dy']/2,roi['y0']+roi['dy']/2,roi['yPts'],.001)
    new_img = scanner.scan()
    setDaqPt(0,0)

    shift = track.corr_NVs(baseline_img,new_img)
    roi = track.update_roi(roi, shift)
    focus_roi = track.update_roi(focus_roi, shift)

    zController = PC.MDT693A('Z')
    current_focus = zController.getVoltage()
    f.Focus.scan(current_focus - FOCUS_DEVIATION, current_focus + FOCUS_DEVIATION, 40, 'Z', focus_roi)

    scanner = ScanAPD.ScanNV(roi['x0']-roi['dx']/2,roi['x0']+roi['dx']/2,roi['xPts'],roi['y0']-roi['dy']/2,roi['y0']+roi['dy']/2,roi['yPts'],.001)
    new_img2 = scanner.scan()
    setDaqPt(0,0)

    shift2 = track.corr_NVs(baseline_img, new_img2)
    roi = track.update_roi(roi, shift2)
    focus_roi = track.update_roi(focus_roi, shift2)

    scanner = ScanAPD.ScanNV(roi['x0']-roi['dx']/2,roi['x0']+roi['dx']/2,roi['xPts'],roi['y0']-roi['dy']/2,roi['y0']+roi['dy']/2,roi['yPts'],.001)
    shifted_img = scanner.scan()
    setDaqPt(0,0)

    writeArray(shifted_img, roi, PATH, TAG)