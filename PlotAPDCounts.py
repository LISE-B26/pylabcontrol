import APDTest as APDIn
import numpy
from PyQt4 import QtGui
import time

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
        while True:
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                break
            self.timeCtr += timePerPt
            self.xdata = numpy.append(self.xdata,self.timeCtr)
            dataPt = self.readAPD()
            self.ydata = numpy.append(self.ydata,dataPt)
            self.dispImageGui()

    def readAPD(self):
        print('start')
        readthread = APDIn.ReadAPD("Dev1/ctr0", sampleRate,
                                           numSamples)
        readthread.runCtr()
        time.sleep(.26)
        #readthread.waitToFinish()
        data = readthread.read()
        readthread.stopCtr()
        readthread.stopClk()
        print('stop')
        diffData = numpy.diff(data)
        normData = numpy.mean(diffData)*(sampleRate/1000)
        return normData



    def dispImageGui(self):
        if(self.plotting == 0):
            self.line, = self.canvas.axes.plot(self.xdata,self.ydata)
            self.canvas.axes.set_title('Counts')
            self.canvas.axes.set_xlabel('Frequency (Hz)')
            self.canvas.axes.set_ylabel('Amplitude (V_RMS)')
            self.canvas.axes.set_xlim(left = 0, right = 10)
            self.canvas.draw()
            QtGui.QApplication.processEvents()
            self.plotting = 1
        else:
            self.line.set_xdata(self.xdata)
            self.line.set_ydata(self.ydata)
            self.canvas.draw()
            QtGui.QApplication.processEvents()