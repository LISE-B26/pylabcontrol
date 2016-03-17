import serial
CR = chr(13)


class SMC100:
    def __init__(self, port = 4, timeout = 1):
        # The serial connection should be setup with the following parameters:
        # 1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below
        self.ser = serial.Serial(port = port, baudrate = 115200, timeout = timeout)
        self.ser.write('1ID?')
        temp = self.ser.readlines()
        print(temp)

if __name__ == '__main__':
    a = SMC100()