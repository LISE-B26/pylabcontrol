from src.core import Instrument, Parameter
import visa

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
        self.spec_anal = rm.open_resource(self.parameters['visa_resource'])

    @property
    def _parameters_default(self):
        """
        parameters_default lists the default Parameters used by the Spectrum Analyzer

        Returns: a list of Parameter objects for the parameters associated with the instrument.
        """

        parameters_default = Parameter([
            Parameter('visa_resource', 'USB0::0x0957::0xFFEF::CN0323B356::INSTR', (str),
                      'pyVisa instrument identifier, to make a connection using the pyVisa package.'),
            Parameter('start_frequency', 1.5e9, float, 'start frequency of spectrum analyzer frequency range'),
            Parameter('stop_frequency', 3e9, float, 'stop frequency of spectrum analyzer frequency range')
        ])

        return parameters_default

    def update(self, parameters):
        super(SpectrumAnalyzer, self).update(parameters)
        for key, value in parameters.iteritems:
            if key == 'start_frequency':
                self.start_frequency(value)
            else:
                message = '{0} is not a parameter of {2}'.format(key, self.name)

    def is_connected(self):
        """
        Checks if the instrument is connected.
        Returns: True if connected, False otherwise.

        """
        identification = self.spec_anal.query('*IDN?\n')
        return identification == self.INSTRUMENT_IDENTIFIER

    @property
    def start_frequency(self, start_freq):
        super(SpectrumAnalyzer, self).update({'start_frequency': start_freq})
        response = self.spec_anal.query('SENS:FREQ:START ' + str(start_freq))

if __name__ == '__main__':
    a = SpectrumAnalyzer()
    print a.is_connected()
    print(a.parameters)