# B26 Lab Code
# Last Update: 2/3/15

# External connections: default channels are input 1, output 1, auxillary 0

# import libraries
import time
import re
import zhinst.utils as utils
import matplotlib.pyplot as plt
import matplotlib.lines
import numpy
import pandas as pd
import sys
from PyQt4 import QtGui, QtCore

# This class initializes an input, output, and auxillary channel on the ZIHF2, and currently has functionality to run
# a sweep, and plot and save the results.
class ZIHF2:
    # initializes values
    # amplitude: output channel amplitude (Vpk)
    # offset: auxillary channel output (V), only functions as offset if aux0 connected to inChannel add port
    # freq: ?
    # ACCoupling: turns ac coupling on (1) or off (0), default off (0)
    # inChannel: specifies input channel number, default channel 1 as listed on device (value 0)
    # outChannel: specifies output channel number, default channel 1 as listed on device (value 0)
    # auxChannel: specifies auxillary channel to use, default channel 1 as listed on device (value 0)
    # add: turns add mode on output channel on (1) or off (0), default 1
    # range: sets output range (V), default 10
    def __init__(self, amplitude, offset, freq, ACCoupling = 0, inChannel = 0, outChannel = 0, auxChannel = 0, add = 1, range = 10, canvas = None):
        # find and connect to device
        self.daq = utils.autoConnect(8005,1)
        self.device = utils.autoDetect(self.daq)
        self.options = self.daq.getByte('/%s/features/options' % self.device)
         #channel settings
        self.in_c = inChannel
        self.out_c = outChannel
        self.demod_c = 0
        self.demod_rate = 10e3
        self.osc_c = 0
        if (not re.match('MF', self.options)):
            self.out_mixer_c = 6
        else:
            self.out_mixer_c = 0
        self.plotting = 0
        self.canvas = canvas
        self.line = None
        self.yLim = None
        self.dataFinal = None


        # Configure the settings relevant to this experiment
        self.exp_setting = [
            ['/%s/sigins/%d/imp50'          % (self.device, self.in_c), 1],
            ['/%s/sigins/%d/ac'             % (self.device, self.in_c), ACCoupling],
            ['/%s/sigins/%d/range'          % (self.device, self.in_c), 2*amplitude],
            ['/%s/demods/%d/order'          % (self.device, self.demod_c), 4],
            ['/%s/demods/%d/rate'           % (self.device, self.demod_c), self.demod_rate],
            ['/%s/demods/%d/harmonic'       % (self.device, self.demod_c), 1],
            ['/%s/demods/%d/phaseshift'     % (self.device, self.demod_c), 0],
            ['/%s/sigouts/%d/on'            % (self.device, self.out_c), 1],
            ['/%s/sigouts/%d/range'         % (self.device, self.out_c), range],
            ['/%s/sigouts/%d/enables/%d'    % (self.device, self.out_c, self.out_mixer_c), 1],
            ['/%s/sigouts/%d/amplitudes/%d' % (self.device, self.out_c, self.out_mixer_c), float(amplitude)],
            ['/%s/AUXOUTS/%d/OFFSET'% (self.device, auxChannel), offset],
            ['/%s/oscs/%d/freq'% (self.device, auxChannel), freq]]

        self.exp_setting.append(['/%s/demods/%d/oscselect' % (self.device, self.demod_c), self.osc_c])
        self.exp_setting.append(['/%s/demods/%d/adcselect' % (self.device, self.demod_c), self.in_c])
        self.exp_setting.append(['/%s/sigins/%d/diff' % (self.device, self.in_c), 0])
        self.exp_setting.append(['/%s/sigouts/%d/add' % (self.device, self.out_c), add])
        self.daq.set(self.exp_setting)
        print(self.exp_setting)

    # performs a frequency sweep and stores result in self.samples
    # freqStart: initial frequency for sweep (Hz)
    # freqEnd: ending frequency for sweep (Hz)
    # sampleNum: number of samples in sweep range
    # samplesPerPt: number of samples to take at each frequency point
    # xScale: choose linear (0) or logarithmic (1) frequency scale, default linear
    # direction: choose sequential (0), binary (1), or bidirectional (2) scan modes, default sequential
    # loopcount: number of times to repeat sweep, default 1
    def sweep(self, freqStart, freqEnd, sampleNum, samplesPerPt, xScale = 0, direction = 0, loopcount = 1, timeout=100000000):
        self.freqStart = freqStart
        self.freqEnd = freqEnd
        self.xScale = xScale
        sweeper = self.daq.sweep(int(timeout))
        sweeper.set('sweep/device', self.device)
        sweeper.set('sweep/start', freqStart)
        sweeper.set('sweep/stop', freqEnd)
        sweeper.set('sweep/samplecount', sampleNum)
        sweeper.set('sweep/gridnode', 'oscs/%d/freq' % self.osc_c)
        #0 = linear, 1 = logarithmic
        sweeper.set('sweep/xmapping', xScale)
        #automatic bandwidth control
        sweeper.set('sweep/bandwidthcontrol', 2)
        #0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)
        sweeper.set('sweep/scan', direction)
        sweeper.set('sweep/loopcount', loopcount)
        #always use samples per point, so set time to 0
        sweeper.set('sweep/averaging/tc', 0)
        #number of samples to average over
        sweeper.set('sweep/averaging/sample', samplesPerPt)

        #specify nodes to recorder data from
        path = '/%s/demods/%d/sample' % (self.device, self.demod_c)
        sweeper.subscribe(path)
        sweeper.execute()

        start = time.time()
        # timeout = 60  # [s]
        print "Will perform %d sweeps...." % loopcount
        #should probably check data[path] is empty instead, just continue if it is
        while not sweeper.finished():
            time.sleep(.5)
            progress = sweeper.progress()
            print "Individual sweep %.2f%% complete.   \r" % (100*progress),
            #read and plot data as it is collected
            data = sweeper.read(True)
            # ensures that first point has completed before attempting to read data
            if path not in data:
                continue
            self.samples = data[path]
            if(not(self.canvas == None)):
                self.plotGui()
            # else:
                # self.plot()
            if (time.time() - start) > timeout:
                # If for some reason the sweep is blocking, force the end of the
                # measurement
                print "\nSweep still not finished, forcing finish..."
                sweeper.finish()
            QtGui.QApplication.processEvents()
        print ""

        # Read the sweep data. This command can also be executed whilst sweeping
        # (before finished() is True), in this case sweep data up to that time point
        # is returned. It's still necessary to issue read() at the end to
        # fetch the rest.
        return_flat_dict = True
        data = sweeper.read(return_flat_dict)
        sweeper.unsubscribe(path)

        # Stop the sweeper thread and clear the memory
        sweeper.clear()
        self.plotting = 0

        # weird bug in code from sample that causes empty data dict when real time reading is implemented, code
        # disabled and this code reads any final samples if data is not empty

        # Check the dictionary returned is non-empty
        #assert data, "read() returned an empty data dictionary, did you subscribe to any paths?"
        # note: data could be empty if no data arrived, e.g., if the demods were
        # disabled or had rate 0
        if(data):
        #assert path in data, "no sweep data in data dictionary: it has no key '%s'" % path
            self.samples = data[path]
        print "sample contains %d sweeps" % len(self.samples)

        # frequency = self.samples[0][0]['frequency']
        # response = numpy.sqrt(self.samples[0][0]['x']**2 + self.samples[0][0]['y']**2)
        # self.dataFinal = numpy.column_stack((frequency,response))

        self.dataFinal = numpy.column_stack((self.samples[0][0]['frequency'],self.samples[0][0]['x'], self.samples[0][0]['y']))

        return self.dataFinal

    def writeData(self, filepath):
        # df = pd.DataFrame(self.dataFinal, columns = ['Frequency', 'Response'])
        df = pd.DataFrame(self.dataFinal, columns = ['Frequency', 'X', 'Y'])
        df.to_csv(filepath, index = False, header=True)

    # plots data contained in self.samples to pyplot window
    def plot(self):
        if(self.plotting == 0):
            plt.ion()
            plt.clf()
            for i in range(0, len(self.samples)):
                # please note: the "[i][0]" indexing is known issue to be fixed in
                # an upcoming release (there shouldn't be an additional [0])
                frequency = self.samples[i][0]['frequency']
                frequency = frequency[~numpy.isnan(frequency)]
                R = numpy.sqrt(self.samples[i][0]['x']**2 + self.samples[i][0]['y']**2)
                R = R[~numpy.isnan(R)]
                plt.plot(frequency, R)
            plt.grid(True)
            plt.title('Results of %d sweeps' % len(self.samples))
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Amplitude (V_RMS)')
            plt.autoscale()
            plt.show(block = False)
            self.plotting = 1
        else:
            for i in range(0, len(self.samples)):
                # please note: the "[i][0]" indexing is known issue to be fixed in
                # an upcoming release (there shouldn't be an additional [0])
                frequency = self.samples[i][0]['frequency']
                frequency = frequency[~numpy.isnan(frequency)]
                R = numpy.sqrt(self.samples[i][0]['x']**2 + self.samples[i][0]['y']**2)
                R = R[~numpy.isnan(R)]
                plt.plot(frequency, R)
                plt.draw()



    # plots data contained in self.samples to GUI
    def plotGui(self):
        if(self.plotting == 0):
                # please note: the "[i][0]" indexing is known issue to be fixed in
                # an upcoming release (there shouldn't be an additional [0])
            frequency = self.samples[0][0]['frequency']
            frequency = frequency[~numpy.isnan(frequency)]
            R = numpy.sqrt(self.samples[0][0]['x']**2 + self.samples[0][0]['y']**2)
            R = R[~numpy.isnan(R)]
            self.line, = self.canvas.axes.plot(frequency, R)
            self.canvas.axes.grid(True)
            self.canvas.axes.set_title('Results of %d sweeps' % len(self.samples))
            self.canvas.axes.set_xlabel('Frequency (Hz)')
            self.canvas.axes.set_ylabel('Amplitude (V_RMS)')
            self.canvas.axes.set_xlim(left = self.freqStart, right = self.freqEnd)
            self.yLim = max(R)*2
            self.canvas.axes.set_ylim(bottom = 0, top = self.yLim)
            self.canvas.draw()
            self.plotting = 1
        else:
                # please note: the "[i][0]" indexing is known issue to be fixed in
                # an upcoming release (there shouldn't be an additional [0])
            frequency = self.samples[0][0]['frequency']
            frequency = frequency[~numpy.isnan(frequency)]
            R = numpy.sqrt(self.samples[0][0]['x']**2 + self.samples[0][0]['y']**2)
            R = R[~numpy.isnan(R)]
            self.line.set_xdata(frequency)
            self.line.set_ydata(R)
            if(self.yLim < max(R)):
                self.yLim = max(R)*2
                self.canvas.axes.set_ylim(bottom = 0, top = self.yLim)
            self.canvas.draw()
            QtGui.QApplication.processEvents()

    # This function switches output 1 on
    def switchOn(self):
        try:
            index = self.exp_setting.index(['/%s/sigouts/%d/on' % (self.device, self.out_c), 0])
        except ValueError:
            return
        self.exp_setting[index]=['/%s/sigouts/%d/on' % (self.device, self.out_c), 1]
        self.daq.set(self.exp_setting)

    # This function switches output 1 off
    def switchOff(self):
        try:
            index = self.exp_setting.index(['/%s/sigouts/%d/on' % (self.device, self.out_c), 1])
        except ValueError:
            return
        self.exp_setting[index]=['/%s/sigouts/%d/on' % (self.device, self.out_c), 0]
        self.daq.set(self.exp_setting)

    # Poll the value of input 1 for polltime seconds and return the magnitude of the average data. Timeout is in milisecond.
    def poll(self, pollTime, timeout = 500):
        path = '/%s/demods/%d/sample' % (self.device, self.demod_c)
        self.daq.subscribe(path)
        flat_dictionary_key = True
        data = self.daq.poll(pollTime,timeout,1,flat_dictionary_key)
        R = numpy.sqrt(numpy.square(data[path]['x'])+numpy.square(data[path]['y']))
        return(numpy.mean(R))


# test code
#if __name__ == '__main__':
    #zi = ZIHF2(1, .5)
    #zi.sweep(1e6, 50e6, 100, 10, xScale = 0)
    #zi.writeData('C:\Users\Experiment\Desktop\ziwritetest.txt')
