# B26 Lab Code
# Last Update: 4/14/15

### WORK IN PROGRESS
# Extremely slow and low resolution, need to find a way to lock ZI to DAQ clock to enable synchronization


# External Connections: Galvo x axis on DAQ channel 0
#                       Galvo y axis on DAQ channel 1
#                       APD input to counter 0 (PFI8)
#                       No external connection to counter 1 out (PFI13)


# import external files
from hardware_modules import GalvoMirrors as DaqOut
import hardware_modules.ZiControl as PDIn
# import standard libraries
import numpy
import matplotlib.pyplot
from PyQt4 import QtGui


# This class controls the galvo and APD to run an NV scan, and displays the
# image. The scan is performed line by line in the x direction.

# data is acquired through the ZI
class ScanNV():
    # initializes values
    # xVmin: minimum x voltage for scan
    # xVmax: maximum x voltage for scan
    # xPts: number of x points to scan
    # yVmin: minimum y voltage for scan
    # yVmax: maximum y voltage for scan
    # yPts: number of y points to scan
    # timePerPt: time to stay at each scan point
    # canvas: send matplotlib.backends canvas from PyQt4 gui if being used, otherwise plots with pyplot
    # settleTime: galvo settling time, excluded from scan
    def __init__(self, xVmin, xVmax, xPts, yVmin, yVmax, yPts, timePerPt, canvas = None,settleTime = .0002):
        # evenly spaced arrays of x and y voltages
        assert((timePerPt/settleTime).is_integer())
        self.xVmin = xVmin
        self.xVmax = xVmax
        self.yVmin = yVmin
        self.yVmax = yVmax
        self.settleTime = settleTime
        self.xArray = numpy.linspace(xVmin, xVmax, xPts)
        self.yArray = numpy.linspace(yVmin, yVmax, yPts)
        self.imageData = numpy.zeros((yPts, xPts))
        self.dt = timePerPt
        self.plotting = 0
        self.canvas = canvas
        self.cbar = None

    # runs scan
    def scan(self,queue=None):
        zi = PDIn.ZIHF2(0, 0, 1000)
        # scan one x line per loop
        for yNum in xrange(0, len(self.yArray)):
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                break
            for xNum in xrange(0, len(self.xArray)):
                self.newPt = numpy.transpose(numpy.column_stack((self.xArray[xNum],
                                            self.yArray[yNum])))
                self.newPt = (numpy.repeat(self.newPt, 2, axis=1))
                # move galvo to next point in line
                pointthread = DaqOut.DaqOutputWave(self.newPt, 1 / self.dt, "Dev1/ao0:1")
                pointthread.run()
                pointthread.waitToFinish()
                pointthread.stop()
            # start counter and scanning sequence
                self.pointData = zi.poll(self.dt)
                self.imageData[yNum][xNum] = self.pointData
            if(not(self.canvas == None)):
                self.dispImageGui()
        return self.imageData

    # displays image to screen
    def dispImage(self):
        # remove interpolation to prevent blurring of image
        implot = matplotlib.pyplot.imshow(self.imageData,
                                          interpolation="nearest")
        implot.set_cmap('pink')
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.show()

    def dispImageGui(self):
        if(self.plotting == 0):
            implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                                              interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
            if(len(self.canvas.fig.axes) > 1):
                self.cbar = self.canvas.fig.colorbar(implot,cax = self.canvas.fig.axes[1])
            else:
                self.cbar = self.canvas.fig.colorbar(implot)
            self.cbar.set_cmap('pink')
            self.canvas.draw()
            QtGui.QApplication.processEvents()
            self.plotting = 1
        else:
            implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                                              interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
            self.cbar.update_bruteforce(implot)
            self.canvas.draw()
            QtGui.QApplication.processEvents()

    @staticmethod
    def updateColorbar(imageData, canvas, extent, cmax):
        implot = canvas.axes.imshow(imageData, cmap = 'pink',
                                          interpolation="nearest", extent = extent)
        implot.set_clim(-.01,cmax)
        if(len(canvas.fig.axes) > 1):
            cbar = canvas.fig.colorbar(implot,cax = canvas.fig.axes[1])
        else:
            cbar = canvas.fig.colorbar(implot)
        cbar.set_cmap('pink')
        canvas.draw()
        QtGui.QApplication.processEvents()

# Test code to run scan and display image

#newScan = ScanNV(-.4, .4, 120, -.4, .4, 120, .001)
#newScan.scan()
#newScan.dispImage()