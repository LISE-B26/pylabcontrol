import ctypes
import time
import warnings
from src.core.read_write_functions import get_dll_config_path
from src.core.instruments import Instrument, Parameter

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double

#define built-in error codes
NCB_Ok = 0
NCB_Error = -1
NCB_Timeout = 1
NCB_NotConnected = 2
NCB_DriverError = 3
NCB_BootIgnored = 4
NCB_FileNotFound = 5
NCB_InvalidParam = 6
NCB_DeviceLocked = 7
NCB_NotSpecifiedParam = 8

# converts x,y,z to axis number in controller
axis_x = int32(1)
axis_y = int32(2)
axis_z = int32(0)

# c struct used as return type for some old_functions
class PositionerInfo(ctypes.Structure):
    _fields_ = [(("id"), ctypes.c_int32), (("locked"), ctypes.c_bool)]

class Attocube(Instrument):
    '''
    Class to control an attocube using a supplied controller. Has been tested on an
    ANC350 controlling a stack of two ANPx101res and one ANPz101res, but it should
    work with any controllers supporting the same low level dll commands if the path
    to the dll is reset.
    Note that we use the 1.5 version of the dll, the 2.0 version cannot be read properly
    and may be written in a non-ctypes compatible language
    '''

    _DEFAULT_SETTINGS = Parameter([
        Parameter('x',
                  [
                      Parameter('on', False, [True, False], 'x axis on'),
                      Parameter('pos', 0.0, float, 'x axis position in um'),
                      Parameter('voltage', 30, float, 'voltage on x axis'),
                      Parameter('freq', 1000, float, 'x frequency in Hz')
                  ]
                  ),
        Parameter('y',
                  [
                      Parameter('on', False, [True, False], 'y axis on'),
                      Parameter('pos', 0, float, 'y axis position in um'),
                      Parameter('voltage', 30, float, 'voltage on y axis'),
                      Parameter('freq', 1000, float, 'y frequency in Hz')
                  ]
                  ),
        Parameter('z',
                  [
                      Parameter('on', False, [True, False], 'z axis on'),
                      Parameter('pos', 0, float, 'x axis position in um'),
                      Parameter('voltage', 30, float, 'voltage on x axis'),
                      Parameter('freq', 1000, float, 'x frequency in Hz')
                  ]
                  )
    ])

    def __init__(self, name = None, settings = None):
        #COMMENT_ME
        super(Attocube, self).__init__(name, settings)
        try:
            # self.attocube = ctypes.WinDLL('C:/Users/Experiment/Downloads/attocube/Software/ANC350_Software_v1.5.15/ANC350_DLL/Win_64Bit/src/anc350v2.dll')
            self.attocube = ctypes.WinDLL(get_dll_config_path('ATTOCUBE_DLL_PATH'))
            dll_detected = True
        except WindowsError:
            # make a fake Attocube instrument
            dll_detected = False
            warnings.warn("Attocube DLL not found. If it should be present, check the path.")
        if dll_detected == True:
            try:
                self.pi = PositionerInfo()
                dev_count = self.attocube.PositionerCheck(ctypes.byref(self.pi))
                device_handle = int32()
                self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
                self._check_error(self.attocube.PositionerClose(device_handle))
            except Exception:
                print('Attocube not detected. Check connection.', UserWarning)

    def update(self, settings):
        '''
        Updates the internal settings, as well as turning the attocube channel on or off, updating
        voltage or frequency, or moving to the given position
        Args:
            settings: a dictionary in the same form as settings with the new values
        '''
        super(Attocube, self).update(settings)
        for key, value in settings.iteritems():
            if isinstance(value, dict) and key in ['x', 'y', 'z']:
                for sub_key, sub_value in sorted(value.iteritems()):
                    if sub_key == 'on':
                        self._toggle_axis(self._convert_axis(key), sub_value)
                    elif sub_key == 'pos':
                        self._move_absolute(self._convert_axis(key), sub_value)
                    elif sub_key == 'voltage':
                        self._set_amplitude(self._convert_axis(key), sub_value)
                    elif sub_key == 'freq':
                        self._set_frequency(self._convert_axis(key), sub_value)
                    else:
                        raise ValueError('No such key')
            else:
                raise ValueError('No such key')


    @property
    def _PROBES(self):
        return{
            'x_pos': 'the position the x direction (with respect to the camera) in um',
            'x_voltage': 'the voltage of the x direction (with respect to the camera)',
            'x_freq': 'the frequency of the x direction (with respect to the camera)',
            'x_cap': 'the capacitance of the piezo in the x direction (with respect to the camera)',
            'y_pos': 'the position the y direction (with respect to the camera) in um',
            'y_voltage': 'the voltage of the y direction (with respect to the camera)',
            'y_freq': 'the frequency of the y direction (with respect to the camera)',
            'y_cap': 'the capacitance of the piezo in the y direction (with respect to the camera)',
            'z_pos': 'the position the z direction (with respect to the camera) in um',
            'z_voltage': 'the voltage of the z direction (with respect to the camera)',
            'z_freq': 'the frequency of the z direction (with respect to the camera)',
            'z_cap': 'the capacitance of the piezo in the z direction (with respect to the camera)'
        }

    def read_probes(self, key):
        assert key in self._PROBES.keys()
        assert isinstance(key, str)

        if key in ['x_pos', 'y_pos', 'z_pos']:
            return self._get_position(self._convert_axis(key[0]))
        elif key in ['x_voltage', 'y_voltage', 'z_voltage']:
            return self._get_amplitude(self._convert_axis(key[0]))
        elif key in ['x_freq', 'y_freq', 'z_freq']:
            return self._get_frequency(self._convert_axis(key[0]))
        elif key in ['x_cap', 'y_cap', 'z_cap']:
            return self._cap_measure(self._convert_axis(key[0]))

    @property
    def is_connected(self):
        '''
        Check if attocube controller is connected
        Returns: True if controller is connected, false otherwise

        '''
        #connecting fails if device is not connected, so this catches that error
        try:
            device_handle = int32()
            self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
            self._check_error(self.attocube.PositionerClose(device_handle))
            return True
        except Exception:
            return False

    def _toggle_axis(self, axis, on):
        '''
        Turn axis on or off
        :param axis: axis_x, axis_y, or axis_z
        :param on: True or False
        '''
        device_handle = int32()
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        self._check_error(self.attocube.PositionerSetOutput(device_handle, axis, ctypes.c_bool(on)))
        self._check_error(self.attocube.PositionerClose(device_handle))

    def _set_frequency(self, axis, freq):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :param freq: frequency to set in Hz
        '''
        assert (freq <= 2000)
        device_handle = int32()
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        self._check_error(self.attocube.PositionerFrequency(device_handle, axis, int32(int(freq))))
        self._check_error(self.attocube.PositionerClose(device_handle))

    def _get_frequency(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: current frequency of axis in Hz
        '''
        device_handle = int32()
        freq = int32()
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        self._check_error(self.attocube.PositionerGetFrequency(device_handle, axis, ctypes.byref(freq)))
        self._check_error(self.attocube.PositionerClose(device_handle))
        return freq.value

    def _set_amplitude(self, axis, amplitude):
        '''
        :param axis: axis: axis_x, axis_y, or axis_z
        :param amplitude: amplitude in V
        '''
        assert(amplitude <= 60)
        device_handle = int32()
        amplitude *= 1000
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        self._check_error(self.attocube.PositionerAmplitude(device_handle, axis, int32(int(amplitude))))
        self._check_error(self.attocube.PositionerClose(device_handle))

    def _get_amplitude(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: amplitude in V
        '''
        device_handle = int32()
        amplitude = int32()
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        self._check_error(self.attocube.PositionerGetAmplitude(device_handle, axis, ctypes.byref(amplitude)))
        self._check_error(self.attocube.PositionerClose(device_handle))
        return (amplitude.value / 1000.0)

    def _get_position(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: position of axis in um
        '''
        device_handle = int32()
        position = int32()
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        # wait command needed since polling rate of attocube is 20 Hz. Empirically determined that .2 is lowest value
        # that always works. No idea why no other function also needs this wait command
        time.sleep(.2)
        self._check_error(self.attocube.PositionerGetPosition(device_handle, axis, ctypes.byref(position)))
        self._check_error(self.attocube.PositionerClose(device_handle))
        return position.value/1000.0

    def _cap_measure(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: Capacitance in uF
        '''
        device_handle = int32()
        capacitance = int32()
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        self._check_error(self.attocube.PositionerCapMeasure(device_handle, axis, ctypes.byref(capacitance)))
        self._check_error(self.attocube.PositionerClose(device_handle))
        return capacitance.value

    def _move_absolute(self, axis, position):
        '''
        Precondition: Must set voltage and frequency sufficiently low that ANC's internal feedback will be able to
        settle on the appropriate position (ex. 7V, 100Hz). Otherwise, fluctuates around target position and never stops
        :param axis: axis_x, axis_y, or axis_z
        :param position: position of axis to move to in um
        '''
        device_handle = int32()
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        self._check_error(self.attocube.PositionerMoveAbsolute(device_handle, axis, int32(int(position * 1000.0))))
        self._check_error(self.attocube.PositionerClose(device_handle))

    def step(self, axis, dir):
        '''
        Move a single step on the given axis in the given direction
        Args:
            axis: 'x', 'y', or 'z'
            dir: 0 for forwards, 1 for backwards

        '''
        device_handle = int32()
        axis = self._convert_axis(axis)
        self._check_error(self.attocube.PositionerConnect(0, ctypes.byref(device_handle)))
        self._check_error(self.attocube.PositionerMoveSingleStep(device_handle, axis, int32(dir)))
        self._check_error(self.attocube.PositionerClose(device_handle))

    def _convert_axis(self, axis):
        if axis == 'x':
            return axis_x
        elif axis == 'y':
            return axis_y
        elif axis == 'z':
            return axis_z
        else:
            raise ValueError('No such axis')

    @staticmethod
    def _check_error(code):
        '''
        Translates error codes to human readable message
        :param code: input error code (integer 0-8)
        :poststate: message printed to stdout
        '''
        if(code == NCB_Ok):
            return
        elif(code == NCB_BootIgnored):
            print( "Warning: boot ignored\n" )
            raise Exception
        elif(code == NCB_Error):
            print( "Error: unspecific\n" )
            raise Exception
        elif(code == NCB_Timeout):
            print( "Error: comm. timeout\n" )
            raise Exception
        elif(code == NCB_NotConnected):
            print( "Error: not connected\n" )
            raise Exception
        elif(code == NCB_DriverError):
            print( "Error: driver error\n" )
            raise Exception
        elif(code == NCB_FileNotFound):
            print( "Error: file not found\n" )
            raise Exception
        elif(code == NCB_InvalidParam):
            print( "Error: invalid parameter\n" )
            raise Exception
        elif(code == NCB_DeviceLocked):
            print( "Error: device locked\n" )
            raise Exception
        elif(code == NCB_NotSpecifiedParam):
            print( "Error: unspec. parameter\n" )
            raise Exception
        else:
            print( "Error: unknown\n" )
            raise Exception

if __name__ == '__main__':
    a = Attocube()
    a.update({'x': {'voltage': 20}})
    print(a.is_connected)