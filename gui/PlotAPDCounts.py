import time

import numpy
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
        time.sleep(.05) #not really understood why this works, but definitely fails without it
        while True:
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                break
            self.timeCtr += timePerPt
            self.xdata = numpy.append(self.xdata,self.timeCtr)
            dataPt = self.readAPD()
            self.ydata = numpy.append(self.ydata,dataPt)
            self.dispImageGui()
        self.readthread.stopCtr()
        self.readthread.stopClk()

    def readAPD(self):
        data = self.readthread.read()
        diffData = numpy.diff(data)
        normData = numpy.mean(diffData)*(sampleRate/1000)
        return normData

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