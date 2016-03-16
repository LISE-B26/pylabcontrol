import serial

CR = chr(13)

class FW102C:
    def __init__(self, port = 8, timeout = 1):
        # The serial connection should be setup with the following parameters:
        # 1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below
        self.ser = serial.Serial(port = port, baudrate = 115200, timeout = timeout)

    def setPos(self, pos):
        self.ser.write('pos=' + str(pos) + CR)
        posret = self.ser.readline()
        if not posret == ('pos=' + str(pos) + CR):
            message = 'Setting Filter Wheel position failed'
            raise IOError(message)