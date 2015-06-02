import numpy

# import ScanDelay as GalvoScan  # for APD counting input
from functions import ScanAPD
from functions import ScanPhotodiode_DAQ as ScanPhotodiode
from hardware_modules import GalvoMirrors as DaqOut, ZiControl
from PyQt4 import QtGui


def ZIGui(canvas, amp, offset, freqLow, freqHigh, sampleNum, samplePerPt, xScale):
    zi = ZiControl.ZIHF2(amp, offset, canvas = canvas)
    data = zi.sweep(freqLow, freqHigh, sampleNum, samplePerPt, xScale=0)
    return data

def scanGui(canvas, xVmin, xVmax, xPts, yVmin, yVmax,yPts, timePerPt, queue, APD = True):
    if(APD):
        scanner = ScanAPD.ScanNV(xVmin,xVmax,xPts,yVmin,yVmax,yPts,timePerPt, canvas = canvas)
    else:
        scanner = ScanPhotodiode.ScanNV(xVmin,xVmax,xPts,yVmin,yVmax,yPts,timePerPt, canvas = canvas)
    imageData = scanner.scan(queue = queue)
    setDaqPt(0,0)
    return imageData

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

