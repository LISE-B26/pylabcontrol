import json
import os
from collections import deque

import src.helper_functions.reading_writing as ReadWriteCommands
import src.helper_functions.test_types as test_types
import matplotlib.pyplot as plt
import numpy
from PyQt4 import QtGui

from src.hardware_modules import APD as APDIn


# This function continuously plots the output of the APD. Note that it restarts the APD every point for ease of coding,
# so there is some reset time between points that isn't recorded. From brief testing, the default settings
# sampleRate = 1000, timePerPt = .25 yield a duty cycle of ~70%
class PlotAPD():
    def __init__(self, canvas = None, sampleRate = 1000.0, bufferSize = 1):
        '''

        :param canvas: canvas to plot on. Supply one if calling from GUI, if not a pyplot plot is created
        :param sampleRate: Samples/sec to read from apd
        :param timePerPt: time to average over these samples per plotted pt
        '''
        self.plot_length = 100
        self.xdata = deque(maxlen = self.plot_length)
        self.timeCtr = 0
        self.ydata = deque(maxlen = self.plot_length)
        self.plotting = 0
        self.canvas = canvas
        self.sampleRate = sampleRate
        self.bufferSize = max(int(sampleRate)+1, bufferSize)


    def startPlot(self,queue = None):
        '''
        Once object created, call this function to start plotting
        :param queue: To stop plotting elegantly, pass in queue. Putting 'STOP' in queue breaks loop (other code can
            execute in parallel because below code creates own thread)
        '''
        self.readthread = APDIn.ReadAPD("Dev1/ctr0", self.sampleRate, self.bufferSize, continuous_acquisition= True)
        self.readthread.runCtr()
        while True:
            if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
                break
            #time.sleep(1) #not really understood why this works, but definitely fails without it
            self.timeCtr += 1
            #self.xdata = numpy.append(self.xdata,self.timeCtr)
            self.xdata.append(self.timeCtr)
            dataPt = self.readAPD()
            #self.ydata = numpy.append(self.ydata,dataPt)
            self.ydata.append(dataPt)
            if self.canvas == None:
                self.dispImage()
            else:
                self.dispImageGui()
        self.readthread.stopCtr()
        self.readthread.stopClk()

    def readAPD(self):
        '''
        Reads from readthread defined above and averages over all samples taken in timeperpt
        :return: average value at timestep (scalar) to be plotted
        '''
        data, num_samples_read = self.readthread.read()
        diffData = numpy.diff(data[0:num_samples_read.value])*(self.sampleRate/1000)
        normData = numpy.mean(diffData)*(self.sampleRate/1000)
        return normData

    def dispImage(self):
        '''
        Plots data using pyplot
        '''
        if(self.plotting == 0):
            self.fig = plt.figure(1)
            plt.ion()
            plt.clf()
            plt.plot(self.xdata, self.ydata, '-b')
            plt.title('Counts')
            plt.xlabel('Time(arb)')
            plt.ylabel('Counts (unnormalized)')
            plt.autoscale()
            plt.show(block = False)
            self.plotting = 1
            plt.pause(.1)
        else:
            self.fig.clear()
            plt.plot(self.xdata, self.ydata, '-b')
            plt.show(block = False)
            plt.pause(.1)

    def dispImageGui(self):
        '''
        Plots data to canvas, to be used with GUI
        '''
        if(self.plotting == 0):
            self.line, = self.canvas.axes.plot(self.xdata,self.ydata, '-b')
            self.canvas.axes.set_title('Counts')
            self.canvas.axes.set_xlabel('Time (arb)')
            self.canvas.axes.set_ylabel('Counts (kcounts/s)')
            self.canvas.draw()
            QtGui.QApplication.processEvents()
            self.plotting = 1
        else:
            self.canvas.axes.clear()
            self.line.set_xdata(self.xdata)
            self.line.set_ydata(self.ydata)
            self.canvas.axes.relim()
            self.canvas.axes.autoscale_view(True,True,True)
            self.canvas.draw()
            QtGui.QApplication.processEvents()


def counter_load_param(filename_or_json):
    '''
    loads counter parameter from json file into gui
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