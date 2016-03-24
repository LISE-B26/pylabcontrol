from src.core import Instrument, Parameter
import visa
import numpy as np
import time
import matplotlib.pyplot as plt


class SpectrumAnalyzer(Instrument):
    """
    This class provides a python implementation of the Keysight N9320B 9kHz-3.0GHz spectrum analyzer
    with trigger generator.
    """

    _INSTRUMENT_IDENTIFIER = u'Keysight Technologies,N9320B,CN0323B356,0B.03.58\n'
    # String returned by spectrum analyzer upon querying it with '*IDN?'

    _DEFAULT_SETTINGS = \
        Parameter([
            Parameter('visa_resource', 'USB0::0x0957::0xFFEF::CN0323B356::INSTR', (str),
                      'pyVisa instrument identifier, to make a connection using the pyVisa package.'),
            Parameter('start_frequency', 0.0, float, 'start frequency of spectrum analyzer frequency range'),
            Parameter('stop_frequency', 3e9, float, 'stop frequency of spectrum analyzer frequency range'),
            Parameter('output_on', True, bool, 'toggles the tracking generator'),
            Parameter('connection_timeout', 1000, int, 'the time to wait for a response '
                                                       'from the spectrum analyzer with each query'),
            Parameter('output_power', 10.0, float, 'the output power (in dBm) of the tracking generator')
        ])

    def __init__(self, name='SpectrumAnalyzer', settings=None):
        """

        Args:
            name (str): optional name of instance of class
            settings (list): list of other values to initialize class with

        """
        super(SpectrumAnalyzer, self).__init__(name, settings)
        rm = visa.ResourceManager()
        self.spec_anal = rm.open_resource(self.settings['visa_resource'])
        self.spec_anal.timeout = self.settings['connection_timeout']
        self.spec_anal.write('*RST\n')

    def update(self, settings):
        super(SpectrumAnalyzer, self).update(settings)

        for key, value in settings.iteritems():
            if key == 'start_frequency':
                self._set_start_frequency(value)
                print 'hi'
            elif key == 'stop_frequency':
                self._set_stop_frequency(value)
            elif key == 'tracking_generator':
                self._set_tracking_generator(value)
            elif key == 'output_power':
                self._set_output_power(value)
            else:
                message = '{0} is not a parameter of {2}'.format(key, self.name)

    @property
    def _probes(self):
        probes = {'start_frequency': 'the lower bound of the frequency sweep',
                  'stop_frequency': 'the upper bound of the frequency sweep',
                  'trace': 'the frequency sweep of the inputted signal',
                  'tracking_generator': 'checks if the tracking generator is on',
                  'bandwidth': 'the curent bandwidth of the spectrum analyzer',
                  'output_power': 'the power of the tracking generator'}

    def read_probes(self, probe_name):
        if probe_name == 'start_frequency':
            return self._get_start_frequency()
        elif probe_name == 'stop_frequency':
            return self._get_stop_frequency()
        elif probe_name == 'trace':
            return self._get_trace()
        elif probe_name == 'tracking_generator':
            return self._get_tracking_generator()
        elif probe_name == 'bandwidth':
            return self._get_bandwidth()
        elif probe_name == 'output_power':
            return self._get_output_power()
        else:
            message = 'no probe with that name exists!'
            raise AttributeError(message)

    def is_connected(self):
        """
        Checks if the instrument is connected.
        Returns: True if connected, False otherwise.

        """
        identification = self.spec_anal.query('*IDN?\n')
        return identification == self._INSTRUMENT_IDENTIFIER

    def _set_start_frequency(self, start_freq):
        self.spec_anal.write('SENS:FREQ:START ' + str(start_freq))

    def _get_start_frequency(self):
        return float(self.spec_anal.query('SENS:FREQ:START?\n'))

    def _set_stop_frequency(self, stop_freq):
        self.spec_anal.write('SENS:FREQ:STOP ' + str(stop_freq))

    def _get_stop_frequency(self):
        return float(self.spec_anal.query('SENS:FREQ:STOP?\n'))

    def _set_output(self, state):
        self.spec_anal.write('OUTPUT ON') if state else self.spec_anal.write('OUTPUT OFF')

    def _get_output(self):
        return bool(self.spec_anal.query('OUTPUT?'))

    def _get_trace(self):
        amplitudes = [float(i) for i in str(self.spec_anal.query('TRACE:DATA? TRACE1')).split(',')]
        num_points = len(amplitudes)
        frequencies = np.linspace(start=self.start_frequency, stop=self.stop_frequency,
                                  num=num_points)
        return np.array([(frequencies[i], amplitudes[i])for i in range(num_points)])

    def _get_bandwidth(self):
        return float(self.spec_anal.query('BANDWIDTH?'))

    def _get_output_power(self):
        return self.spec_anal.query('SOURCE:POWER?')

    def set_output_power(self, power):
        return self.spec_anal.write('SOURCE:POWER ' + str(power))



if __name__ == '__main__':

        spec_anal = SpectrumAnalyzer()

        spec_anal.start_frequency = 200001

        print spec_anal._get_start_frequency()
        print spec_anal.start_frequency
        print spec_anal.settings['start_frequency']

        spec_anal.settings['start_frequency'] = 200222
        print('======')
        print spec_anal._get_start_frequency()
        print spec_anal.start_frequency
        print spec_anal.settings['start_frequency']

        spec_anal.update({'start_frequency': 200222})
        print('======')
        print spec_anal._get_start_frequency()
        print spec_anal.start_frequency
        print spec_anal.settings['start_frequency']
