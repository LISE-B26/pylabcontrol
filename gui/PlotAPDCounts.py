# BROKEN, USE PLOTAPDCOUNTS2

import time

import numpy
import matplotlib.pyplot as plt
from PyQt4 import QtGui

from hardware_modules import APD as APDIn


sampleRate = 1000
timePerPt = .25
numSamples = int(sampleRate*timePerPt)+1

class PlotAPD():
    def __init__(self, canvas):
        self.xdata = []
        self.timeCtr = 0
        self.ydata = []
        self.plotting = 0
        self.canvas = canvas

    def startPlot(self,queue):
        self.readthread = APDIn.ReadAPD("Dev1/ctr0", sampleRate,
                                           numSamples)
        self.readthread.runCtr()
        #time.sleep(1) #not really understood why this works, but definitely fails without it
        while True:
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                break
            self.timeCtr += timePerPt
            self.xdata = numpy.append(self.xdata,self.timeCtr)
            dataPt = self.readAPD()
            self.ydata = numpy.append(self.ydata,dataPt)
            if self.canvas == None:
                self.dispImage()
            else:
                self.dispImageGui()
        self.readthread.stopCtr()
        self.readthread.stopClk()

    def readAPD(self):
        data = self.readthread.read()
        print('read')
        diffData = numpy.diff(data)
        normData = numpy.mean(diffData)*(sampleRate/1000)
        return normData

    def dispImage(self):
        if(self.plotting == 0):
            self.fig = plt.figure(1)
            plt.ion()
            plt.clf()
            plt.plot(self.xdata, self.ydata)
            plt.title('Counts')
            plt.xlabel('Time(s)')
            plt.ylabel('Counts (kcounts/s)')
            plt.autoscale
            plt.show(block = False)
            self.plotting = 1
            plt.pause(.1)
        else:
            plt.plot(self.xdata, self.ydata)
            plt.show(block = False)
            plt.pause(.1)

    def dispImageGui(self):
        if(self.plotting == 0):
            self.line, = self.canvas.axes.plot(self.xdata,self.ydata)
            self.canvas.axes.set_title('Counts')
            self.canvas.axes.set_xlabel('Time (s)')
            self.canvas.axes.set_ylabel('Counts (kcounts/s')
            self.canvas.draw()
            QtGui.QApplication.processEvents()
            self.plotting = 1
        else:
            self.line.set_xdata(self.xdata)
            self.line.set_ydata(self.ydata)
            self.canvas.axes.relim()
            self.canvas.axes.autoscale_view(True,True,True)
            self.canvas.draw()
            QtGui.QApplication.processEvents()

#a = PlotAPD(None)
#a.startPlot(None)