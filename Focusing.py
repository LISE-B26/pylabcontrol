import numpy
import scipy.ndimage
import scipy.optimize
import ScanTest as GalvoScan
import GalvoTest as DaqOut
import PiezoController
import matplotlib.pyplot as plt
import time

normalRange = 1.0
scanRange = normalRange/10
xRangeMax = .5
yRangeMax = .5
xPts = 10
yPts = 10
timePerPt = .001




class Focus:
    @classmethod
    def scan(cls, minV, maxV, numPts, waitTime = 5, canvas = None):
        assert(minV >= 1 and maxV <= 99)
        voltRange = numpy.linspace(minV, maxV, numPts)
        xdata = []
        ydata = []
        (xInit, yInit, _, _) = DaqOut.DaqOutputWave.getOutputVoltages()
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
        piezo = PiezoController.MDT693A('Z')
        if canvas == None:
            axes = plt.axes()
            line = axes.plot()
            plt.show(block = False)
        else:
            axes = canvas.axes
            line, = axes.plot()
            canvas.axes.set_xlim(left = min(voltRange), right = max(voltRange))
            canvas.axes.set_ylim(bottom = 0, top = 20)
        for voltage in voltRange:
            #piezo.setVoltage(voltage)
            time.sleep(waitTime)
            scanner = GalvoScan.ScanNV(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            image = scanner.scan()
            xdata.append(voltage)
            ydata.append(scipy.ndimage.measurements.standard_deviation(image))
            print(scipy.ndimage.measurements.standard_deviation(image))
            cls.plotData(axes, line, xdata, ydata)
        cls.setDaqPt(xInit, yInit)
        (a,mean,sigma),_ = cls.fit(voltRange, ydata)
        if(mean > numpy.min(voltRange) and mean < numpy.max(voltRange)):
            #piezo.setVoltage(mean)
            print(mean)
        else:
            #piezo.setVoltage(numpy.mean(voltRange))
            print("FAILURE")

    @classmethod
    def fit(cls, x, y):
        n = len(x)
        mean = numpy.sum(x*y)/numpy.sum(y)
        sigma = numpy.sum(y*(x-mean)**2)/n
        return scipy.optimize.curve_fit(cls.gaussian, x, y, p0=[1, mean, sigma])

    @staticmethod
    def gaussian(x,a,x0,sigma):
        return a*numpy.exp(-(x-x0)**2/(2*sigma**2))

    @staticmethod
    def plotData(axes, line, x, y):
        line.set_xdata(x)
        line.set_ydata(y)
        axes.draw()

    @classmethod
    def plotFit(cls, axes, a, mean, sigma, minV, maxV):
        xfit = numpy.linspace(minV, maxV, 100)
        yfit = cls.gaussian(xfit, a, mean, sigma)
        axes.plot(xfit, yfit)
        axes.show()


    @staticmethod
    def setDaqPt(xVolt,yVolt):
        pt = numpy.transpose(numpy.column_stack((xVolt,yVolt)))
        pt = (numpy.repeat(pt, 2, axis=1))
        # prefacing string with b should do nothing in python 2, but otherwise this doesn't work
        pointthread = DaqOut.DaqOutputWave(pt, 1000.0, b"Dev1/ao0:1")
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()


a = Focus.scan(48.5, 52.5, 15, waitTime = 5)