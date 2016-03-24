import visa
import pyvisa.errors

from src.core.instruments import *


class MicrowaveGenerator(Instrument):
    def __init__(self, name = None, settings = None):
        super(MicrowaveGenerator, self).__init__(name, settings)
        try:
            rm = visa.ResourceManager()
            self.srs = rm.open_resource(u'GPIB' + str(self._parameters['GPIB_num']) + '::' + str(self._parameters['port']) + '::INSTR')
            self.srs.query('*IDN?') # simple call to check connection
        except pyvisa.errors.VisaIOError:
            print('No Piezo Controller Detected')

    #Doesn't appear to be necessary, can't manually make two sessions conflict, rms may share well
    # def __del__(self):
    #     self.srs.close()

    @property
    def _settings_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameters_default = Parameter([
            Parameter('port', 27, int, 'GPIB port on which to connect'),
            Parameter('GPIB_num', 0, int, 'GPIB device on which to connect'),
            Parameter('ENBR', False, bool, 'Type-N output enabled'),
            Parameter('FREQ', 3e9, float, 'frequency in Hz, or with label in other units ex 300 MHz'),
            Parameter('AMPR', -60, float, 'Type-N amplitude in dBm'),
            Parameter('PHAS', 0, float, 'output phase'),
            Parameter('MODL', True, bool, 'enable modulation'),
            Parameter('TYPE', 1, [0,1,2,3,4,5,6], 'Modulation Type: 0= AM, 1=FM, 2= PhaseM, 3= Freq sweep, 4= Pulse, 5 = Blank, 6=IQ'),
            Parameter('MFNC', 5, [1,2,3,4,5], 'Modulation Function: 0=Sine, 1=Ramp, 2=Triangle, 3=Square, 4=Noise, 5=External'),
            Parameter('PFNC', 5, [3,4,5], 'Pulse Modulation Function: 3=Square, 4=Noise(PRBS), 5=External'),
            Parameter('FDEV', 32e6, float, 'Width of deviation from center frequency in FM')
        ])
        return parameters_default

    def update(self, settings):
        super(MicrowaveGenerator, self).update(settings)
        for key, value in settings.iteritems():
            if not (key == 'port' or key == 'GPIB_num'):
                if type(self._parameters.valid_values[key]) == bool: #converts booleans, which are more natural to store for on/off, to
                    value = int(value)                #the integers used internally in the SRS
                self.srs.write(key + ' ' + str(value))

    @property
    def _probes(self):
        return{
            'ENBR': 'if type-N output is enabled',
            'FREQ': 'frequency of output in Hz',
            'AMPR': 'type-N amplitude in dBm',
            'PHAS': 'phase',
            'MODL': 'is modulation enabled',
            'TYPE': 'Modulation Type: 0= AM, 1=FM, 2= PhaseM, 3= Freq sweep, 4= Pulse, 5 = Blank, 6=IQ',
            'MFNC': 'Modulation Function: 0=Sine, 1=Ramp, 2=Triangle, 3=Square, 4=Noise, 5=External',
            'PFNC': 'Pulse Modulation Function: 3=Square, 4=Noise(PRBS), 5=External',
            'FDEV': 'Width of deviation from center frequency in FM'
        }

    def read_probes(self, key):
        assert key in self._probes.keys()

        #query always returns string, need to cast to proper return type
        if key in ['ENBR', 'MODL']:
            value = self.srs.query(key + '?')
            if value == 1:
                value = True
            elif value == 0:
                value = False
        elif key in ['TYPE','MFNC','PFNC']:
            value = int(self.srs.query(key + '?'))
        else:
            value = float(self.srs.query(key + '?'))

        return value

    @property
    def is_connected(self):
        try:
            self.srs.query('*IDN?') # simple call to check connection
            return True
        except pyvisa.errors.VisaIOError:
            return False

if __name__ == '__main__':
    a = MicrowaveGenerator()
    print(a.FREQ)