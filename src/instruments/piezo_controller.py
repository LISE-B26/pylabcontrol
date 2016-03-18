import serial

from src.core.instruments import *


class PiezoController(Instrument):
    def __init__(self, name, parameters=[]):
        super(PiezoController, self).__init__(name, parameters)
        self._is_connected = False
        try:
            self.connect(port = self.as_dict()['port'], baudrate = self.as_dict()['baudrate'], timeout = self.as_dict()['timeout'])
        except Exception:
            print('No Piezo Controller Detected')
            raise

    def connect(self, port, baudrate, timeout):
            self.ser = serial.Serial(port = port, baudrate = baudrate, timeout = timeout)
            self.ser.write('echo=0\r') #disables repetition of input commands in output
            self.ser.readlines()
            self._is_connected = True

    @property
    def _parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            Parameter('axis', 'x', ['x', 'y', 'z'], '"x", "y", or "z" axis'),
            Parameter('port', 'COM17', (str), 'serial port on which to connect'),
            Parameter('baudrate', 115200, (int), 'baudrate of connection'),
            Parameter('timeout', .1, (float), 'connection timeout'),
            Parameter('voltage', 0.0, (float), 'current voltage'),
            Parameter('voltage_limit', 100, [75, 100, 150], 'maximum voltage')
        ]
        return parameter_list_default

    def __del__(self):
        if self._is_connected:
            self.ser.close()

    def update_parameters(self, parameters_new):
        parameters_new = super(PiezoController, self).update_parameters(parameters_new)
        for key, value in parameters_new.iteritems():
            if key == 'voltage':
                self.set_voltage(value)
            elif key == 'voltage_limit':
                raise EnvironmentError('Voltage limit cannot be set in software. Change physical switch on back of device')

    def set_voltage(self, voltage):
        self.ser.write(self.axis + 'voltage=' + str(voltage) + '\r')
        successCheck = self.ser.readlines()
        # print(successCheck)
        # * and ! are values returned by controller on success or failure respectively
        if(successCheck[0] == '*'):
            print('Voltage set')
        elif(successCheck[0] == '!'):
            message = 'Setting voltage failed. Confirm that device is properly connected and a valid voltage was entered'
            raise ValueError(message)

    @property
    def voltage(self):
        self.ser.write(self.axis + 'voltage?\r')
        xVoltage = self.ser.readline()
        return(float(xVoltage[2:-2].strip()))

    @property
    def voltage_limit(self):
            self.ser.write('vlimit?\r')
            vlimit = self.ser.readline()
            return vlimit[2:-3].strip()

if __name__ == '__main__':
    a = PiezoController('hi')
    print(a.parameters)