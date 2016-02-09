# clr is python for .net
import clr # run pip install pythonnet
import sys
sys.path.insert(0,"C:\\Program Files\\Thorlabs\\Kinesis\\")

# ctypes DLL load failed: Probably a C++ dll was provided, which is incompatable with ctypes, possibly due to name
# mangling
#ctypes.cdll.LoadLibrary("Thorlabs.MotionControl.TCube.DCServo.dll")

# makes each dll, corresponding to a namespace, avaliable to python at runtime
clr.AddReference('ThorLabs.MotionControl.DeviceManagerCLI')
clr.AddReference('Thorlabs.MotionControl.TCube.DCServoCLI')
clr.AddReference('System')

# imports classes from the namespaces. All read as unresolved references because python doesn't know about the dlls
# until runtime
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.TCube.DCServoCLI import TCubeDCServo
# adds .NET stuctures corresponding to primitives
from System import Decimal, Double



class TDC001:
    '''
    Class to control the thorlabs TDC001 servo. Note that ALL DLL FUNCTIONS TAKING NUMERIC INPUT REQUIRE A SYSTEM.DECIMAL
    VALUE. Check help doc at C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DotNet_API for the DLL api
    '''
    def __init__(self, serial_number = 83832028):
        '''
        Initializes connection to
        :param serial_number: serial number of device as written on physical device. Defaults to 83832028 of TDC001
        :PostState: Initializes device
        '''
        try:
            DeviceManagerCLI.BuildDeviceList()
            serial_number_list = DeviceManagerCLI.GetDeviceList(TCubeDCServo.DevicePrefix)
        except (Exception):
            print("Exception raised by BuildDeviceList")
        if not (str(serial_number) in serial_number_list):
            print(str(serial_number) + " is not a valid serial number")
            raise

        self.device = TCubeDCServo.CreateTCubeDCServo(str(serial_number))
        if(self.device == None):
            print(serial_number + " is not a TCubeDCServo")
            raise

        try:
            self.device.Connect(str(serial_number))
        except Exception:
            print('Failed to open device ' + str(serial_number))
            raise

        if not self.device.IsSettingsInitialized():
            try:
                self.device.WaitForSettingsInitialized(5000)
            except Exception:
                print("Settings failed to initialize")
                raise

        self.device.StartPolling(250)

        motorSettings = self.device.GetMotorConfiguration(str(serial_number))
        currentDeviceSettings = self.device.MotorDeviceSettings

    def move_servo(self, position, velocity = 0):
        '''
        Move servo to given position with given maximum velocity
        :param position: position in mm, ranges from 0-6
        :param velocity: maximum velocity in mm/s, ranges from 0-2.5
        :PostState: servo has moved
        '''
        try:
            if(velocity != 0):
                self.set_velocity(velocity)
            # print("Moving Device to " + str(position))
            self.device.MoveTo(self.Py_Decimal(position), 60000)
        except Exception:
            print("Failed to move to position")
            raise
        # print ("Device Moved")

    def get_position(self):
        '''
        :return: position of servo
        '''
        return self.Undo_Decimal(self.device.Position)

    def set_velocity(self, velocity):
        '''
        :param maximum velocity in mm/s, ranges from 0-2.5
        :PostState: velocity changed in hardware
        '''
        if(velocity != 0):
            velPars = self.device.GetVelocityParams()
            velPars.MaxVelocity = self.Py_Decimal(velocity)
            self.device.SetVelocityParams(velPars)

    def get_velocity(self):
        '''
        :return: maximum velocity setting
        '''
        return self.Undo_Decimal(self.device.GetVelocityParams().MaxVelocity)

    def Py_Decimal(self, value):
        '''
        Casting a python double to System.Decimal results in the Decimal having only integer values, likely due to an
        improper selection of the overloaded Decimal function. Casting it first to System.Double, which always maintains
        precision, then from Double to Decimal, where the proper overloaded function is clear, bypasses this issue
        :param value: a python double
        :return: the input as a System.Decimal
        '''
        return Decimal(Double(value))

    def Undo_Decimal(self, value):
        '''
        Casting back from System.Decimal to a python float fails due to overloading issues, but one can successfully
        cast back to a string. Thus, we use a two-part cast to return to python numeric types
        :param value: a System.Decimal
        :return: the input as a python float
        '''
        return float(str(value))

    def __del__(self):
        '''
        Cleans up TDC001 connection
        :PostState: TDC001 is disconnected
        '''
        self.device.StopPolling()
        self.device.Disconnect()

    def wait_time(self, motor_step):
        # motor_step = 1 corresponds to 1/100 mm, nominally the motor runs at its max speed motor_speed = 2.5 mm/s
        # However, since it has to accelerate, we assume that the aver. speed is only motor_speed = 0.5 mm/s
        # thus the wait time to reach  the position is motor_step / (100  * motor_speed )
        # in addition we add a buffer wait time of 0.2 s

        # motor_step = abs(target_position - self.get_position()
        motor_speed = 0.5

        return motor_step / (100  * motor_speed )+0.2

# Test Code
if __name__ == '__main__':
    # TDC001 serial number is 83832028 as given on physical device
    serial_number = 83832028
    a = TDC001(serial_number)
    print(a.get_position())
    a.move_servo(3.0)
    print(a.get_position())
