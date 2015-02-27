# B26 Lab Code
# Last Update: 1/28/15

# External Connections: Galvo x axis on DAQ channel 0
#                       Galvo y axis on DAQ channel 1
#                       APD input to counter 0 (PFI8)
#                       No external connection to counter 1 out (PFI13)


# import external files
import GalvoTest as DaqOut
import APDTest as APDIn
# import standard libraries
import numpy
import matplotlib.pyplot
import time
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
    def __init__(self, xVmin, xVmax, xPts, yVmin, yVmax, yPts, timePerPt, canvas = None):
        # evenly spaced arrays of x and y voltages
        self.xVmin = xVmin
        self.xVmax = xVmax
        self.yVmin = yVmin
        self.yVmax = yVmax
        self.xArray = numpy.linspace(xVmin, xVmax, xPts)
        self.yArray = numpy.linspace(yVmin, yVmax, yPts)
        self.imageData = numpy.zeros((xPts, yPts))
        self.dt = timePerPt
        # stores one line of x data at a time
        self.xLineData = numpy.zeros(len(self.xArray) + 1)
        self.plotting = 0
        self.canvas = canvas
        self.cbar = None

    # runs scan
    def scan(self):
        # scan one x line per loop
        for yNum in xrange(0, len(self.yArray)):
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
            self.xLineData = readthread.read()
            self.imageData[yNum] = numpy.diff(self.xLineData)
            # clean up APD tasks
            readthread.stopCtr()
            readthread.stopClk()
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
# Test code to run scan and display image

#newScan = ScanNV(-.4, .4, 120, -.4, .4, 120, .001)
#newScan.scan()
#newScan.dispImage()