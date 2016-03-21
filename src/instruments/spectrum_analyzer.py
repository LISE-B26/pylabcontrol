from src.core import Instrument, Parameter


class SpectrumAnalyzer(Instrument):
    """
    This class provides a python implementation of the Keysight N9320B 9kHz-3.0GHz spectrum analyzer
    with trigger generator.
    """
    try:
        import visa
        _is_connected = True
    except ImportError:
        # make a fake ZI instrument
        _is_connected = False
    except:
        raise


    INSTRUMENT_IDENTIFIER = 'Keysight Technologies,N9320B,CN0323B356,0B.03.58'
    # String returned by spectrum analyzer upon querying it with '*IDN?'

    def __init__(self, name='SpectrumAnalyzer', parameter_list=[]):
        """

        Args:
            name (str): optional name of instance of class
            parameter_list (list): list of other values to initialize class with

        """
        super(SpectrumAnalyzer, self).__init__(name, parameter_list)
        if self._is_connected:
            self.rm = visa.ResourceManager()
            self.spec_anal = self.rm.open_resource(self.visa_resource)
        else:
            self.rm = None
            self.spec_anal = None
    def parameters_default(self):
        """
        parameters_default lists the default Parameters used by the Spectrum Analyzer

        Returns: a list of Parameter objects for the parameters associated with the instrument.
        """

        parameter_list_default = [
            Parameter('visa_resource', 'USB0::0x0957::0xFFEF::CN0323B356::INSTR', (str),
                      'pyVisa instrument identifier, ''to make a connection using the pyVisa package.'),
            Parameter('start_frequency', 1.5e9, (int), 'start frequency of spectrum analyzer frequency range'),
            Parameter('stop_frequency', 3e9, (int), 'stop frequency of spectrum analyzer frequency range')
        ]

        return parameter_list_default

    def is_connected(self):
        """
        Checks if the instrument is connected.
        Returns: True if connected, False otherwise.

        """
        identification = self.spec_anal.query('*IDN?\n')
        return identification == self.INSTRUMENT_IDENTIFIER
