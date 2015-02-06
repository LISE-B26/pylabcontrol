# B26 Lab Code
# Last Update: 2/3/15

#To implement: SweepingOut, ReadSweep, FFT, configure channel (offset, amplitude, frequency)

import time
import re
import zhinst.utils as utils
import matplotlib.pyplot as plt
import numpy


class ZIHF2:

    def __init__(self, amplitude, coupling = 0):
        self.daq = utils.autoConnect(8005,1)
        self.device = utils.autoDetect(self.daq)
        self.options = self.daq.getByte('/%s/features/options' % self.device)
         #channel settings
        self.in_c = 0
        self.out_c = 0
        self.demod_c = 0
        self.demod_rate = 10e3
        self.osc_c = 0
        if (not re.match('MF', self.options)):
            self.out_mixer_c = 6
        else:
            self.out_mixer_c = 0

        # Configure the settings relevant to this experiment
        self.exp_setting = [
            ['/%s/sigins/%d/imp50'          % (self.device, self.in_c), 1],
            ['/%s/sigins/%d/ac'             % (self.device, self.in_c), coupling],
            ['/%s/sigins/%d/range'          % (self.device, self.in_c), 2*amplitude],
            ['/%s/demods/%d/order'          % (self.device, self.demod_c), 4],
            ['/%s/demods/%d/rate'           % (self.device, self.demod_c), self.demod_rate],
            ['/%s/demods/%d/harmonic'       % (self.device, self.demod_c), 1],
            ['/%s/demods/%d/phaseshift'     % (self.device, self.demod_c), 0],
            ['/%s/sigouts/%d/on'            % (self.device, self.out_c), 1],
            ['/%s/sigouts/%d/range'         % (self.device, self.out_c), 1],
            ['/%s/sigouts/%d/enables/%d'    % (self.device, self.out_c, self.out_mixer_c), 1],
            ['/%s/sigouts/%d/amplitudes/%d' % (self.device, self.out_c, self.out_mixer_c), amplitude]]

        self.exp_setting.append(['/%s/demods/%d/oscselect' % (self.device, self.demod_c), self.osc_c])
        self.exp_setting.append(['/%s/demods/%d/adcselect' % (self.device, self.demod_c), self.in_c])
        self.exp_setting.append(['/%s/sigins/%d/diff' % (self.device, self.in_c), 0])
        self.exp_setting.append(['/%s/sigouts/%d/add' % (self.device, self.out_c), 0])
        self.daq.set(self.exp_setting)


    def sweep(self, freqStart, freqEnd, samplecount, samplesPerPt, xScale = 0, direction = 0, loopcount = 1, timeout=10000):
        sweeper = self.daq.sweep(timeout)
        sweeper.set('sweep/device', self.device)
        sweeper.set('sweep/start', freqStart)
        sweeper.set('sweep/stop', freqEnd)
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
        timeout = 60  # [s]
        print "Will perform %d sweeps...." % loopcount
        while not sweeper.finished():
            time.sleep(0.2)
            progress = sweeper.progress()
            print "Individual sweep %.2f%% complete.   \r" % (100*progress),
            ## Here we could read intermediate data via
            # data = sweeper.read(True)...
            ## and process it
            # if device in data:
            # ...
            if (time.time() - start) > timeout:
                # If for some reason the sweep is blocking, force the end of the
                # measurement
                print "\nSweep still not finished, forcing finish..."
                sweeper.finish()
        print ""

        # Read the sweep data. This command can also be executed whilst sweeping
        # (before finished() is True), in this case sweep data up to that time point
        # is returned. It's still necessary still need to issue read() at the end to
        # fetch the rest.
        return_flat_dict = True
        data = sweeper.read(return_flat_dict)
        sweeper.unsubscribe(path)

        # Stop the sweeper thread and clear the memory
        sweeper.clear()

        # Check the dictionary returned is non-empty
        assert data, "read() returned an empty data dictionary, did you subscribe to any paths?"
        # note: data could be empty if no data arrived, e.g., if the demods were
        # disabled or had rate 0
        assert path in data, "no sweep data in data dictionary: it has no key '%s'" % path
        self.samples = data[path]
        print "sample contains %d sweeps" % len(self.samples)

    def plot(self):
        plt.figure()
        plt.interactive(True)
        plt.hold(True)
        for i in range(0, len(self.samples)):
            # please note: the "[i][0]" indexing is known issue to be fixed in
            # an upcoming release (there shouldn't be an additional [0])
            frequency = self.samples[i][0]['frequency']
            R = numpy.sqrt(self.samples[i][0]['x']**2 + self.samples[i][0]['y']**2)
            plt.loglog(frequency, R)
        plt.grid(True)
        plt.title('Results of %d sweeps' % len(self.samples))
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude (V_RMS)')
        plt.autoscale()
        plt.draw()
        plt.show()

if __name__ == '__main__':
    zi = ZIHF2(.1)
    zi.sweep(1e6, 50e6, 100, 10, xScale = 0)
    zi.plot()
