# B26 Lab Code
# REquirements: Assumes that Thorlabs Piezo Controller MDT693A is connected via serial port,
# by default on port 2 adn baudrate 115200
# Last Update: 2/3/15

# TROUBLESHOOTING:
# if no commands are accepted, first try unplugging and replugging connection

import serial
import time

class MDT693A:

    SYSTEM_OFFSET = 0.6 # volts


    def __init__(self, outputAxis, port = 3, baudrate = 115200, timeout = .1):
        # The serial connection should be setup with the following parameters:
        # 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below

        if (outputAxis is not 'X' and outputAxis is not 'Y' and outputAxis is not 'Z'):
            message = 'Piezo Controller Axis not correctly defined; must be either \'X\', \'Y\', or \'Z\''
            raise ValueError(message)

        self.axis = outputAxis.upper()

        self.ser = serial.Serial(port = port, baudrate=baudrate, timeout = timeout)
        self.ser.close()
        self.manualOffset = -1
        self.getManualOffset()

    # get the voltage on the port 'axis' of the piezo controller
    def getVoltage(self):

        if not self.ser.isOpen():
            self.ser.open()

        self.ser.write(self.axis + 'R?\r')
        xVoltage = self.ser.readline()

        xVoltage = xVoltage[6:-2].strip()

        self.ser.close()

        return float(xVoltage)

    # set the voltage on the port 'axis' of the piezo controller
    def setVoltage(self, voltage):

        if not self.ser.isOpen():
            self.ser.open()

        #print 'Setting voltage for ' + self.axis + ' axis: ' + str(voltage - self.manualOffset)
        if (self.manualOffset > voltage):
            message = 'Voltage to be set is less than manually set voltage; cannot change to desired value.' \
                      'Manually set voltage: %s V. Voltage desired: %s V.' % (str(self.manualOffset), str(voltage))
            raise ValueError(message)

        elif (self.SYSTEM_OFFSET > voltage):
            message = 'The controller has a small bias and cannot go below ' + str(self.SYSTEM_OFFSET) + ' V .'
            raise ValueError(message)

        else:
            self.ser.write('%s%f\r'%(self.axis + 'V', voltage - self.manualOffset))
            self.ser.readline()

        self.ser.close()

    # gets the manual offset on the output port 'axis'.
    # This is an additional voltage added via the physical front panel knob
    def getManualOffset(self):

        if not self.ser.isOpen():
            self.ser.open()

        curr_voltage = self.getVoltage()
        self.setSoftwareVoltage(0)
        self.manualOffset = self.getVoltage() - self.SYSTEM_OFFSET
        self.setSoftwareVoltage(curr_voltage - self.manualOffset)

        self.ser.close()
        return self.manualOffset

    def setSoftwareVoltage(self, voltage):
        if not self.ser.isOpen():
            self.ser.open()

        self.ser.write('%s%f\r'%(self.axis + 'V', voltage))
        self.ser.readline()

        self.ser.close()


    # closes the connection with the controller
    def closeConnection(self):
        self.ser.close()

class MDT693B:
    def __init__(self, outputAxis, port = 10, baudrate = 115200, timeout = .1):
        # The serial connection should be setup with the following parameters:
        # 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below

        if (outputAxis is not 'X' and outputAxis is not 'Y' and outputAxis is not 'Z'):
            message = 'Piezo Controller Axis not correctly defined; must be either \'X\', \'Y\', or \'Z\''
            raise ValueError(message)

        self.axis = outputAxis.lower()

        self.ser = serial.Serial(port = port, baudrate=baudrate, timeout = timeout)
        self.ser.write('echo=0\r') #disables repetition of input commands in output
        self.ser.readlines()
        self.ser.close()

    # get the voltage on the port 'axis' of the piezo controller
    def getVoltage(self):

        if not self.ser.isOpen():
            self.ser.open()

        self.ser.write(self.axis + 'voltage?\r')
        xVoltage = self.ser.readline()

        xVoltage = xVoltage[2:-2].strip()

        self.ser.close()

        return float(xVoltage)

    # set the voltage on the port 'axis' of the piezo controller
    def setVoltage(self, voltage):

        if (not isinstance(voltage,(int, long, float, complex))):
            message = 'Setting voltage failed. Entered voltage must be a number'
            raise ValueError(message)

        if not self.ser.isOpen():
            self.ser.open()

        self.ser.write(self.axis + 'voltage=' + str(voltage) + '\r')
        successCheck = self.ser.readlines()
        if(successCheck[0] == '*'):
            print('Voltage set')
        elif(successCheck[0] == '!'):
            self.ser.write('vlimit?\r')
            vlimit = self.ser.readline()
            vlimit = vlimit[2:-3].strip()
            if(voltage > int(vlimit)):
                message = 'Setting voltage failed. Maximum voltage exceeded. Check limit switch on back of device.'
                raise ValueError(message)
            elif(voltage < 0):
                message = 'Setting voltage failed. Negative voltage is invalid'
                raise ValueError(message)
            else:
                message = 'Setting voltage failed. Confirm that device is properly connected and a valid voltage was entered'
                raise ValueError(message)

        self.ser.close()

    # closes the connection with the controller
    def closeConnection(self):
        self.ser.close()


if __name__ == '__main__':
    """
    xController = MDT693A('X')
    yController = MDT693A('Y')
    zController = MDT693A('Z')
    initialVoltages = [xController.getVoltage(), yController.getVoltage(), zController.getVoltage()]
    print 'The X voltage is ' + str(initialVoltages[0])
    print 'The Y voltage is ' + str(initialVoltages[1])
    print 'The Z voltage is ' + str(initialVoltages[2])

    testVoltages = [5.0, 10.0, 15.0]
    print 'Setting x, y, and z voltages to 5, 10, and 15, respectively...'
    xController.setVoltage(testVoltages[0])
    yController.setVoltage(testVoltages[1])
    zController.setVoltage(testVoltages[2])

    print 'The X voltage is now ' + str(xController.getVoltage())
    print 'The Y voltage is now ' + str(yController.getVoltage())
    print 'The Z voltage is now ' + str(zController.getVoltage())

    print 'Setting Voltages back...'
    xController.setVoltage(initialVoltages[0])
    xController.setVoltage(initialVoltages[1])
    yController.setVoltage(initialVoltages[2])
    #time.sleep(10)
    currentVoltages = [xController.getVoltage(), yController.getVoltage(), zController.getVoltage()]
    print currentVoltages

    if abs(initialVoltages[0] - currentVoltages[0]) < 1 and abs(initialVoltages[1] - currentVoltages[1]) < 1 and abs(initialVoltages[2] - currentVoltages[2]) < 1:
        print 'Successfully set voltages back to original values'
    else:
        print 'Was not able to set voltages back to original values. /_\X = %f, /_\Y = %f, /_\Z = %f' % (initialVoltages[0] - currentVoltages[0], initialVoltages[1] - currentVoltages[1], initialVoltages[2] - currentVoltages[2])

    print 'The X manual offset is ' + str(xController.getManualOffset())
    print 'The Y manual offset is ' + str(yController.getManualOffset())
    print 'The Z manual offset is ' + str(zController.getManualOffset())

    for i in xrange(80):
        yController.setVoltage(i+1)
        print 'Set the voltage to %s, read voltage %s' % (str(i+1), str(yController.getVoltage()))


    yController.setVoltage(10)

    """

    #xController.setVoltage(58.6)
    #while True:
    #print zController.getVoltage()
    #    time.sleep(5)
    #    zController.setVoltage(95)
    #    time.sleep(5)