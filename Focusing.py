# B26 Lab Code
# Last Update 3/7/15

# External Connections: z channel of piezo controller connected to piezo on z axis of microscope

import numpy
import scipy.ndimage
import scipy.optimize
import ScanTest as GalvoScan
import GalvoTest as DaqOut
import PiezoController
import matplotlib
import matplotlib.pyplot as plt
import time
from PyQt4 import QtGui

normalRange = 1.0
scanRange = normalRange/10
xRangeMax = .5
yRangeMax = .5
xPts = 20
yPts = 20
timePerPt = .001

# This class runs the standard focusing routine, and sets the piezo height to either the center of the fitted gaussian
# or, if the fit fails, to the center of the scanning range
class Focus:
    # runs the standard focusing routine
    # minV: starting voltage for the scan
    # maxV: ending voltage for the scan
    # numPts: number of points to take in scan
    # piezoChannel: name of channel on piezocontroller for piezo ('X' for low temp, 'Z' for room temp)
    # waitTime: wait time (in seconds) between each point. If this is set too low for an oil-immersion lens, the oil
    #   won't have time to settle between points and the results will be poor
    # canvas: Pass in a backends canvas to plot to the gui, otherwise plots using pyplot
    @classmethod
    def scan(cls, minV, maxV, numPts, piezoChannel, waitTime = 5, canvas = None):
        assert(minV >= 1 and maxV <= 99)
        voltRange = numpy.linspace(minV, maxV, numPts)
        xdata = []
        ydata = []
        (xInit, yInit, _, _) = DaqOut.DaqOutputWave.getOutputVoltages()
        # tries to define a square scanRange/2 to each side of the point. If this would include points out of bounds,
        # that dimension of the square runs from rangeMax-scanRange to rangeMax
        if(numpy.absolute(xInit) > xRangeMax - scanRange/2):
            xMin = numpy.min(numpy.sign(xInit)*xRangeMax, numpy.sign(xInit)*(xRangeMax-scanRange))
            xMax = numpy.max(numpy.sign(xInit)*xRangeMax, numpy.sign(xInit)*(xRangeMax-scanRange))
        else:
            xMin = xInit-scanRange/2
            xMax = xInit+scanRange/2
        if(numpy.absolute(yInit) > yRangeMax - scanRange/2):
            yMin = numpy.min(numpy.sign(yInit)*yRangeMax, numpy.sign(yInit)*(yRangeMax-scanRange))
            yMax = numpy.max(numpy.sign(yInit)*yRangeMax, numpy.sign(yInit)*(yRangeMax-scanRange))
        else:
            yMin = yInit-scanRange/2
            yMax = yInit+scanRange/2
        piezo = PiezoController.MDT693A(piezoChannel)
        # initializes pyplot figure if using pyplot plotting
        if canvas is None:
            fig = plt.figure()
            axes = fig.add_subplot(111)
            plt.ion()
        else:
            axes = canvas.axes
        # plots junk data to initialize lines used later
        dat=[-1,0]
        dat2 = [0,1]
        datline,fitline = axes.plot(dat,dat2,dat,dat2)
        axes.set_xlim([minV-1,maxV+1])
        #axes.set_ylim([0,10])
        cls.updatePlot(canvas)
        for voltage in voltRange:
            piezo.setVoltage(voltage)
            time.sleep(waitTime)
            scanner = GalvoScan.ScanNV(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            image = scanner.scan()
            xdata.append(voltage)
            ydata.append(scipy.ndimage.measurements.standard_deviation(image))
            print(scipy.ndimage.measurements.standard_deviation(image))
            cls.plotData(datline, xdata, ydata, canvas, axes)
        cls.setDaqPt(xInit, yInit)
        (a,mean,sigma,c),_ = cls.fit(voltRange, ydata)
        cls.plotFit(fitline,a,mean,sigma,c,minV,maxV, canvas)
        # checks if computed mean is outside of scan range and, if so, sets piezo to center of scan range to prevent a
        # poor fit from trying to move the piezo by a large amount and breaking the stripline
        if(mean > numpy.min(voltRange) and mean < numpy.max(voltRange) and a > 0):
            piezo.setVoltage(mean)
            print(mean)
        else:
            piezo.setVoltage(numpy.mean(voltRange))
        if canvas is None:
            plt.show()

    # Fits the data to a gaussian given by the cls.gaussian method, and returns the fit parameters. If the fit fails,
    # returns (-1,-1,-1) as the parameters
    @classmethod
    def fit(cls, x, y):
        # x: x input data
        # y: y input data
        try:
            n = len(x)
            # compute mean and standard deviation initial guesses
            mean = numpy.sum(x*y)/numpy.sum(y)
            sigma = numpy.sqrt(abs(sum((x-mean)**2*y)/sum(y)))
            c = min(y)
            return scipy.optimize.curve_fit(cls.gaussian, x, y, p0=[1, mean, sigma, c])
        except RuntimeError:
            print('Gaussian fit failed. Setting piezo to mean of input range')
            return (-1,-1,-1),'Ignore'

    # defines a gaussian for use in the fitting routine
    @staticmethod
    # x: variable
    # a: gaussian amplitude
    # x0: gaussian center
    # sigma: standard deviation
    # c: offset
    def gaussian(x,a,x0,sigma,c):
        return a*numpy.exp(-(x-x0)**2/(2*sigma**2))+c

    # plots the x and y data to the given line
    # line: matplotlib Line2D object to plot data to
    # x: x data
    # y: y data
    # canvas: passed through to updatePlot to allow selection of the proper method to plot the data
    @classmethod
    def plotData(cls, line, x, y, canvas, axes):
        line.set_xdata(x)
        line.set_ydata(y)
        axes.relim()
        axes.autoscale_view(scalex=False, scaley=True)
        cls.updatePlot(canvas)

    # plots the gaussian fit
    # line: matplotlib Line2D object to plot fit to
    # a, mean, sigma, c: gaussian fitting parameters
    # minV: minimum voltage in scan
    # maxV: maximum voltage in scan
    # canvas: passed through to updatePlot to allow selection of the proper method to plot the data
    @classmethod
    def plotFit(cls, line, a, mean, sigma, c, minV, maxV, canvas):
        xfit = numpy.linspace(minV, maxV, 100)
        line.set_xdata(xfit)
        line.set_ydata(cls.gaussian(xfit, a, mean, sigma, c))
        cls.updatePlot(canvas)

    # sets the output channels 0 and 1 on the daq to the given (x,y) point
    # xVolt, yVolt: point to set the daq to
    @staticmethod
    def setDaqPt(xVolt,yVolt):
        pt = numpy.transpose(numpy.column_stack((xVolt,yVolt)))
        pt = (numpy.repeat(pt, 2, axis=1))
        # prefacing string with b should do nothing in python 2, but otherwise this doesn't work
        pointthread = DaqOut.DaqOutputWave(pt, 1000.0, b"Dev1/ao0:1")
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()

    # updates the plot to display given data. If there is an input canvas, uses the QtGui updatiing function, otherwise
    # uses the pyplot ion() pause function to allow it to update
    @staticmethod
    def updatePlot(canvas):
        if canvas is None:
            plt.pause(.001)
        else:
            canvas.draw()
            QtGui.QApplication.processEvents()



#a = Focus.scan(20, 80, 300, 'Z', waitTime = .5)