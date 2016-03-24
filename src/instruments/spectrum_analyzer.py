from src.core import Instrument, Parameter
import visa
import numpy as np
import matplotlib.pyplot as plt


class SpectrumAnalyzer(Instrument):
    """
    This class provides a python implementation of the Keysight N9320B 9kHz-3.0GHz spectrum analyzer
    with trigger generator.
    """

    INSTRUMENT_IDENTIFIER = u'Keysight Technologies,N9320B,CN0323B356,0B.03.58\n'
    # String returned by spectrum analyzer upon querying it with '*IDN?'

    def __init__(self, name='SpectrumAnalyzer', parameter_list=None):
        """

        Args:
            name (str): optional name of instance of class
            parameter_list (list): list of other values to initialize class with

        """
        super(SpectrumAnalyzer, self).__init__(name, parameter_list)
        rm = visa.ResourceManager()
        self.spec_anal = rm.open_resource(self.settings['visa_resource'])
        self.spec_anal.timeout = 1000
        self.spec_anal.write('*RST\n')

    @property
    def _settings_default(self):
        """
        parameters_default lists the default Parameters used by the Spectrum Analyzer

        Returns: a list of Parameter objects for the parameters associated with the instrument.
        """

        parameters_default = Parameter([
            Parameter('visa_resource', 'USB0::0x0957::0xFFEF::CN0323B356::INSTR', (str),
                      'pyVisa instrument identifier, to make a connection using the pyVisa package.'),
            Parameter('start_frequency', 1e4, float, 'start frequency of spectrum analyzer frequency range'),
            Parameter('stop_frequency', 3e9, float, 'stop frequency of spectrum analyzer frequency range'),
            Parameter('tracking_generator', False, bool, 'toggles the tracking generator'),
            Parameter('connection_timeout', 1000, int, 'the time to wait for a response '
                                                       'from the spectrum analyzer with each query')
        ])

        return parameters_default

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
            else:
                message = '{0} is not a parameter of {2}'.format(key, self.name)

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
        elif probe_name == 'frequency_step':
            return self._get_frequency_step()
        else:
            message = 'no probe with that name exists!'
            raise AttributeError(message)

    @property
    def _probes(self):
        probes = {'start_frequency': 'the lower bound of the frequency sweep',
                  'stop_frequency': 'the upper bound of the frequency sweep',
                  'trace': 'the frequency sweep of the inputted signal',
                  'tracking_generator': 'checks if the tracking generator is on',
                  'bandwidth': 'the curent bandwidth of the spectrum analyzer',
                  'frequency_step': 'the frequency step size for the frequency range'}

    def is_connected(self):
        """
        Checks if the instrument is connected.
        Returns: True if connected, False otherwise.

        """
        identification = self.spec_anal.query('*IDN?\n')
        return identification == self.INSTRUMENT_IDENTIFIER

    def _set_start_frequency(self, start_freq):
        self.spec_anal.write('SENS:FREQ:START ' + str(start_freq))

    def _get_start_frequency(self):
        return float(self.spec_anal.query('SENS:FREQ:START?\n'))

    def _set_stop_frequency(self, stop_freq):
        self.spec_anal.write('SENS:FREQ:STOP ' + str(stop_freq))

    def _get_stop_frequency(self):
        return float(self.spec_anal.query('SENS:FREQ:STOP?\n'))

    def _set_tracking_generator(self, state):
        self.spec_anal.write('OUTPUT ON') if state else self.spec_anal.write('OUTPUT OFF')

    def _get_tracking_generator(self):
        return bool(self.spec_anal.query('OUTPUT?'))

    def _get_trace(self):
        amplitudes = [float(i) for i in str(self.spec_anal.query('TRACE:DATA? TRACE1')).split(',')]
        num_points = len(amplitudes)
        frequencies = np.linspace(start=self._get_start_frequency(), stop=self._get_stop_frequency(),
                                  num=num_points)
        return np.array([(frequencies[i], amplitudes[i])for i in range(num_points)])

    def _get_bandwidth(self):
        return float(self.spec_anal.query('BANDWIDTH?'))

    def _get_frequency_step(self):
        return float(self.spec_anal.query('FREQUENCY:CENTER:STEP?'))


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