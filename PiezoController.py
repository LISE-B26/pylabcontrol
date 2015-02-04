# B26 Lab Code
# Last Update: 2/3/15

import serial




class MDT693A:

    def __init__(self, port = 7, timeout = 1):
        # The serial connection should be setup with the following parameters:
        # 1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below
        self.ser = serial.Serial(port = port, baudrate=115200, timeout = timeout)

    def getXVoltage(self):
        assert self.ser.isOpen()

        self.ser.write('XR?\r')
        xVoltage = self.ser.readline()

        return xVoltage


    # closes the connection with the controller
    def closeConnection(self):
        self.ser.close()


if __name__ == '__main__':

    controller = MDT693A()
    print 'The X voltage is ' + controller.getXVoltage()
    controller.closeConnection()