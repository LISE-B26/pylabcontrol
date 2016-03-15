import serial
from instruments import *


class Piezo_Controller(Instrument):
    def __init__(self, name, parameters = []):
        super(Piezo_Controller, self).__init__(name, parameters)
        self._is_connected = False
        try:
            self.ser = serial.Serial(port = self.parameters_dict['port'], baudrate = self.parameters_dict['baudrate'], timeout = self.parameters_dict['timeout'])
            self.ser.write('echo=0\r') #disables repetition of input commands in output
            self.ser.readlines()
            self._is_connected = True
        except Exception:
            print('No Piezo Controller Detected')

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('axis', 'x', (str), '"x", "y", or "z" axis'),
            Parameter('port', 'COM17', (str), 'serial port on which to connect'),
            Parameter('baudrate', 115200, (int), 'baudrate of connection'),
            Parameter('timeout', .1, (float), 'connection timeout'),
            Parameter('voltage', 0.0, (float), 'current voltage')
        ]
        return parameter_list_default

    def __del__(self):
        if self._is_connected:
            self.ser.close()

a = Piezo_Controller('PC')
print(a.parameters)