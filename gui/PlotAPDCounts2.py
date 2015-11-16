import numpy
import matplotlib.pyplot as plt
from PyQt4 import QtGui
import os
import json
import helper_functions.reading_writing as ReadWriteCommands
import helper_functions.test_types as test_types

from hardware_modules import APD as APDIn


class PlotAPD():
    def __init__(self, canvas = None, sampleRate = 1000, timePerPt = .25):
        self.xdata = []
        self.timeCtr = 0
        self.ydata = []
        self.plotting = 0
        self.canvas = canvas
        self.sampleRate = sampleRate
        self.timePerPt = timePerPt
        self.numSamples = int(sampleRate*timePerPt)+1

    def startPlot(self,queue = None):
        while True:
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                break
            self.readthread = APDIn.ReadAPD("Dev1/ctr0", self.sampleRate,
                                               self.numSamples)
            self.readthread.runCtr()
            #time.sleep(1) #not really understood why this works, but definitely fails without it
            self.timeCtr += self.timePerPt
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
        diffData = numpy.diff(data)
        normData = numpy.mean(diffData)*(self.sampleRate/1000)
        return normData

    def dispImage(self):
        if(self.plotting == 0):
            self.fig = plt.figure(1)
            plt.ion()
            plt.clf()
            plt.plot(self.xdata, self.ydata, '-b')
            plt.title('Counts')
            plt.xlabel('Time(s)')
            plt.ylabel('Counts (unnormalized)')
            plt.autoscale()
            plt.show(block = False)
            self.plotting = 1
            plt.pause(.1)
        else:
            plt.plot(self.xdata, self.ydata, '-b')
            plt.show(block = False)
            plt.pause(.1)

    def dispImageGui(self):
        if(self.plotting == 0):
            self.line, = self.canvas.axes.plot(self.xdata,self.ydata, '-b')
            self.canvas.axes.set_title('Counts')
            self.canvas.axes.set_xlabel('Time (s)')
            self.canvas.axes.set_ylabel('Counts (kcounts/s)')
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


def counter_load_param(filename_or_json):
    '''
    loads counter parameter from json file
    '''
    filename_or_json = str(filename_or_json)

    cnts_param = {}
    # check if input is path to json file or dictionary itself
    if os.path.isfile(filename_or_json):
        cnts_param = ReadWriteCommands.load_json(filename_or_json)
    elif test_types.is_counter_param(filename_or_json):
        cnts_param = json.loads(filename_or_json)

    else:
        raise ValueError('Counter: no valid parameter filename or dictionary')

    return cnts_param

#a = PlotAPD()
#a.startPlot()