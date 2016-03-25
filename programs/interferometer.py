__author__ = 'Experiment'

# locking of interferometer
# started December 1st
# current status: very initial state

class interferometer():
    # initializes values
    # Vmin: minimum x voltage for scan
    # Vmax: maximum x voltage for scan
    # Pts: number of x points to scan

    # timePerPt: time to stay at each scan point
    # canvas: send matplotlib.backends canvas from PyQt4 gui_old if being used, otherwise plots with pyplot

    def __init__(self, Vmin, Vmax, Pts, timePerPt, canvas = None):

        self.Vmin = Vmin
        self.Vmax = Vmax
        self.pts = Pts
        self.time_per_pt = timePerPt

        self.VArray = numpy.linspace(xVmin, xVmax, xPts)
        # self.xArray = numpy.repeat(self.xArray, self.clockAdjust)
        self.dt = timePerPt
        self.plotting = 0
        self.canvas = canvas
        self.cbar = None

    # runs scan
    def scan(self,queue=None):

        # initialize input thread
        readthread = PDIn.ReadAI("Dev1/AI5", 1 / self.dt,
                                   len(self.xArray) + 1)
        self.initPt = numpy.transpose(numpy.column_stack((self.xArray[0],
                                      self.yArray[yNum])))
        self.initPt = (numpy.repeat(self.initPt, 2, axis=1))
        # move galvo to first point in line
        pointthread = DaqOut.DaqOutputWave(self.initPt, 1 / self.dt, "Dev1/ao0:1")
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()
        writethread = DaqOut.DaqOutputWave(self.xArray, 1 / self.dt,
                                           "Dev1/ao0")
        # start counter and scanning sequence
        readthread.run()
        writethread.run()
        writethread.waitToFinish()
        writethread.stop()
        self.xLineData = readthread.read()
        self.averagedData = numpy.zeros(len(self.xArray)/self.clockAdjust)
        for i in range(0,int((len(self.xArray)/self.clockAdjust))):
            self.averagedData[i] = numpy.mean(self.xLineData[(i*self.clockAdjust+1):(i*self.clockAdjust+self.clockAdjust-1)])
        self.imageData[yNum] = self.averagedData
        if(not(self.canvas == None)):
            self.dispImageGui()
        return self.imageData

    # displays image to screen
    def dispImage(self):
        # remove interpolation to prevent blurring of image
        implot = matplotlib.pyplot.imshow(self.imageData,
                                          interpolation="nearest")
        implot.set_cmap('pink')
        matplotlib.pyplot.colorbar()
        matplotlib.pyplot.show()

    def dispImageGui(self):
        if(self.plotting == 0):
            if self.dvconv is None:
                implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                self.canvas.axes.set_xlabel('Vx')
                self.canvas.axes.set_ylabel('Vy')
            else:
                implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                self.canvas.axes.set_xlabel('Distance (um)')
                self.canvas.axes.set_ylabel('Distance (um)')
            if(len(self.canvas.fig.axes) > 1):
                self.cbar = self.canvas.fig.colorbar(implot,cax = self.canvas.fig.axes[1])
            else:
                self.cbar = self.canvas.fig.colorbar(implot)
            self.cbar.set_cmap('pink')
            self.canvas.draw()
            QtGui.QApplication.processEvents()
            self.plotting = 1
        else:
            if self.dvconv is None:
                implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                                                  interpolation="nearest", extent = [self.xVmin,self.xVmax,self.yVmax,self.yVmin])
                self.canvas.axes.set_xlabel('Vx')
                self.canvas.axes.set_ylabel('Vy')
            else:
                implot = self.canvas.axes.imshow(self.imageData, cmap = 'pink',
                  interpolation="nearest", extent = [self.xVmin*self.dvconv,self.xVmax*self.dvconv,self.yVmax*self.dvconv,self.yVmin*self.dvconv])
                self.canvas.axes.set_xlabel('Distance (um)')
                self.canvas.axes.set_ylabel('Distance (um)')
            self.cbar.update_bruteforce(implot)
            self.canvas.draw()
            QtGui.QApplication.processEvents()

    @staticmethod
    def updateColorbar(imageData, canvas, extent, cmax):
        implot = canvas.axes.imshow(imageData, cmap = 'pink',
                                          interpolation="nearest", extent = extent)
        implot.set_clim(-.01,cmax)
        if(len(canvas.fig.axes) > 1):
            cbar = canvas.fig.colorbar(implot,cax = canvas.fig.axes[1])
        else:
            cbar = canvas.fig.colorbar(implot)
        cbar.set_cmap('pink')
        canvas.draw()
        QtGui.QApplication.processEvents()

    # return estimate for how long a scan takes
    def scan_time(self):
        EMPIRICAL_SCAN_RATE = 1.1313 # per point
        return EMPIRICAL_SCAN_RATE * self.x_pts * self.y_pts * self.time_per_pt


def find_lock(Vmin, Vmax, V_step, time_step):
    '''
    ramps voltages from Vmin to Vmax in steps V_step with time interval time_step
    :param Vmin: starting voltage of ramp
    :param Vmax: end voltage of ramp
    :param V_step: voltage step size
    :param time_step: time step
    :return:
        Vo - the starting voltage around which to lock
        set_point - the setpoint for the PI loop
    '''


    ai = ReadAI.ReadAI(device, freq)
    ai.run()
    num_samps_read = 0

    while num_samps_read < freq*run_time:
        data = np.append(data, ai.read())
        num_samps_read = data.__len__()
        print(num_samps_read)
    time_mat = np.arange(0,float(num_samps_read)/freq, step=1/float(freq))

    ai.stop()

