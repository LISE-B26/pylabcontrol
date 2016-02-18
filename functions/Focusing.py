# B26 Lab Code
# Last Update 3/7/15

# External Connections: z channel of piezo controller connected to piezo on z axis of microscope

import numpy
import scipy.ndimage
import scipy.optimize
from hardware_modules import GalvoMirrors as DaqOut, PiezoController, Attocube
from functions import ScanPhotodiode_DAQ as GalvoScanPD
from functions import ScanAPD as GalvoScanAPD
import matplotlib.gridspec as gridspec

from functions.regions import *

import matplotlib.pyplot as plt
import time
from PyQt4 import QtGui

# normalRange = 1.0
# scanRange = normalRange/20
# xRangeMax = .5
# yRangeMax = .5
# xPts = 20
# yPts = 20
ATTO_FORWARD = 0
ATTO_REVERSE = 1



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
    # return: returns voltage to set it to
    @classmethod
    def scan(cls, minV, maxV, numPts, piezoChannel, waitTime = 5, canvas = None, APD = True, scan_range_roi = None, plotting = True, blocking=True, return_data = False, queue = None, std = True, timePerPt = .001):
        assert(minV >= 1 and maxV <= 99)

        if scan_range_roi == None:
            scan_range_roi = {
                "dx": 0.1,
                "dy": 0.1,
                "xPts": 20,
                "xo": 0.0,
                "yPts": 20,
                "yo": 0.0
            }

        assert_is_roi

        roi_crop(scan_range_roi)

        voltRange = numpy.linspace(minV, maxV, numPts)
        xdata = []
        ydata = []
        (xInit, yInit, _, _) = DaqOut.DaqOutputWave.getOutputVoltages()

        #
        # # tries to define a square scanRange/2 to each side of the point. If this would include points out of bounds,
        # # that dimension of the square runs from rangeMax-scanRange to rangeMax
        # if(numpy.absolute(xInit) > xRangeMax - scanRange/2):
        #     xMin = numpy.min(numpy.sign(xInit)*xRangeMax, numpy.sign(xInit)*(xRangeMax-scanRange))
        #     xMax = numpy.max(numpy.sign(xInit)*xRangeMax, numpy.sign(xInit)*(xRangeMax-scanRange))
        # else:
        #     xMin = xInit-scanRange/2
        #     xMax = xInit+scanRange/2
        # if(numpy.absolute(yInit) > yRangeMax - scanRange/2):
        #     yMin = numpy.min(numpy.sign(yInit)*yRangeMax, numpy.sign(yInit)*(yRangeMax-scanRange))
        #     yMax = numpy.max(numpy.sign(yInit)*yRangeMax, numpy.sign(yInit)*(yRangeMax-scanRange))
        # else:
        #     yMin = yInit-scanRange/2
        #     yMin = yInit-scanRange/2
        #     yMax = yInit+scanRange/2



        xMin, xMax, yMin, yMax = roi_to_min_max(scan_range_roi)

        xPts = scan_range_roi['xPts']
        yPts = scan_range_roi['yPts']

        # xMin, xMax = scan_range_roi['xo'] - scan_range_roi['dx']/2., scan_range_roi['xo'] + scan_range_roi['dx']/2.
        # yMin, yMax = scan_range_roi['yo'] - scan_range_roi['dy']/2., scan_range_roi['yo'] + scan_range_roi['dy']/2.


        piezo = PiezoController.MDT693B(piezoChannel)
        # initializes pyplot figure if using pyplot plotting
        if canvas is None and plotting:
            fig = plt.figure()
            axes = fig.add_subplot(1,3,1)
            axes_img = fig.add_subplot(1,3,2)
            axes_img_best = fig.add_subplot(1,3,3)
            plt.ion()
        elif plotting:
            fig = canvas.fig
            fig.clf()
            gs = gridspec.GridSpec(2,2)
            axes_img = fig.add_subplot(gs[0,0])
            axes_img_best = fig.add_subplot(gs[0,1])
            axes = fig.add_subplot(gs[1,:])
            axes.set_xlabel('Piezo Voltage (V)')
            axes.set_ylabel('Standard Deviation')
            axes.set_title('Autofocusing')
            axes_img.set_xlabel('Vx')
            axes_img.set_ylabel('Vy')
            axes_img.set_title('Current Image')
            axes_img_best.set_xlabel('Vx')
            axes_img_best.set_ylabel('Vy')
            axes_img_best.set_title('Best Focused Image')
            gs.tight_layout(fig)
        # plots junk data to initialize lines used later
        if plotting:
            dat=[-1,0]
            dat2 = [0,0]
            datline,fitline = axes.plot(dat,dat2,dat,dat2)
            axes.set_xlim([minV-1,maxV+1])
            plt.xlabel(piezoChannel + ' Piezo Voltage [V]')
            plt.ylabel('Image Standard Deviation [V]')
            plt.title('Auto-focusing')
            #axes.set_ylim([0,10])
            cls.updatePlot(canvas)
        for voltage in voltRange:
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                return voltage, voltRange, ydata
            piezo.setVoltage(voltage)
            time.sleep(waitTime)
            print(xMin)
            print(xMax)
            print(xPts)
            if(APD):
                scanner = GalvoScanAPD.ScanNV(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            else:
                scanner = GalvoScanPD.ScanNV(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            image = scanner.scan(queue = None)
            xdata.append(voltage)
            if std == True:
                ydata.append(scipy.ndimage.measurements.standard_deviation(image))
            else:
                ydata.append(scipy.ndimage.measurements.mean(image))
            if plotting:
                cls.plotData(datline, xdata, ydata, canvas, axes)

                cls.plotImg(image, canvas, axes_img)

                if ydata[-1] == max(ydata): image_best = image

                cls.plotImg(image_best, canvas, axes_img_best)

        cls.setDaqPt(xInit, yInit)
        (a,mean,sigma,c),_ = cls.fit(voltRange, ydata)
        if plotting:
            cls.plotFit(fitline,a,mean,sigma,c,minV,maxV, canvas)
        # checks if computed mean is outside of scan range and, if so, sets piezo to center of scan range to prevent a
        # poor fit from trying to move the piezo by a large amount and breaking the stripline
        if(mean > numpy.min(voltRange) and mean < numpy.max(voltRange) and a > 0):
            piezo.setVoltage(mean)
            print(mean)
        else:
            piezo.setVoltage(numpy.mean(voltRange))
        if canvas is None and plotting and blocking:
            plt.show()
        elif canvas is None and plotting:
            plt.close()

        if return_data:
            return mean, voltRange, ydata
        elif return_data == False:
            return mean

    @classmethod
    def scan_attocube(cls, min_pos, max_pos, center_position, max_deviation, cont_voltage = 25, step_voltage = 30, atto_frequency = 100, attoChannel = 0, waitTime = .1, canvas = None, APD = True, scan_range_roi = None, plotting = True, blocking=True, return_data = False, queue = None, std = True, timePerPt = .001):
        assert((min_pos < max_pos) and (min_pos > center_position - max_deviation) and (max_pos < center_position + max_deviation))

        if scan_range_roi == None:
            scan_range_roi = {
                "dx": 0.1,
                "dy": 0.1,
                "xPts": 20,
                "xo": 0.0,
                "yPts": 20,
                "yo": 0.0
            }

        assert_is_roi

        roi_crop(scan_range_roi)

        current_pos = min_pos
        xdata = numpy.array([])
        ydata = numpy.array([])
        (xInit, yInit, _, _) = DaqOut.DaqOutputWave.getOutputVoltages()

        #
        # # tries to define a square scanRange/2 to each side of the point. If this would include points out of bounds,
        # # that dimension of the square runs from rangeMax-scanRange to rangeMax
        # if(numpy.absolute(xInit) > xRangeMax - scanRange/2):
        #     xMin = numpy.min(numpy.sign(xInit)*xRangeMax, numpy.sign(xInit)*(xRangeMax-scanRange))
        #     xMax = numpy.max(numpy.sign(xInit)*xRangeMax, numpy.sign(xInit)*(xRangeMax-scanRange))
        # else:
        #     xMin = xInit-scanRange/2
        #     xMax = xInit+scanRange/2
        # if(numpy.absolute(yInit) > yRangeMax - scanRange/2):
        #     yMin = numpy.min(numpy.sign(yInit)*yRangeMax, numpy.sign(yInit)*(yRangeMax-scanRange))
        #     yMax = numpy.max(numpy.sign(yInit)*yRangeMax, numpy.sign(yInit)*(yRangeMax-scanRange))
        # else:
        #     yMin = yInit-scanRange/2
        #     yMin = yInit-scanRange/2
        #     yMax = yInit+scanRange/2



        xMin, xMax, yMin, yMax = roi_to_min_max(scan_range_roi)

        xPts = scan_range_roi['xPts']
        yPts = scan_range_roi['yPts']

        # xMin, xMax = scan_range_roi['xo'] - scan_range_roi['dx']/2., scan_range_roi['xo'] + scan_range_roi['dx']/2.
        # yMin, yMax = scan_range_roi['yo'] - scan_range_roi['dy']/2., scan_range_roi['yo'] + scan_range_roi['dy']/2.


        attocube = Attocube.ANC350()
        attocube.set_amplitude(attoChannel, cont_voltage)
        attocube.set_frequency(attoChannel, atto_frequency)
        attocube.move_absolute(attoChannel, min_pos)
        attocube.set_amplitude(attoChannel, step_voltage)
        time.sleep(5)
        # initializes pyplot figure if using pyplot plotting
        if canvas is None and plotting:
            fig = plt.figure()
            axes = fig.add_subplot(1,3,1)
            axes_img = fig.add_subplot(1,3,2)
            axes_img_best = fig.add_subplot(1,3,3)
            plt.ion()
        elif plotting:
            fig = canvas.fig
            fig.clf()
            gs = gridspec.GridSpec(2,2)
            axes_img = fig.add_subplot(gs[0,0])
            axes_img_best = fig.add_subplot(gs[0,1])
            axes = fig.add_subplot(gs[1,:])
            axes.set_xlabel('Piezo Voltage (V)')
            axes.set_ylabel('Standard Deviation')
            axes.set_title('Autofocusing')
            axes_img.set_xlabel('Vx')
            axes_img.set_ylabel('Vy')
            axes_img.set_title('Current Image')
            axes_img_best.set_xlabel('Vx')
            axes_img_best.set_ylabel('Vy')
            axes_img_best.set_title('Best Focused Image')
            gs.tight_layout(fig)
        # plots junk data to initialize lines used later
        if plotting:
            dat=[-1,0]
            dat2 = [0,0]
            datline,fitline = axes.plot(dat,dat2,dat,dat2)
            axes.set_xlim([min_pos-1,max_pos+1])
            plt.xlabel('Piezo Position [um]')
            plt.ylabel('Image Standard Deviation [V]')
            plt.title('Auto-focusing')
            #axes.set_ylim([0,10])
            cls.updatePlot(canvas)
        while current_pos < max_pos:
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                return current_pos, xdata, ydata
            attocube.step_piezo(attoChannel,ATTO_FORWARD)
            current_pos = attocube.get_position(attoChannel)
            time.sleep(waitTime)
            xdata = numpy.append(xdata, current_pos)
            if(APD):
                scanner = GalvoScanAPD.ScanNV(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            else:
                scanner = GalvoScanPD.ScanNV(xMin, xMax, xPts, yMin, yMax, yPts, timePerPt)
            image = scanner.scan(queue = None)
            if std == True:
                ydata = numpy.append(ydata, scipy.ndimage.measurements.standard_deviation(image))
            else:
                ydata = numpy.append(ydata, scipy.ndimage.measurements.mean(image))
            if plotting:
                cls.plotData(datline, xdata, ydata, canvas, axes)

                cls.plotImg(image, canvas, axes_img)

                if ydata[-1] == max(ydata): image_best = image

                cls.plotImg(image_best, canvas, axes_img_best)

        cls.setDaqPt(xInit, yInit)
        (a,mean,sigma,c),_ = cls.fit(xdata, ydata)
        if plotting:
            cls.plotFit(fitline,a,mean,sigma,c,min_pos,max_pos, canvas)
        # checks if computed mean is outside of scan range and, if so, sets piezo to center of scan range to prevent a
        # poor fit from trying to move the piezo by a large amount and breaking the stripline
        attocube.set_amplitude(attoChannel, cont_voltage)
        if(mean > numpy.min(xdata) and mean < numpy.max(xdata) and a > 0):
            print(mean)
            attocube.move_absolute(attoChannel, mean)
            print(mean)
        else:
            print(numpy.mean(xdata))
            attocube.move_absolute(attoChannel, numpy.mean(xdata))
        if canvas is None and plotting and blocking:
            plt.show()
        elif canvas is None and plotting:
            plt.close()

        if return_data:
            return mean, xdata, ydata
        elif return_data == False:
            return mean

    # Fits the data to a gaussian given by the cls.gaussian method, and returns the fit parameters. If the fit fails,
    # returns (-1,-1,-1) as the parameters
    @classmethod
    def fit(cls, x, y):
        # x: x input data
        # y: y input data
        try:
            n = len(x)
            # compute mean and standard deviation initial guesses
            # mean = numpy.sum(x*y)/numpy.sum(y)
            mean = x[numpy.argmax(y)]

            sigma = numpy.sqrt(abs(sum((x-mean)**2*y)/sum(y)))


            c = min(y)

            print('initial guess for mean and std: {:0.3f} +- {:0.3f}'.format(mean, sigma))

            return scipy.optimize.curve_fit(cls.gaussian, x, y, p0=[1, mean, sigma, c])
        except RuntimeError:
            print('Gaussian fit failed. Setting piezo to mean of input range')
            return (-1,-1,-1,-1),'Ignore'

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

    @classmethod
    def plotImg(cls, imadata, canvas, axes):

        axes.imshow(imadata, cmap = 'pink')
        # axes.autoscale_view(scalex=False, scaley=True)
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
