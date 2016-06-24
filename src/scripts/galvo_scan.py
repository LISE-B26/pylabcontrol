from src.core import Script, Parameter
from PySide.QtCore import Signal, QThread, QReadWriteLock
import numpy as np
from src.instruments.NIDAQ import DAQ
from src.plotting.plots_2d import plot_fluorescence
import time
import datetime
import Queue


class GalvoScan(Script, QThread):
    """
    GalvoScan uses the apd, daq, and galvo to sweep across voltages while counting photons at each voltage,
    resulting in an image in the current field of view of the objective.
    """
    updateProgress = Signal(int)
    lock = QReadWriteLock()

    _DEFAULT_SETTINGS = Parameter([
        Parameter('path',  'tmp_data', str, 'path to folder where data is saved'),
        Parameter('tag', 'some_name'),
        Parameter('save', False, bool,'check to automatically save data'),
        Parameter('point_a',
                  [Parameter('x', -0.4, float, 'x-coordinate'),
                   Parameter('y', -0.4, float, 'y-coordinate')
                   ]),
        Parameter('point_b',
                  [Parameter('x', 0.4, float, 'x-coordinate'),
                   Parameter('y', 0.4, float, 'y-coordinate')
                   ]),
        Parameter('RoI_mode','corner',['corner', 'center'],'mode to calculate region of interest.\n \
                                                           corner: pta and ptb are diagonal corners of rectangle.\n \
                                                           center: pta is center and pta is extend or rectangle'),
        Parameter('num_points',
                  [Parameter('x', 120, int, 'number of x points to scan'),
                   Parameter('y', 120, int, 'number of y points to scan')
                   ]),
        Parameter('time_per_pt', .001, [.001, .002, .005, .01, .015, .02], 'time in s to measure at each point'),
        Parameter('settle_time', .0002, [.0002], 'wait time between points to allow galvo to settle'),
        Parameter('max_counts_plot', -1, int, 'Rescales colorbar with this as the maximum counts on replotting')
    ])

    _INSTRUMENTS = {'daq':  DAQ}

    _SCRIPTS = {}

    def __init__(self, instruments, name=None, settings=None, log_function=None, data_path=None):
        '''
        Initializes GalvoScan script for use in gui

        Args:
            instruments: list of instrument objects
            name: name to give to instantiated script object
            settings: dictionary of new settings to pass in to override defaults
            log_function: log function passed from the gui to direct log calls to the gui log
            data_path: path to save data

        '''
        self.plot_widget = None

        Script.__init__(self, name, settings=settings, instruments=instruments, log_function=log_function,
                        data_path = data_path)

        QThread.__init__(self)

        self._plot_type = 'main'

        self.queue = Queue.Queue()

        self._plotting = False

    def _function(self):
        """
        Executes threaded galvo scan
        """
        update_time = datetime.datetime.now()

        self.updateProgress.emit(1)

        self._plotting = True

        def init_scan():
            self._recording = False
            self._abort = False

            self.clockAdjust = int(
                (self.settings['time_per_pt'] + self.settings['settle_time']) / self.settings['settle_time'])

            [self.xVmin, self.xVmax, self.yVmax, self.yVmin] = self.pts_to_extent(self.settings['point_a'],
                                                                                  self.settings['point_b'],
                                                                                  self.settings['RoI_mode'])


            self.x_array = np.repeat(np.linspace(self.xVmin, self.xVmax, self.settings['num_points']['x']),
                                     self.clockAdjust)
            self.y_array = np.linspace(self.yVmin, self.yVmax, self.settings['num_points']['y'], endpoint=True)
            sample_rate = float(1) / self.settings['settle_time']
            self.instruments['daq']['instance'].settings['analog_output']['ao0']['sample_rate'] = sample_rate
            self.instruments['daq']['instance'].settings['analog_output']['ao1']['sample_rate'] = sample_rate
            self.instruments['daq']['instance'].settings['digital_input']['ctr0']['sample_rate'] = sample_rate
            self.data = {'image_data': np.zeros((self.settings['num_points']['y'], self.settings['num_points']['x'])),
                         'bounds': [self.xVmin, self.xVmax, self.yVmin, self.yVmax]}

        init_scan()
        self.data['extent'] = [self.xVmin, self.xVmax, self.yVmax, self.yVmin]

        for yNum in xrange(0, len(self.y_array)):

            if self._abort:
                break
            # initialize APD thread
            clk_source = self.instruments['daq']['instance'].DI_init("ctr0", len(self.x_array) + 1)
            self.initPt = np.transpose(np.column_stack((self.x_array[0],
                                          self.y_array[yNum])))
            self.initPt = (np.repeat(self.initPt, 2, axis=1))

            # move galvo to first point in line
            self.instruments['daq']['instance'].AO_init(["ao0", "ao1"], self.initPt, "")
            self.instruments['daq']['instance'].AO_run()
            self.instruments['daq']['instance'].AO_waitToFinish()
            self.instruments['daq']['instance'].AO_stop()
            self.instruments['daq']['instance'].AO_init(["ao0"], self.x_array, clk_source)
            # start counter and scanning sequence
            self.instruments['daq']['instance'].AO_run()
            self.instruments['daq']['instance'].DI_run()
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



            current_time = datetime.datetime.now()
            #prevents emits to the gui too often, which seems to slow it down
            if ((current_time - update_time).total_seconds() > 0.1):
                progress = int(float(yNum + 1) / len(self.y_array) * 100)
                self.updateProgress.emit(progress)
                update_time = current_time


        progress = 100
        self.updateProgress.emit(progress)

        self._plotting = False

        #saves standard values and the galvo image plot
        if self.settings['save']:
            self.save_b26()
            self.save_data()
            self.save_log()
            self.save_image_to_disk()


    @staticmethod
    def pts_to_extent(pta, ptb, roi_mode):
        """

        Args:
            pta: point a
            ptb: point b
            roi_mode:   mode how to calculate region of interest
                        corner: pta and ptb are diagonal corners of rectangle.
                        center: pta is center and ptb is extend or rectangle

        Returns: extend of region of interest [xVmin, xVmax, yVmax, yVmin]

        """
        if roi_mode == 'corner':
            xVmin = min(pta['x'], ptb['x'])
            xVmax = max(pta['x'], ptb['x'])
            yVmin = min(pta['y'], ptb['y'])
            yVmax = max(pta['y'], ptb['y'])
        elif roi_mode == 'center':
            xVmin = pta['x'] - float(ptb['x']) / 2.
            xVmax = pta['x'] + float(ptb['x']) / 2.
            yVmin = pta['y'] - float(ptb['y']) / 2.
            yVmax = pta['y'] + float(ptb['y']) / 2.
        return [xVmin, xVmax, yVmax, yVmin]

    def plot(self, image_figure, axes_colorbar = None):
        '''
        Plots the galvo scan image to the input figure, clearing the figure and creating new axes if necessary
        Args:
            image_figure: figure to plot onto
            axes_colorbar: axes with a colorbar to overwrite with the new colorbar

        '''

        self.axes_image = self.get_axes_layout(image_figure)
        if 'image_data' in self.data.keys() and not self.data['image_data'] == []:
            plot_fluorescence(self.data['image_data'], self.data['extent'], self.axes_image,
                              max_counts=self.settings['max_counts_plot'],
                              axes_colorbar=axes_colorbar)

    def stop(self):
        '''
        Stops galvo scan
        '''
        self._abort = True


if __name__ == '__main__':
    script, failed, instruments = Script.load_and_append(script_dict={'GalvoScan': 'GalvoScan'})

    print(script)
    print(failed)
    # print(instruments)

