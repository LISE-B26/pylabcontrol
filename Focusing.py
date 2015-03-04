import numpy
import scipy.ndimage
import scipy.optimize
import ScanTest as GalvoScan
import GalvoTest as DaqOut
import PiezoController
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
    def scan(cls, minV, maxV, numPts):
        assert(minV >= 1 and maxV <= 99)
        voltRange = numpy.linspace(minV, maxV, numPts)
        data = []
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
        for voltage in voltRange:
            piezo.setVoltage(voltage)
            #time.sleep(1)
            scanner = GalvoScan(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            image = scanner.scan()
            data.append(scipy.ndimage.measurements.standard_deviation(image))
        (_,mean,_),_ = cls.fit(voltRange, data)
        piezo.setVoltage(mean)

    @classmethod
    def fit(cls, x, y):
        n = len(x)
        mean = numpy.sum(x*y)/numpy.sum(y)
        sigma = numpy.sum(y*(x-mean)**2)/n
        return scipy.optimize.curve_fit(cls.gaussian, x, y, p0=[1, mean, sigma])

    @staticmethod
    def gaussian(x,a,x0,sigma):
        return a*numpy.exp(-(x-x0)**2/(2*sigma**2))



a = Focus.scan()