import visa

from src.core.instruments import *


class MicrowaveGenerator(Instrument):
    def __init__(self, name, parameters = []):
        super(MicrowaveGenerator, self).__init__(name, parameters)
        self._is_connected = False
        try:
            rm = visa.ResourceManager()
            self.srs = rm.open_resource(u'GPIB' + str(self.as_dict()['GPIB_num']) + '::' + str(self.as_dict()['port']) + '::INSTR')
            self.srs.query('*IDN?') # simple call to check connection
        except Exception:
            print('No Piezo Controller Detected')

    #Doesn't appear to be necessary, can't make two sessions conflict, rms may share well
    # def __del__(self):
    #     self.srs.close()

    @property
    def _parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('port', 27, (int), 'GPIB port on which to connect'),
            Parameter('GPIB_num', 0, (int), 'GPIB device on which to connect'),
            Parameter('ENBR', False, (bool), 'Type-N output enabled'),
            Parameter('FREQ', 3e9, (int, float, str), 'frequency in Hz, or with label in other units ex 300 MHz'),
            Parameter('AMPR', -60, (int, float), 'Type-N amplitude in dBm'),
            Parameter('PHAS', 0, (int, float), 'output phase'),
            Parameter('MODL', True, (bool), 'enable modulation'),
            Parameter('TYPE', 1, [0,1,2,3,4,5,6], 'Modulation Type: 0= AM, 1=FM, 2= PhaseM, 3= Freq sweep, 4= Pulse, 5 = Blank, 6=IQ'),
            Parameter('MFNC', 5, [1,2,3,4,5], 'Modulation Function: 0=Sine, 1=Ramp, 2=Triangle, 3=Square, 4=Noise, 5=External'),
            Parameter('PFNC', 5, [3,4,5], 'Pulse Modulation Function: 3=Square, 4=Noise(PRBS), 5=External'),
            Parameter('FDEV', '32 MHz', (int, float, str), 'Width of deviation from center frequency in FM')
        ]
        return parameter_list_default

    def update_parameters(self, parameters_new):
        parameters_new = super(MicrowaveGenerator, self).update_parameters(parameters_new)
        for key, value in parameters_new.iteritems():
            if not(key == 'port' or key == 'GPIB_num'):
                if type(self.as_dict()[key]) == bool: #converts booleans, which are more natural to store for on/off, to
                    value = int(value)                #the integers used internally in the SRS
                self.srs.write(key + ' ' + str(value))

    def read_probes(self, name):
        if (name == 'port' or name == 'GPIB_num'):
            return self.as_dict()[str(name)]
        elif name in self.as_dict():
            return self.srs.query(name + '?')
        else:
            raise KeyError