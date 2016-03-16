import numpy

# import ScanDelay as GalvoScan  # for APD counting input
from src.functions import ScanAPD
from src.functions import ScanPhotodiode_DAQ as ScanPhotodiode
from src.hardware_modules import GalvoMirrors as DaqOut
from src.hardware_modules import ZiControl
#from scripts.ESR import run_esr
from PyQt4 import QtGui


def ZIGui(canvas, amp, offset, freqLow, freqHigh, sampleNum, samplePerPt, xScale):
    zi = ZiControl.ZIHF2(amp, offset, canvas = canvas)
    data = zi.sweep(freqLow, freqHigh, sampleNum, samplePerPt, xScale=0)
    return data

def scanGui(canvas, xVmin, xVmax, xPts, yVmin, yVmax,yPts, timePerPt, queue = None, APD = True, dist_volt_conv = None):
    if(APD):
        scanner = ScanAPD.ScanNV(xVmin, xVmax, xPts, yVmin, yVmax, yPts, timePerPt, canvas = canvas, dist_volt_conversion = dist_volt_conv)
    else:
        scanner = ScanPhotodiode.ScanNV(xVmin,xVmax,xPts,yVmin,yVmax,yPts,timePerPt, canvas = canvas)
    imageData = scanner.scan(queue = queue)
    setDaqPt(0,0)
    imageRoI = {
    "dx": xVmax-xVmin,
    "dy": yVmax-yVmin,
    "xPts": xPts,
    "xo": (xVmax+xVmin)/2,
    "yPts": yPts,
    "yo": (yVmax+yVmin)/2
}
    return imageData, imageRoI

def updateColorbar(imageData, canvas, extent, cmax):
    ScanAPD.ScanNV.updateColorbar(imageData, canvas, extent, cmax)

def setDaqPt(xVolt,yVolt):
    initPt = numpy.transpose(numpy.column_stack((xVolt, yVolt)))
    initPt = (numpy.repeat(initPt, 2, axis=1))
    # move galvo to first point in line
    pointthread = DaqOut.DaqOutputWave(initPt, 1 / .001, "Dev1/ao0:1")
    pointthread.run()
    pointthread.waitToFinish()
    pointthread.stop()
    QtGui.QApplication.processEvents()

def runESR(rf_power, minFreq, maxFreq, numPts):
    #freq_values = numpy.linspace(minFreq, maxFreq, numPts)
    #run_esr(rf_power, freq_values)
    print("Functionality Not Yet Implemented")