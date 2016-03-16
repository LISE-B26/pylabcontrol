import serial
import time
import re

class Lakeshore335:
    def __init__(self, port = 11, baudrate = 57600, timeout = .1):
        self.ser = serial.Serial(port = port, baudrate=baudrate, timeout = timeout)
        self.ser.close()

    def get_temp(self):
        self.ser.open()
        time.sleep(.1)
        self.ser.write("KRDG? A\r\n")
        xx = str(self.ser.readlines())
        yy =xx.split('\\r\\x8a')[0]
        #print(yy)
        y = re.findall('\d+|ae', yy)
        y[y.index('ae')] = '.'
        y = ''.join(y)
        #print(yy)
        #for y in yy:
        #    print(y)

        #print('d3'.decode("hex"))
        self.ser.close()

        #print(y)
        return y


#a = Lakeshore335()
#print(a.get_temp())
