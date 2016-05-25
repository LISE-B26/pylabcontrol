from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread
import numpy as np
from collections import deque
from src.instruments.NIDAQ import DAQ

import datetime as dt
import time
import threading
import Queue


class GalvoScan(Script, QThread):
    updateProgress = Signal(int)
    saveFigure = Signal(str)

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'C:\\Users\\Experiment\\Desktop\\tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', True, bool,'check to automatically save data'),
        Parameter('point_a',
                  [Parameter('x', -0.4, float, 'x-coordinate'),
                   Parameter('y', -0.4, float, 'y-coordinate')
                   ]),
        Parameter('point_b',
                  [Parameter('x', 0.4, float, 'x-coordinate'),
                   Parameter('y', 0.4, float, 'y-coordinate')
                   ]),
        Parameter('num_points',
                  [Parameter('x', 120, int, 'number of x points to scan'),
                   Parameter('y', 120, int, 'number of y points to scan')
                   ]),
        Parameter('time_per_pt', .001, [.001, .002, .005, .01], 'time in s to measure at each point'),
        Parameter('settle_time', .0002, [.0002], 'wait time between points to allow galvo to settle')
    ])

    _INSTRUMENTS = {'daq':  DAQ}

    _SCRIPTS = {}

    def __init__(self, instruments, name = None, settings = None,  log_output = None, timeout = 1000000000):
        self.timeout = timeout
        self.plot_widget = None

        Script.__init__(self, name, settings=settings, instruments=instruments, log_output=log_output)

        QThread.__init__(self)

        self._plot_type = 1

        self.queue = Queue.Queue()

        self.plotting_data = None

    def _function(self):
        """
        This is the actual function that will be executed. It uses only information that is provided in the settings property
        will be overwritten in the __init__
        """

        def init_scan():
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
            self.y_array = np.linspace(self.yVmin, self.yVmax, self.settings['num_points']['y'])
            sample_rate = float(1) / self.settings['settle_time']
            self.instruments['daq']['instance'].settings['analog_output']['ao0']['sample_rate'] = sample_rate
            self.instruments['daq']['instance'].settings['analog_output']['ao1']['sample_rate'] = sample_rate
            self.instruments['daq']['instance'].settings['digital_input']['ctr0']['sample_rate'] = sample_rate
            self.data = {'image_data': np.zeros((self.settings['num_points']['y'], self.settings['num_points']['x'])), 'bounds': [self.xVmin, self.xVmax, self.yVmin, self.yVmax]}

        # self.data.clear()  # clear data queue
        self.log('update instruments')
        init_scan()
        # preallocate
        # image_data = np.zeros(len(self.x_array), len(self.y_array))
        update_time = dt.datetime.now()


        for yNum in xrange(0, len(self.y_array)):

            if (self._abort):
                break
            # initialize APD thread
            self.instruments['daq']['instance'].DI_init("ctr0", len(self.x_array) + 1, sample_rate_multiplier=(self.clockAdjust - 1))
            self.initPt = np.transpose(np.column_stack((self.x_array[0],
                                          self.y_array[yNum])))
            self.initPt = (np.repeat(self.initPt, 2, axis=1))

            # move galvo to first point in line
            self.instruments['daq']['instance'].AO_init(["ao0","ao1"], self.initPt)
            self.instruments['daq']['instance'].AO_run()
            self.instruments['daq']['instance'].AO_waitToFinish()
            self.instruments['daq']['instance'].AO_stop()
            self.instruments['daq']['instance'].AO_init(["ao0"], self.x_array, sample_rate_multiplier=(self.clockAdjust - 1))
            # start counter and scanning sequence
            self.instruments['daq']['instance'].DI_run()
            self.instruments['daq']['instance'].AO_run()
            self.instruments['daq']['instance'].AO_waitToFinish()
            self.instruments['daq']['instance'].AO_stop()
            xLineData,_ = self.instruments['daq']['instance'].DI_read()
            self.instruments['daq']['instance'].DI_stop()
            diffData = np.diff(xLineData)

            summedData = np.zeros(len(self.x_array)/self.clockAdjust)
            for i in range(0,int((len(self.x_array)/self.clockAdjust))):
                summedData[i] = np.sum(diffData[(i*self.clockAdjust+1):(i*self.clockAdjust+self.clockAdjust-1)])
            #also normalizing to kcounts/sec
            self.data['image_data'][yNum] = summedData * (.001/self.settings['time_per_pt'])


            # image_data[:, yNum] = self.summedData * (self.settings['time_per_pt'])
            # self.data.append(image_data)

            # sending updates every cycle leads to invalid task errors, so wait and don't overload gui
            current_time = dt.datetime.now()
            if((current_time-update_time).total_seconds() > 2):
                self.plotting_data = np.copy(self.data['image_data'])
                progress = int(float(yNum + 1)/len(self.y_array)*100)
                self.updateProgress.emit(progress)
                # print('emitting')
                update_time = current_time
                #time.sleep(0) #ensure plot finishes before starting next row, otherwise occasional daq crash
                # print('waiting')
                # temp = self.queue.get(True)
                # print('got')
                # print('queue_len', self.queue.qsize())

        self.plotting_data = np.copy(self.data['image_data'])
        if not ((current_time - update_time).total_seconds() > 1.5):
            time.sleep(2 - (current_time - update_time).total_seconds())
        progress = 100
        self.updateProgress.emit(progress)

        if self.settings['save']:
            self.save()
            self.save_data()
            self.save_log()


    def plot(self, axes):
        if(self._plotting == False):
            self.fig = axes.get_figure()
            if self.dvconv is None:
                implot = axes.imshow(self.plotting_data, cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                axes.set_xlabel('Vx')
                axes.set_ylabel('Vy')
                axes.set_title('Confocal Image')
            else:
                implot = axes.imshow(self.plotting_data, cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                axes.set_xlabel('Distance (um)')
                axes.set_ylabel('Distance (um)')
                axes.set_title('Confocal Image')
            if(len(self.fig.axes) > 1):
                self.cbar = self.fig.colorbar(implot,cax = self.fig.axes[1],label = 'kcounts/sec')
            else:
                self.cbar = self.fig.colorbar(implot,label = 'kcounts/sec')
            self.cbar.set_cmap('pink')
            self._plotting = True
        else:
            if self.dvconv is None:
                implot = axes.imshow(self.plotting_data, cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                axes.set_xlabel('Vx')
                axes.set_ylabel('Vy')
                axes.set_title('Confocal Image')
            else:
                implot = axes.imshow(self.plotting_data, cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                axes.set_xlabel('Distance (um)')
                axes.set_ylabel('Distance (um)')
                axes.set_title('Confocal Image')
            self.cbar.update_bruteforce(implot)

    def stop(self):
        self._abort = True

    def save_data(self, filename = None):
        super(GalvoScan, self).save_data(filename)
        if filename is None:
            filename = self.filename('.jpg')
        self.saveFigure.emit(filename)

if __name__ == '__main__':
    script, failed, instruments = Script.load_and_append(script_dict={'GalvoScan': 'GalvoScan'})

    print(script)
    print(failed)
    # print(instruments)

