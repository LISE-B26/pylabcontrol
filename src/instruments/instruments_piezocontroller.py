import serial

from src.core.instruments import *


class Piezo_Controller(Instrument):
    def __init__(self, name, parameters = []):
        super(Piezo_Controller, self).__init__(name, parameters)
        self._is_connected = False
        try:
            self.connect(port = self.as_dict()['port'], baudrate = self.as_dict()['baudrate'], timeout = self.as_dict()['timeout'])
        except Exception:
            print('No Piezo Controller Detected')

    def connect(self, port, baudrate, timeout):
            self.ser = serial.Serial(port = port, baudrate = baudrate, timeout = timeout)
            self.ser.write('echo=0\r') #disables repetition of input commands in output
            self.ser.readlines()
            self._is_connected = True

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
            Parameter('voltage', 0.0, (int, float), 'current voltage'),
            Parameter('voltage_limit', 100, [75, 100, 150], 'maximum voltage')
        ]
        return parameter_list_default

    def __del__(self):
        if self._is_connected:
            self.ser.close()

    def update_parameters(self, parameters_new):
        parameters_new = super(Piezo_Controller, self).update_parameters(parameters_new)
        for key, value in parameters_new.iteritems():
            if key == 'port' or key == 'baudrate' or key == 'timeout':
                if self._is_connected:
                       self.ser.close()
                self.connect(port = self.parameters_dict['port'], baudrate = self.parameters_dict['baudrate'], timeout = self.parameters_dict['timeout'])
            elif key == 'voltage':
                self.set_voltage(value)

    def set_voltage(self, voltage):
        self.ser.write(self.axis + 'voltage=' + str(voltage) + '\r')
        #self.ser.write(self.parameters_dict['axis'] + 'voltage=' + str(voltage) + '\r')
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



a = Piezo_Controller('PC')
a.axis = 'y'
print(a.voltage)
a.voltage = 25
print(a.parameters)
print(a.voltage)