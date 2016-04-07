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
        Parameter('time_per_pt', .001, float, 'time in s to measure at each point')
        Parameter('settle_time', .0002, float, 'wait time between points to allow galvo to settle')
    ])

    _INSTRUMENTS = {'daq':  NIDAQ}

    _SCRIPTS = {}

    def __init__(self, instruments = None, name = None, settings = None,  log_output = None, timeout = 1000000000):

        self._recording = False
        self._timeout = timeout
        self.clockAdjust = int((self.settings['time_per_pt'] + self.settings['settle_time'] ) / self.settings['settle_time'] )

        Script.__init__(self, name, settings=settings, instruments=instruments, log_output=log_output)
        QThread.__init__(self)

        xVmin = min(self.settings['point_a'][0], self.settings['point_b'][0])
        xVmax = max(self.settings['point_a'][0], self.settings['point_b'][0])
        yVmin = min(self.settings['point_a'][1], self.settings['point_b'][1])
        yVmax = max(self.settings['point_a'][1], self.settings['point_b'][1])

        self.x_array = np.repeat(np.linspace(xVmin, xVmax, self.settings['num_points'[0]]), self.clockAdjust)
        self.y_array = np.linspace(yVmin, yVmax, self.settings['num_points'[1]])
        self.dt = (self.settings['time_per_pt']+self.settings['settle_time'])/self.clockAdjust
        self.image_data = np.zeros((self.settings['num_points'[1]],self.settings['num_points'[0]]))

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
            readthread = APDIn.ReadAPD("Dev1/ctr0", 1 / self.dt,
                                       len(self.xArray) + 1)
            self.initPt = np.transpose(np.column_stack((self.xArray[0],
                                          self.yArray[yNum])))
            self.initPt = (np.repeat(self.initPt, 2, axis=1))
            # move galvo to first point in line
            pointthread = DaqOut.DaqOutputWave(self.initPt, 1 / self.dt, "Dev1/ao0:1")
            pointthread.run()
            pointthread.waitToFinish()
            pointthread.stop()
            writethread = DaqOut.DaqOutputWave(self.xArray, 1 / self.dt,
                                               "Dev1/ao0")
            # start counter and scanning sequence
            readthread.runCtr()
            writethread.run()
            writethread.waitToFinish()
            writethread.stop()
            self.xLineData,_ = readthread.read()
            self.diffData = np.diff(self.xLineData)
            self.summedData = np.zeros(len(self.xArray)/self.clockAdjust)
            for i in range(0,int((len(self.xArray)/self.clockAdjust))):
                self.summedData[i] = np.sum(self.diffData[(i*self.clockAdjust+1):(i*self.clockAdjust+self.clockAdjust-1)])
            #also normalizing to kcounts/sec
            self.imageData[yNum] = self.summedData*(.001/self.timePerPt)
            # clean up APD tasks
            readthread.stopCtr()
            readthread.stopClk()
            if(not(self.canvas == None)):
                self.dispImageGui()

        # if self.settings['save']:
        #     self.save()


    def plot(self, axes):

        raise NotImplementedError

if __name__ == '__main__':
    pass

