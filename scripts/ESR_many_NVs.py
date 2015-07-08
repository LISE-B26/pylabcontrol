from scripts import ESR
from functions import track_NVs as track
from functions import ScanAPD
from hardware_modules import GalvoMirrors as DaqOut

import numpy as np
import matplotlib.pyplot as plt

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

roi = {
    "dx": 0.10,
    "dy": 0.10,
    "xPts": 120,
    "xo": 0.0,
    "yPts": 120,
    "yo": 0.0,
}
#find_NVs(roi)

img = np.zeros((120,120))
coor = np.array([[ 14,  65], [ 60,  60]], dtype = float)
coor_v = track.pixel_to_voltage(coor, img, roi)
print(coor_v)
ESR_NVs(coor_v)