from src.core import Script, Parameter
from PyQt4 import QtCore
from PySide.QtCore import Signal, QThread
import time
from collections import deque
from src.instruments import ZIHF2
import numpy as np
from src.core import plotting
from src.instruments import NIDAQ


class GalvoScan(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('point_a', (0.0, 0.0), tuple, 'top left corner point of scan region'),
        Parameter('point_b', (0.1, -0.1), tuple, 'bottom right corner point of scan region'),
        Parameter('num_points', (120,120), tuple, 'number of points to scan in x,y'),
        Parameter('time_per_pt', .001, float, 'time in s to measure at each point'),
        Parameter('settle_time', .0002, float, 'wait time between points to allow galvo to settle')
    ])

    _INSTRUMENTS = {'daq':  NIDAQ}

    _SCRIPTS = {}

    def __init__(self, instruments = None, name = None, settings = None,  log_output = None, timeout = 1000000000):

        self._recording = False
        self._timeout = timeout
        self._plotting = False
        self.dvconv = None

        self.clockAdjust = int((self.settings['time_per_pt'] + self.settings['settle_time'] ) / self.settings['settle_time'] )

        Script.__init__(self, name, settings=settings, instruments=instruments, log_output=log_output)
        QThread.__init__(self)

        self.xVmin = min(self.settings['point_a'][0], self.settings['point_b'][0])
        self.xVmax = max(self.settings['point_a'][0], self.settings['point_b'][0])
        self.yVmin = min(self.settings['point_a'][1], self.settings['point_b'][1])
        self.yVmax = max(self.settings['point_a'][1], self.settings['point_b'][1])

        self.x_array = np.repeat(np.linspace(self.xVmin, self.xVmax, self.settings['num_points'[0]]), self.clockAdjust)
        self.y_array = np.linspace(self.yVmin, self.yVmax, self.settings['num_points'[1]])
        self.dt = (self.settings['time_per_pt']+self.settings['settle_time'])/self.clockAdjust
        self.data = {'image_data': np.zeros((self.settings['num_points'[1]],self.settings['num_points'[0]]))}

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """
        self.data.clear() # clear data queue

        self.log()

        for yNum in xrange(0, len(self.yArray)):
            # if (not (queue is None) and not (queue.empty()) and (queue.get() == 'STOP')):
            #     break
            # initialize APD thread
            self.instruments['daq'].DI_init("ctr0", len(self.xArray) + 1)
            self.initPt = np.transpose(np.column_stack((self.xArray[0],
                                          self.yArray[yNum])))
            self.initPt = (np.repeat(self.initPt, 2, axis=1))
            # move galvo to first point in line
            self.instruments['daq'].AO_init(self.initPt, ["ao0","ao1"])
            self.instruments['daq'].AO_run()
            self.instruments['daq'].AO_waitToFinish()
            self.instruments['daq'].AO_stop()
            self.instruments['daq'].AO_init(self.xArray, "ao0")
            # start counter and scanning sequence
            self.instruments['daq'].DI_run()
            self.instruments['daq'].AO_run()
            self.instruments['daq'].AO_waitToFinish()
            self.instruments['daq'].AO_stop()
            self.xLineData,_ = self.instruments['daq'].DI_read()
            self.diffData = np.diff(self.xLineData)
            self.summedData = np.zeros(len(self.xArray)/self.clockAdjust)
            for i in range(0,int((len(self.xArray)/self.clockAdjust))):
                self.summedData[i] = np.sum(self.diffData[(i*self.clockAdjust+1):(i*self.clockAdjust+self.clockAdjust-1)])
            #also normalizing to kcounts/sec
            self.data['image_data'][yNum] = self.summedData*(.001/self.timePerPt)
            # clean up APD tasks
            self.instruments['daq'].DI_stopCtr()
            self.instruments['daq'].DI_stopClk()
            progress = int(float(yNum + 1)/len(self.yArray)*100)
            self.updateProgress.emit(progress)

        if self.settings['save']:
            self.save()


    def plot(self, axes):
        #todo: this almost definitely breaks if you switch to another plot and back again, find a way to fix it
        #todo: not sure if axes.get_figure is a thing, we'll see
        if(self.plotting == False):
            fig = axes.get_figure()
            if self.dvconv is None:
                implot = self.canvas.axes.imshow(self.data['image_data'], cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                self.canvas.axes.set_xlabel('Vx')
                self.canvas.axes.set_ylabel('Vy')
                self.canvas.axes.set_title('Confocal Image')
            else:
                implot = self.canvas.axes.imshow(self.data['image_data'], cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                self.canvas.axes.set_xlabel('Distance (um)')
                self.canvas.axes.set_ylabel('Distance (um)')
                self.canvas.axes.set_title('Confocal Image')
            if(len(fig.axes) > 1):
                self.cbar = fig.colorbar(implot,cax = fig.axes[1],label = 'kcounts/sec')
            else:
                self.cbar = fig.colorbar(implot,label = 'kcounts/sec')
            self.cbar.set_cmap('pink')
            self.plotting = True
        else:
            if self.dvconv is None:
                implot = axes.imshow(self.data['image_data'], cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                axes.set_xlabel('Vx')
                axes.set_ylabel('Vy')
                axes.set_title('Confocal Image')
            else:
                implot = axes.imshow(self.data['image_data'], cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                self.canvas.axes.set_xlabel('Distance (um)')
                self.canvas.axes.set_ylabel('Distance (um)')
                self.canvas.axes.set_title('Confocal Image')
            self.cbar.update_bruteforce(implot)

if __name__ == '__main__':
    pass

