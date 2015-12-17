# B26 Lab Code
# Last Update 12/11/15

# External Connections: usb connection to ANC350 controller. Confirm connection using DAISY software

import ctypes

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

attocube = ctypes.WinDLL('C:/Users/Experiment/Downloads/attocube/attocube/Software/ANC350_Software_v1.5.15/ANC350_DLL/Win_64Bit/src/anc350v2.dll')

# c struct used as return type for some functions
class PositionerInfo(ctypes.Structure):
    _fields_ = [(("id"), ctypes.c_int32), (("locked"), ctypes.c_bool)]

class ANC350:

    def __init__(self):
        '''
        Initializes then closes a connection to the attocube to ensure that the connection is working properly
        '''
        self.pi = PositionerInfo()
        dev_count = attocube.PositionerCheck(ctypes.byref(self.pi))
        if not dev_count == 1:
            if dev_count == 0:
                print('No attocube controller connected. Connect a device.')
                raise Exception
            elif dev_count > 1:
                print('Multiple attocube controllers detected. This program will not continue.')
                raise Exception
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerClose(device_handle))

    def get_status(self, axis):
        '''
        Check axis status
        :param axis: axis_x, axis_y, or axis_z
        :return: four status bytes (0 if false, 1 if true) to check if the axis is moving, stopped, there is a sensor
            error, or the sensor is disconnected in that order
        '''
        status = int32()
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetStatus(device_handle, axis, ctypes.byref(status)))
        moving = status.value % 2
        stopped = status.value >> 1 % 2
        sensor_error = status.value >> 2 % 2
        sensor_disconnect = status.value >> 3 % 2
        self.check_error(attocube.PositionerClose(device_handle))
        return moving, stopped, sensor_error, sensor_disconnect

    def toggle_axis(self, axis, on):
        '''
        Turn axis on or off
        :param axis: axis_x, axis_y, or axis_z
        :param on: True or False
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerSetOutput(device_handle, axis, ctypes.c_bool(on)))
        self.check_error(attocube.PositionerClose(device_handle))

    def get_position(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: position of axis times 1000
        '''
        device_handle = int32()
        position = float64()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetPosition(device_handle, axis, ctypes.byref(position)))
        self.check_error(attocube.PositionerClose(device_handle))
        return position.value

    def cap_measure(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: Capacitance in uF
        '''
        device_handle = int32()
        capacitance = float64()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerCapMeasure(device_handle, axis, ctypes.byref(capacitance)))
        self.check_error(attocube.PositionerClose(device_handle))
        return capacitance.value

    def set_origin(self, axis):
        '''
        Reset axis origin to current position
        :param axis: axis_x, axis_y, or axis_z
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerResetPosition(device_handle, axis))
        self.check_error(attocube.PositionerClose(device_handle))

    # Check that float is correct format for input
    def move_absolute(self, axis, position):
        '''

        :param axis: axis_x, axis_y, or axis_z
        :param position: position of axis to move to times 1000
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveAbsolute(device_handle, axis, float64(position)))
        self.check_error(attocube.PositionerClose(device_handle))

    def move_relative(self, axis, distance):
        '''

        :param axis: axis: axis_x, axis_y, or axis_z
        :param distance: amount to move axis times 1000
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveRelative(device_handle, axis, float64(distance)))
        self.check_error(attocube.PositionerClose(device_handle))

    def stop_move_to_pos(self, axis):
        '''

        :param axis: axis: axis_x, axis_y, or axis_z
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerStopApproach(device_handle, axis))
        self.check_error(attocube.PositionerClose(device_handle))

    def set_amplitude(self, axis, amplitude):
        '''

        :param axis: axis: axis_x, axis_y, or axis_z
        :param amplitude: amplitude in mv
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerAmplitude(device_handle, axis, float64(amplitude)))
        self.check_error(attocube.PositionerClose(device_handle))

    def get_amplitude(self, axis):
        '''

        :param axis: axis_x, axis_y, or axis_z
        :return: amplitude in mv
        '''
        device_handle = int32()
        amplitude = float64()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetAmplitude(device_handle, axis, ctypes.byref(amplitude)))
        self.check_error(attocube.PositionerClose(device_handle))
        return amplitude.value

    def step_piezo(self, axis, direction):
        '''

        :param axis: axis_x, axis_y, or axis_z
        :param direction: 0 for forwards, 1 for backwards
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveSingleStep(device_handle, axis, int32(direction)))
        self.check_error(attocube.PositionerClose(device_handle))

    def cont_move_piezo(self, axis, direction):
        '''

        :param axis: axis_x, axis_y, or axis_z
        :param direction: 0 for forwards, 1 for backwards
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveContinuous(device_handle, axis, int32(direction)))
        self.check_error(attocube.PositionerClose(device_handle))

    def stop_piezo(self, axis):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerStopMoving(device_handle, axis))
        self.check_error(attocube.PositionerClose(device_handle))

    def set_frequency(self, axis, freq):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerFrequency(device_handle, axis, float64(freq)))
        self.check_error(attocube.PositionerClose(device_handle))

    def get_frequency(self, axis):
        device_handle = int32()
        freq = float64()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetFrequency(device_handle, axis, ctypes.byref(freq)))
        self.check_error(attocube.PositionerClose(device_handle))
        return freq.value

    @staticmethod
    def check_error(code):
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

#a = ANC350()
#print(a.get_position(axis_x))