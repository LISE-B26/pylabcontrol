# clr is python for .net
import clr # run pip install pythonnet
import sys
from src.core.read_write_functions import get_dll_config_path

sys.path.insert(0,get_dll_config_path('KINESIS_DLL_PATH'))

from src.core.instruments import *

# ctypes DLL load failed: Probably a C++ dll was provided, which is incompatable with ctypes, possibly due to name
# mangling. Instead, we use the .net framework with python for .net to interface with the dll
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

class TDC001(Instrument):
    '''
    Class to control the thorlabs TDC001 servo. Note that ALL DLL FUNCTIONS TAKING NUMERIC INPUT REQUIRE A SYSTEM.DECIMAL
    VALUE. Check help doc at C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.DotNet_API for the DLL api
    '''

    _DEFAULT_SETTINGS = Parameter([
        Parameter('serial_number', 83832028, int, 'serial number written on device'),
        Parameter('position', 0, float, 'servo position (from 0 to 6 in mm)'),
        Parameter('velocity', 0, float, 'servo maximum velocity in mm/s')
    ])

    def __init__(self, name = None, settings = None):
        super(TDC001, self).__init__(name, settings)
        try:
            DeviceManagerCLI.BuildDeviceList()
            serial_number_list = DeviceManagerCLI.GetDeviceList(TCubeDCServo.DevicePrefix)
        except (Exception):
            print("Exception raised by BuildDeviceList")
        if not (str(self.settings['serial_number']) in serial_number_list):
            print(str(self.settings['serial_number']) + " is not a valid serial number")
            raise

        self.device = TCubeDCServo.CreateTCubeDCServo(str(self.settings['serial_number']))
        if(self.device == None):
            print(self.settings['serial_number'] + " is not a TCubeDCServo")
            raise

        try:
            self.device.Connect(str(self.settings['serial_number']))
        except Exception:
            print('Failed to open device ' + str(self.settings['serial_number']))
            raise

        if not self.device.IsSettingsInitialized():
            try:
                self.device.WaitForSettingsInitialized(5000)
            except Exception:
                print("Settings failed to initialize")
                raise

        self.device.StartPolling(250)

        motorSettings = self.device.GetMotorConfiguration(str(self.settings['serial_number']))
        currentDeviceSettings = self.device.MotorDeviceSettings

    def update(self, settings):
        super(TDC001, self).update(settings)
        for key, value in settings.iteritems():
            if key == 'position':
                self._move_servo(value)
            elif key == 'velocity':
                self._set_velocity(value)

    @property
    def _PROBES(self):
        return{
            'position': 'servo position in mm',
            'velocity': 'servo velocity in mm/s'
        }

    def read_probes(self, key):
        assert key in self._PROBES.keys()
        assert isinstance(key, str)

        #query always returns string, need to cast to proper return type
        if key in ['position']:
            return self._get_position()
        elif key in ['velocity']:
            return self._get_velocity()

    @property
    def is_connected(self):
        DeviceManagerCLI.BuildDeviceList()
        return(str(self.settings['serial_number']) in DeviceManagerCLI.GetDeviceList(TCubeDCServo.DevicePrefix))

    def __del__(self):
        '''
        Cleans up TDC001 connection
        :PostState: TDC001 is disconnected
        '''
        self.device.StopPolling()
        self.device.Disconnect()

    def goto_home(self):
        try:
            self.device.Home(60000)
        except Exception:
            print("Failed to move to position")
            raise

    def _move_servo(self, position, velocity = 0):
        '''
        Move servo to given position with given maximum velocity
        :param position: position in mm, ranges from 0-6
        :param velocity: maximum velocity in mm/s, ranges from 0-2.5
        :PostState: servo has moved
        '''
        try:
            if(velocity != 0):
                self._set_velocity(velocity)
            # print("Moving Device to " + str(position))
            self.device.MoveTo(self._Py_Decimal(position), 60000)
        except Exception:
            print("Failed to move to position")
            raise

    def _get_position(self):
        '''
        :return: position of servo
        '''
        return self._Undo_Decimal(self.device.Position)

    def _set_velocity(self, velocity):
        '''
        :param maximum velocity in mm/s, ranges from 0-2.5
        :PostState: velocity changed in hardware
        '''
        if(velocity != 0):
            velPars = self.device.GetVelocityParams()
            velPars.MaxVelocity = self._Py_Decimal(velocity)
            self.device.SetVelocityParams(velPars)

    def _get_velocity(self):
        '''
        :return: maximum velocity setting
        '''
        return self._Undo_Decimal(self.device.GetVelocityParams().MaxVelocity)



    def _Py_Decimal(self, value):
        '''
        Casting a python double to System.Decimal results in the Decimal having only integer values, likely due to an
        improper selection of the overloaded Decimal function. Casting it first to System.Double, which always maintains
        precision, then from Double to Decimal, where the proper overloaded function is clear, bypasses this issue
        :param value: a python double
        :return: the input as a System.Decimal
        '''
        return Decimal(Double(value))

    def _Undo_Decimal(self, value):
        '''
        Casting back from System.Decimal to a python float fails due to overloading issues, but one can successfully
        cast back to a string. Thus, we use a two-part cast to return to python numeric types
        :param value: a System.Decimal
        :return: the input as a python float
        '''
        return float(str(value))

if __name__ == '__main__':
    a = TDC001()
    a.is_connected