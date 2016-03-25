# B26 Lab Code
# Last Update: 4/14/15

# External Connections: Galvo x axis on DAQ channel 0
#                       Galvo y axis on DAQ channel 1
#                       APD input to counter 0 (PFI8)
#                       No external connection to counter 1 out (PFI13)


# import external files
import hardware_modules.GalvoMirrors as DaqOut

from src.old_hardware_modules import APD as APDIn
# import standard libraries
import numpy
import matplotlib.pyplot
from PyQt4 import QtGui


# This class controls the galvo and APD to run an NV scan, and displays the
# image. The scan is performed line by line in the x direction.
class ScanNV():
    # initializes values
    # xVmin: minimum x voltage for scan
    # xVmax: maximum x voltage for scan
    # xPts: number of x points to scan
    # yVmin: minimum y voltage for scan
    # yVmax: maximum y voltage for scan
    # yPts: number of y points to scan
    # timePerPt: time to stay at each scan point
    # canvas: send matplotlib.backends canvas from PyQt4 old_gui if being used, otherwise plots with pyplot
    # settleTime: galvo settling time, excluded from scan
    # dist_volt_conversion: conversion factor of number of microns per galvo volt
    def __init__(self, xVmin, xVmax, xPts, yVmin, yVmax, yPts, timePerPt, canvas = None, settleTime = .0002, dist_volt_conversion = None):
        # evenly spaced arrays of x and y voltages
        assert((timePerPt/settleTime).is_integer())
        self.xVmin = xVmin
        self.xVmax = xVmax
        self.yVmin = yVmin
        self.yVmax = yVmax
        self.settleTime = settleTime
        self.timePerPt = timePerPt
        self.clockAdjust = int((timePerPt+settleTime)/settleTime)
        self.xArray = numpy.linspace(xVmin, xVmax, xPts)
        self.yArray = numpy.linspace(yVmin, yVmax, yPts)
        self.xArray = numpy.repeat(self.xArray, self.clockAdjust)
        self.imageData = numpy.zeros((yPts,xPts))
        self.dt = (timePerPt+settleTime)/self.clockAdjust
        # stores one line of x data at a time
        self.xLineData = numpy.zeros(len(self.xArray) + 1)
        self.plotting = 0
        self.canvas = canvas
        self.cbar = None
        if dist_volt_conversion is None:
            self.dvconv = None
        else:
            self.dvconv = float(dist_volt_conversion)

    # runs scan
    def scan(self,queue = None):
        # scan one x line per loop
        for yNum in xrange(0, len(self.yArray)):
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                break
            # initialize APD thread
            readthread = APDIn.ReadAPD("Dev1/ctr0", 1 / self.dt,
                                       len(self.xArray) + 1)
            self.initPt = numpy.transpose(numpy.column_stack((self.xArray[0],
                                          self.yArray[yNum])))
            self.initPt = (numpy.repeat(self.initPt, 2, axis=1))
            # move galvo to first point in line
            pointthread = DaqOut.DaqOutputWave(self.initPt, 1 / self.dt, "Dev1/ao0:1")
            pointthread.run()
            pointthread.waitToFinish()
            pointthread.stop()
            writethread = DaqOut.DaqOutputWave(self.xArray, 1 / self.dt,
                                               "Dev1/ao0")
            # start counter and scanning sequence
            readthread.runCtr()
            writethread.run()
            writethread.waitToFinish()
            writethread.stop()
            self.xLineData,_ = readthread.read()
            self.diffData = numpy.diff(self.xLineData)
            self.summedData = numpy.zeros(len(self.xArray)/self.clockAdjust)
            for i in range(0,int((len(self.xArray)/self.clockAdjust))):
                self.summedData[i] = numpy.sum(self.diffData[(i*self.clockAdjust+1):(i*self.clockAdjust+self.clockAdjust-1)])
            #also normalizing to kcounts/sec
            self.imageData[yNum] = self.summedData*(.001/self.timePerPt)
            # clean up APD tasks
            readthread.stopCtr()
            readthread.stopClk()
            if(not(self.canvas == None)):
                self.dispImageGui()
        return self.imageData

    # displays image to screen
    def dispImage(self):
        # remove interpolation to prevent blurring of image
        implot = matplotlib.pyplot.imshow(self.imageData, interpolation="nearest")
        implot.set_cmap('pink')
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.show()

    def dispImageGui(self):
        if(self.plotting == 0):
            if self.dvconv is None:
                implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                self.canvas.axes.set_xlabel('Vx')
                self.canvas.axes.set_ylabel('Vy')
                self.canvas.axes.set_title('Confocal Image')
            else:
                implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                self.canvas.axes.set_xlabel('Distance (um)')
                self.canvas.axes.set_ylabel('Distance (um)')
                self.canvas.axes.set_title('Confocal Image')
            if(len(self.canvas.fig.axes) > 1):
                self.cbar = self.canvas.fig.colorbar(implot,cax = self.canvas.fig.axes[1],label = 'kcounts/sec')
            else:
                self.cbar = self.canvas.fig.colorbar(implot,label = 'kcounts/sec')
            self.cbar.set_cmap('pink')
            self.canvas.draw()
            QtGui.QApplication.processEvents()
            self.plotting = 1
        else:
            if self.dvconv is None:
                implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                self.canvas.axes.set_xlabel('Vx')
                self.canvas.axes.set_ylabel('Vy')
                self.canvas.axes.set_title('Confocal Image')
            else:
                implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                self.canvas.axes.set_xlabel('Distance (um)')
                self.canvas.axes.set_ylabel('Distance (um)')
                self.canvas.axes.set_title('Confocal Image')
            self.cbar.update_bruteforce(implot)
            self.canvas.draw()
            QtGui.QApplication.processEvents()

    @staticmethod
    def updateColorbar(imageData, canvas, extent, cmax):
        implot = canvas.axes.imshow(imageData, cmap = 'pink',
                                          interpolation="nearest", extent = extent)
        implot.set_clim(0,cmax)
        if(len(canvas.fig.axes) > 1):
            cbar = canvas.fig.colorbar(implot,cax = canvas.fig.axes[1],label = 'kcounts/sec')
        else:
            cbar = canvas.fig.colorbar(implot,label = 'kcounts/sec')
        cbar.set_cmap('pink')
        canvas.draw()
        QtGui.QApplication.processEvents()

# Test code to run scan and display image

#newScan = ScanNV(-.4, .4, 120, -.4, .4, 120, .001)
#newScan.scan()
#newScan.dispImage()