from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
import numpy as np

from src.instruments.NIDAQ import DAQ

import time


class GalvoScan(Script, QThread):
    updateProgress = Signal(int)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('point_a',
                  [Parameter('x', -0.1, float, 'x-coordinate'),
                   Parameter('y', -0.1, float, 'y-coordinate')
                   ]),
        Parameter('point_b',
                  [Parameter('x', 0.1, float, 'x-coordinate'),
                   Parameter('y', 0.1, float, 'y-coordinate')
                   ]),
        Parameter('num_points',
                  [Parameter('x', 120, int, 'number of x points to scan'),
                   Parameter('y', 120, int, 'number of y points to scan')
                   ]),
        Parameter('time_per_pt', .001, float, 'time in s to measure at each point'),
        Parameter('settle_time', .0002, [.0002], 'wait time between points to allow galvo to settle')
    ])

    _INSTRUMENTS = {'daq':  DAQ}

    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None,  log_output = None, timeout = 1000000000):
        self.timeout = timeout

        Script.__init__(self, name, settings=settings, instruments=instruments, log_output=log_output)

        QThread.__init__(self)

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        self.init_scan()

        for yNum in xrange(0, len(self.y_array)):
            if (self._abort):
                break
            # initialize APD thread
            self.instruments['daq'].DI_init("ctr0", len(self.x_array) + 1, sample_rate_multiplier=(self.clockAdjust - 1))
            self.initPt = np.transpose(np.column_stack((self.x_array[0],
                                          self.y_array[yNum])))
            self.initPt = (np.repeat(self.initPt, 2, axis=1))
            # move galvo to first point in line
            self.instruments['daq'].AO_init(["ao0","ao1"], self.initPt)
            self.instruments['daq'].AO_run()
            self.instruments['daq'].AO_waitToFinish()
            self.instruments['daq'].AO_stop()
            self.instruments['daq'].AO_init(["ao0"], self.x_array, sample_rate_multiplier=(self.clockAdjust - 1))
            # start counter and scanning sequence
            self.instruments['daq'].DI_run()
            self.instruments['daq'].AO_run()
            self.instruments['daq'].AO_waitToFinish()
            self.instruments['daq'].AO_stop()
            self.xLineData,_ = self.instruments['daq'].DI_read()
            self.instruments['daq'].DI_stop()
            self.diffData = np.diff(self.xLineData)
            self.summedData = np.zeros(len(self.x_array)/self.clockAdjust)
            for i in range(0,int((len(self.x_array)/self.clockAdjust))):
                self.summedData[i] = np.sum(self.diffData[(i*self.clockAdjust+1):(i*self.clockAdjust+self.clockAdjust-1)])
            #also normalizing to kcounts/sec
            self.data['image_data'][yNum] = self.summedData*(self.settings['time_per_pt'])
            # clean up APD tasks
            progress = int(float(yNum + 1)/len(self.y_array)*100)
            self.updateProgress.emit(progress)
            #time.sleep(.3) #necessary to avoid invalid task

        if self.settings['save']:
            self.save()


    def plot(self, axes):
        #todo: this almost definitely breaks if you switch to another plot and back again, find a way to fix it
        if(self._plotting == False):
            fig = axes.get_figure()
            if self.dvconv is None:
                implot = axes.imshow(self.data['image_data'], cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                axes.set_xlabel('Vx')
                axes.set_ylabel('Vy')
                axes.set_title('Confocal Image')
            else:
                implot = axes.imshow(self.data['image_data'], cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                axes.set_xlabel('Distance (um)')
                axes.set_ylabel('Distance (um)')
                axes.set_title('Confocal Image')
            if(len(fig.axes) > 1):
                self.cbar = fig.colorbar(implot,cax = fig.axes[1],label = 'kcounts/sec')
            else:
                self.cbar = fig.colorbar(implot,label = 'kcounts/sec')
            self.cbar.set_cmap('pink')
            self._plotting = True
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
                axes.set_xlabel('Distance (um)')
                axes.set_ylabel('Distance (um)')
                axes.set_title('Confocal Image')
            self.cbar.update_bruteforce(implot)

    def init_scan(self):
        self._recording = False
        self._plotting = False
        self.dvconv = None
        self._abort = False

        self.clockAdjust = int(
            (self.settings['time_per_pt'] + self.settings['settle_time']) / self.settings['settle_time'])

        self.xVmin = min(self.settings['point_a']['x'], self.settings['point_b']['x'])
        self.xVmax = max(self.settings['point_a']['x'], self.settings['point_b']['x'])
        self.yVmin = min(self.settings['point_a']['y'], self.settings['point_b']['y'])
        self.yVmax = max(self.settings['point_a']['y'], self.settings['point_b']['y'])

        self.x_array = np.repeat(np.linspace(self.xVmin, self.xVmax, self.settings['num_points']['x']),
                                 self.clockAdjust)
        self.y_array = np.linspace(self.yVmin, self.yVmax, self.settings['num_points']['x'])
        self.dt = (self.settings['time_per_pt'] + self.settings['settle_time']) / self.clockAdjust
        self.data = {'image_data': np.zeros((self.settings['num_points']['y'], self.settings['num_points']['x']))}

if __name__ == '__main__':
    pass

