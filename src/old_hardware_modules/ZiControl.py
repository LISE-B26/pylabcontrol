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
from copy import deepcopy
from collections import deque
# This class initializes an input, output, and auxillary channel on the ZIHF2, and currently has functionality to run
# a sweep, and plot and save the results.
class ZIHF2:


    def __init__(self, amplitude, offset, freq, ACCoupling = 0, inChannel = 0, outChannel = 0, auxChannel = 0, add = 1, range = 10, canvas = None):

        '''
            initializes values
        :param amplitude: output channel amplitude (Vpk)
        :param offset: auxillary channel output (V), only old_functions as offset if aux1  (value 0) connected to inChannel add port
        :param freq: output channel frequence (Hz)
        :param ACCoupling: turns ac coupling on (1) or off (0), default off (0)
        :param inChannel: specifies input channel number, default channel 1 as listed on device (value 0)
        :param outChannel: specifies output channel number, default channel 1 as listed on device (value 0)
        :param auxChannel: specifies auxillary channel to use, default channel 1 as listed on device (value 0)
        :param add: turns add mode on output channel on (1) or off (0), default 1
        :param range: sets output range (V), default 10
        :param find and connect to device
        '''

        self.daq = utils.autoConnect(8005,1) # connect to ZI, 8005 is the port number
        self.device = utils.autoDetect(self.daq)
        self.options = self.daq.getByte('/%s/features/options' % self.device)
         #channel settings
        self.in_c = inChannel
        self.out_c = outChannel
        self.demod_c = 0
        self.demod_rate = 10e3 # sample rate of low pass filtered signal after mixing
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
        # note that the output amplitude has to be scaled with the range to give the right result
        # todo: JG - this can probably be written in a single line using a propper dictionary
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
            ['/%s/sigouts/%d/amplitudes/%d' % (self.device, self.out_c, self.out_mixer_c), float(amplitude)/range],
            ['/%s/AUXOUTS/%d/OFFSET'% (self.device, auxChannel), offset],
            ['/%s/oscs/%d/freq'% (self.device, auxChannel), freq]]

        self.exp_setting.append(['/%s/demods/%d/oscselect' % (self.device, self.demod_c), self.osc_c])
        self.exp_setting.append(['/%s/demods/%d/adcselect' % (self.device, self.demod_c), self.in_c])
        self.exp_setting.append(['/%s/sigins/%d/diff' % (self.device, self.in_c), 0])
        self.exp_setting.append(['/%s/sigouts/%d/add' % (self.device, self.out_c), add])
        self.daq.set(self.exp_setting)
        print(self.exp_setting)


    def sweep(self, freqStart, freqEnd, sampleNum, samplesPerPt, xScale = 0, direction = 0, loopcount = 1, timeout=100000000):
        '''
        performs a frequency sweep and stores result in self.samples
        :param freqStart: initial frequency for sweep (Hz)
        :param freqEnd: ending frequency for sweep (Hz)
        :param sampleNum: number of samples in sweep range
        :param samplesPerPt: number of samples to take at each frequency point
        :param xScale: choose linear (0) or logarithmic (1) frequency scale, default linear
        :param direction: choose sequential (0), binary (1), or bidirectional (2) scan modes, default sequential
        :param loopcount: number of times to repeat sweep, default 1
        :param timeout:
        :return:
        '''
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
            time.sleep(5)
            progress = sweeper.progress()
            print "Individual sweep %.2f%% complete. \n" % (100*progress),
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

        # todo: JG: should be able to run this without figures, plotting should be optional
        # return self.dataFinal, self.fig
        return self.dataFinal

# saves the esr_data to a timestamped file in the dirpath with a tag
    def save_ZI(self, ZI_data, fig, dirpath, tag = "", saveImage = True):
        df = pd.DataFrame(ZI_data)
        start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        filepathCSV = dirpath + "\\" + start_time + '_' + tag + '.csv'
        df.to_csv(filepathCSV)
        filepathPNG = dirpath + "\\" + start_time + '_' + tag + '.png'
        print filepathPNG

        if (fig == None) == False:
            fig.savefig(filepathPNG, format='png')

    # plots data contained in self.samples to pyplot window
    def plot(self):
        if(self.plotting == 0):
            self.fig = plt.figure(1)
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
            self.fig = self.canvas.figure
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


