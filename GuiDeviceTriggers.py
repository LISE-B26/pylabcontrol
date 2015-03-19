import numpy
import ZiControl
import ScanTest as GalvoScan
import GalvoTest as DaqOut
from PyQt4 import QtGui

class DeviceTriggers():
    @staticmethod
    #def ZIGui(canvas):
    def ZIGui(canvas, amp, offset, freqLow, freqHigh, sampleNum, samplePerPt, xScale):
        zi = ZiControl.ZIHF2(amp, offset, canvas = canvas)
        data = zi.sweep(freqLow, freqHigh, sampleNum, samplePerPt, xScale=0)
        return data

    @staticmethod
    def scanGui(canvas, xVmin, xVmax, xPts, yVmin, yVmax,yPts, timePerPt):
        scanner = GalvoScan.ScanNV(xVmin,xVmax,xPts,yVmin,yVmax,yPts,timePerPt, canvas = canvas)
        imageData = scanner.scan()
        return imageData

    @staticmethod
    def setDaqPt(xVolt,yVolt):
        pt = numpy.transpose(numpy.column_stack((xVolt,yVolt)))
        pt = (numpy.repeat(pt, 2, axis=1))
        # prefacing string with b should do nothing in python 2, but otherwise this doesn't work
        pointthread = DaqOut.DaqOutputWave(pt, 1000.0, b"Dev1/ao0:1")
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()
        QtGui.QApplication.processEvents()

