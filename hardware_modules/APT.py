#Adopted from:
#https://github.com/mcleung/PyAPT/blob/master/PyAPT.py

# This code controls the stepper motor for the Thorlabs filter wheel
# CODE BROKEN DO NOT USE: device continually disconnects and is otherwise rendered unresponsive

from ctypes import c_long, c_buffer, c_float, windll, pointer

DEVICE_TYPE = 29 # internal identifier for the TST_001 controller
SERIAL_NUMBER_TST001 = 80828901

class TST001:
    def __init__(self, serial_number, device_type):
        self.Connected = False
        self.aptdll = windll.LoadLibrary('C:\\Program Files\\Thorlabs\\APT\\APT Server\\APT.dll')
        self.aptdll.EnableEventDlg(True)
        self.aptdll.APTInit()
        print 'APT initialized'
        self.blCorr = 0.10 #100um backlash correction
        self.serial_number = serial_number
        self.device_type = device_type

    def getSerialNumberByIdx(self, index):
        '''
        Returns the Serial Number of the specified index
        '''
        HWSerialNum = c_long()
        hardwareIndex = c_long(index)
        self.aptdll.GetHWSerialNumEx(self.device_type, hardwareIndex, pointer(HWSerialNum))
        return HWSerialNum

    def getNumberOfHardwareUnits(self):
        '''
        Returns the number of HW units connected that are available to be interfaced
        '''
        numUnits = c_long()
        self.aptdll.GetNumHWUnitsEx(self.device_type, pointer(numUnits))
        return numUnits.value

    def initializeHardwareDevice(self):
        '''
        Initialises the motor.
        You can only get the position of the motor and move the motor after it has been initialised.
        Once initiallised, it will not respond to other objects trying to control it, until released.
        '''
        result = self.aptdll.InitHWDevice(self.serial_number)
        if result == 0:
            self.Connected = True
        # need some kind of error reporting here
        else:
            raise Exception('Connection Failed. Check Serial Number!')
        return True

    def getPos(self):
        '''
        Obtain the current absolute position of the stage
        '''
        if not self.Connected:
            raise Exception('Please connect first! Use initializeHardwareDevice')

        position = c_float()
        self.aptdll.MOT_GetPosition(self.serial_number, pointer(position))
        return position.value

    def getStageAxisInformation(self):
        minimumPosition = c_float()
        maximumPosition = c_float()
        units = c_long()
        pitch = c_float()
        self.aptdll.MOT_GetStageAxisInfo(self.serial_number, pointer(minimumPosition), pointer(maximumPosition), pointer(units), pointer(pitch))
        stageAxisInformation = [minimumPosition.value, maximumPosition.value, units.value, pitch.value]
        return stageAxisInformation

    def mAbs(self, absPosition):
        '''
        Moves the motor to the Absolute position specified
        absPosition    float     Position desired
        '''
        if not self.Connected:
            raise Exception('Please connect first! Use initializeHardwareDevice')
        absolutePosition = c_float(absPosition)
        print('here')
        self.aptdll.MOT_MoveAbsoluteEx(self.serial_number, absolutePosition, True)
        print('there')
        return True

    def mRel(self, relDistance):
        '''
        Moves the motor a relative distance specified
        relDistance    float     Relative position desired
        '''
        if not self.Connected:
            print('Please connect first! Use initializeHardwareDevice')
            #raise Exception('Please connect first! Use initializeHardwareDevice')
        relativeDistance = c_float(relDistance)
        self.aptdll.MOT_MoveRelativeEx(self.serial_number, relativeDistance, True)
        return True

    def cleanUpAPT(self):
        '''
        Releases the APT object
        Use when exiting the program
        '''
        self.aptdll.APTCleanUp()
        self.Connected = False

a = TST001(SERIAL_NUMBER_TST001,DEVICE_TYPE)
a.initializeHardwareDevice()
print(a.getPos())
a.mAbs(.2)
print(a.getPos())
a.cleanUpAPT()