# This class initializes an input, output, and auxillary channel on the ZIHF2, and currently has functionality to run
# a sweep, and plot and save the results.
# version 2, started by JG March 3rd 2016
class ZIHF2_v2(QtCore.QThread):

    updateProgress = QtCore.Signal(int)

    ZI_Default_Settings = {
        'general': {
            'freq' : 1e6,
            'sigins' : {
                'channel' : 0,
                'imp50': 1,
                'ac' : 1,
                'range': 10,
                'diff' : 0
            },
            'sigouts' : {
                'channel' : 0,
                'on' : 1,
                'range' : 10,
                'add': 1
            },
            'demods': {
                'channel' : 0,
                'order' : 4,
                'rate' : 10e3,
                'harmonic': 1,
                'phaseshift': 0,
                'oscselect': 0,
                'adcselect' : 0
            },
            'aux':{
                'channel' : 0,
                'offset' : 1
            },
        },
        # 'sweep' : {
        #     'start' : 0,
        #     'stop' : 0,
        #     'samplecount' : 0,
        #     'gridnode' : 'oscs/0/freq',
        #     'xmapping' : 0, #0 = linear, 1 = logarithmic
        #     'bandwidthcontrol': 2, #2 = automatic bandwidth control
        #     'scan' : 0, #scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)
        #     'loopcount': 1,
        #     'averaging/sample' : 2 #number of samples to average over
        # }
        'sweep' : {
            'start' : {'value': 0, 'valid_values': None, 'info':'start value of sweep', 'visible' : True},
            'stop' : {'value': 0, 'valid_values': None, 'info':'end value of sweep', 'visible' : True},
            'samplecount' : {'value': 0, 'valid_values': None, 'info':'number of data points', 'visible' : True},
            'gridnode' : {'value': 'oscs/0/freq', 'valid_values': ['oscs/0/freq', 'oscs/1/freq'], 'info':'channel that\'s used in sweep', 'visible' : True},
            'xmapping' : {'value': 0, 'valid_values': [0,1], 'info':'mapping 0 = linear, 1 = logarithmic', 'visible' : True},
            'bandwidthcontrol' : {'value': 2, 'valid_values': [2], 'info':'2 = automatic bandwidth control', 'visible' : True},
            'scan' : {'value': 0, 'valid_values': [0, 1, 2], 'info':'#scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)', 'visible' : True},
            'loopcount' : {'value': 1, 'valid_values': None, 'info':'number of times it sweeps', 'visible' : False},
            'averaging/sample' : {'value': 0, 'valid_values': None, 'info':'number of samples to average over', 'visible' : True}
        }
    }

    @property
    def general_settings(self):
        return self._settings['general']
    @general_settings.setter
    def general_settings(self, value):
        # print('======== general settings =================')
        self._settings['general'].update(value)
        commands = self.dict_to_settings(value)
        # print(commands)
        self.daq.set(commands)


    @property
    def sweep_settings(self):
        return self._settings['sweep']
    @sweep_settings.setter
    def sweep_settings(self, value):

        self._settings['sweep'].update(value)
        # print('======== sweep settings =================')
        commands = self.dict_to_settings({'sweep' : value})
        # print(commands)
        self.sweeper.set(commands)

    # This function switches output on or off
    @property
    def OutputOn(self):
        return bool(self._ZI_Settings['sigouts']['on'])
    @OutputOn.setter
    def OutputOn(self, value):
        self._ZI_Settings['sigouts']['on'] = int(value)
        self.daq.set(['/%s/sigouts/%d/on' % (self.device, self._ZI_Settings['sigouts']['channel']), self._ZI_Settings['sigouts']['on']])


    def dict_to_settings(self, dictionary):
        '''
        converts dictionary to list of  setting, which can then be passed to the zi controler
        :param dictionary = dictionary that contains the settings
        :return: settings = list of settings, which can then be passed to the zi controler
        '''
        # create list that is passed to the ZI controler


        settings = []
        for key, element in sorted(dictionary.iteritems()):
            if isinstance(element, dict) and key in ['sigins', 'sigouts', 'demods']:
                channel = element['channel']
                for sub_key, val in sorted(element.iteritems()):
                    if not sub_key == 'channel':
                        settings.append(['/%s/%s/%d/%s'%(self.device, key, channel, sub_key), val])
            elif isinstance(element, dict) and key in ['aux']:
                settings.append(['/%s/AUXOUTS/%d/OFFSET'% (self.device, element['channel']), element['offset']])
            elif key in ['freq']:
                settings.append(['/%s/oscs/%d/freq' % (self.device, dictionary['sigouts']['channel']), dictionary['freq']])
            elif isinstance(element, dict) and key in ['sweep']:
                for key, val in element.iteritems():

                    if isinstance(val, dict) and 'value' in  val:
                        settings.append(['sweep/%s' % (key), val['value']])
                    else:
                        settings.append(['sweep/%s' % (key), val])
            elif isinstance(element, dict) == False:
                settings.append([key, element])


        return settings

    def __init__(self, ZI_Settings = {}, port_number = 8005, timeout = 100000000):
        print('creating')

        '''
        initializes values
        :ZI_Settings dictionary with settings for ZI HF2 control, check ZI_Default_Settings variable for elements
        '''
        def connect(port_number, timeout):
            self.daq = utils.autoConnect(port_number,1) # connect to ZI, 8005 is the port number
            self.device = utils.autoDetect(self.daq)
            self.options = self.daq.getByte('/%s/features/options' % self.device)
            self.sweeper = self.daq.sweep(timeout)
            self._timeout = timeout

        connect(port_number, timeout)
        # overwrite the default setting with the settings that have been provided
        self._settings = deepcopy(self.ZI_Default_Settings)
        self._settings.update(ZI_Settings)
        self.general_settings = self._settings['general']
        self.sweep_settings = self._settings['sweep']

        self.sweeper.set('sweep/device', self.device)
        #
        self.sweep_data = deque()
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.stop()

    def run_sweep(self, sweep_data):
        '''
        starts a sweep
        :param sweep_data: dictionary that contains the data acquired from the ZI, e.g. 'frequency', 'r'
        :return:
        '''

        self._recording = False
        self._acquisition_mode = 'sweep'
        self._sweep_values = sweep_data.keys()
        self.start()
        print('self.start()')
    def run(self):
        self._recording = True

        while self._recording:
            #Emit the signal so it can be received on the UI side.
            if self._acquisition_mode == 'sweep':

                #specify nodes to recorder data from
                path = '/%s/demods/%d/sample' % (self.device, self.general_settings['demods']['channel'])
                self.sweeper.subscribe(path)
                self.sweeper.execute()
                start = time.time()
                while not self.sweeper.finished():
                    time.sleep(1)
                    progress = int(100*self.sweeper.progress())
                    print('progress', progress)
                    data = self.sweeper.read(True)# True: flattened dictionary

                    #  ensures that first point has completed before attempting to read data
                    if path not in data:
                        continue

                    data = data[path][0][0] # the data is nested, we remove the outer brackets with [0][0]
                    # now we only want a subset of the data porvided by ZI
                    data = {k : data[k] for k in self._sweep_values}
                    print('data', data)
                    self.sweep_data.append(data)

                    if (time.time() - start) > self._timeout:
                        # If for some reason the sweep is blocking, force the end of the
                        # measurement
                        print("\nSweep still not finished, forcing finish...")
                        self.sweeper.finish()
                        self._recording = False

                    print("Individual sweep %.2f%% complete. \n" % (progress))
                    self.updateProgress.emit(progress)

                if self.sweeper.finished():
                    self._recording = False
                    progress = 100 # make sure that progess is set 1o 100 because we check that in the old_gui

            else:
                # todo: raise error
                self.stop()
                print('unknown acquisition type!! acquisition stopped')

    def stop(self):
        if self._acquisition_mode == 'sweep':
            self.sweeper.finish()
        self._recording = False

    def poll(self, pollTime, timeout = 500):
        #todo: implement
        '''
        NOT FINISHED!!!!
        Poll the value of input 1 for polltime seconds and return the magnitude of the average data. Timeout is in milisecond.
        :param pollTime:
        :param timeout:
        :return:
        '''
        pass
        # path = '/%s/demods/%d/sample' % (self.device, self.demod_c)
        # self.daq.subscribe(path)
        # flat_dictionary_key = True
        # data = self.daq.poll(pollTime,timeout,1,flat_dictionary_key)
        # R = numpy.sqrt(numpy.square(data[path]['x'])+numpy.square(data[path]['y']))
        # return(numpy.mean(R))



if __name__ == '__main__':

    zi = ZIHF2_v2()


    zi.sweep_settings = {'start': 1e3, 'stop': 1e4, 'samplecount':10}

    zi.run_sweep({'frequency':0})
