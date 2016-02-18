# B26 Lab Code
# Last Update 12/11/15

# External Connections: usb connection to ANC350 controller. Confirm connection using DAISY software

import ctypes
import time
import sys

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

attocube = ctypes.WinDLL('C:/Users/Experiment/Downloads/attocube/Software/ANC350_Software_v1.5.15/ANC350_DLL/Win_64Bit/src/anc350v2.dll')
#attocube = ctypes.WinDLL('C:/Users/Experiment/Downloads/Software_ANC350v2/DLL/Win64/lib/hvpositionerv2.dll')

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
        #if not dev_count == 1:
        #    if dev_count == 0:
        #        print('No attocube controller connected. Connect a device.')
        #        raise Exception
        #    elif dev_count > 1:
        #        print('Multiple attocube controllers detected. This program will not continue.')
        #        raise Exception
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerClose(device_handle))

    def load(self, axis, filepath):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerSetOutput(device_handle, axis, filepath))
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
        :return: position of axis in um
        '''
        device_handle = int32()
        position = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        # wait command needed since polling rate of attocube is 20 Hz. Empirically determined that .2 is lowest value
        # that always works. No idea why no other function also needs this wait command
        time.sleep(.2)
        self.check_error(attocube.PositionerGetPosition(device_handle, axis, ctypes.byref(position)))
        self.check_error(attocube.PositionerClose(device_handle))
        return position.value/1000.0

    def get_ref(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: position of axis in um
        '''
        device_handle = int32()
        position = int32()
        valid = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetReference(device_handle, axis, ctypes.byref(position), ctypes.byref(valid)))
        self.check_error(attocube.PositionerClose(device_handle))
        return position.value/1000.0

    def cap_measure(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: Capacitance in uF
        '''
        device_handle = int32()
        capacitance = int32()
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

    def move_absolute(self, axis, position):
        '''
        Precondition: Must set voltage and frequency sufficiently low that ANC's internal feedback will be able to
        settle on the appropriate position (ex. 7V, 100Hz). Otherwise, fluctuates around target position and never stops
        :param axis: axis_x, axis_y, or axis_z
        :param position: position of axis to move to in um
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveAbsolute(device_handle, axis, int32(int(position*1000.0))))
        self.check_error(attocube.PositionerClose(device_handle))

    def move_relative(self, axis, distance):
        '''
        Precondition: Must set voltage and frequency sufficiently low that ANC's internal feedback will be able to
        settle on the appropriate position (ex. 7V, 100Hz). Otherwise, fluctuates around target position and never stops        :param axis: axis_x, axis_y, or axis_z
        :param distance: amount to move axis in um
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveRelative(device_handle, axis, int32(int(distance*1000.0))))
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
        :param amplitude: amplitude in V
        '''
        assert(amplitude <= 60)
        device_handle = int32()
        amplitude *= 1000
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerAmplitude(device_handle, axis, int32(int(amplitude))))
        self.check_error(attocube.PositionerClose(device_handle))

    def get_amplitude(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: amplitude in V
        '''
        device_handle = int32()
        amplitude = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetAmplitude(device_handle, axis, ctypes.byref(amplitude)))
        self.check_error(attocube.PositionerClose(device_handle))
        return (amplitude.value / 1000.0)

    def get_speed(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: speed in V/s
        '''
        device_handle = int32()
        speed = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetSpeed(device_handle, axis, ctypes.byref(speed)))
        self.check_error(attocube.PositionerClose(device_handle))
        return (speed.value / 1000.0)

    def step_piezo(self, axis, direction):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :param direction: 0 for forwards, 1 for backwards
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveSingleStep(device_handle, axis, int32(direction)))
        self.check_error(attocube.PositionerClose(device_handle))

    def step_cnt(self, axis, num_steps):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :param direction: 0 for forwards, 1 for backwards
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerStepCount(device_handle, axis, int32(num_steps)))
        self.check_error(attocube.PositionerMoveSingleStep(device_handle, axis, int32(1)))
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
        '''
        :param axis: axis_x, axis_y, or axis_z
        '''
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerStopMoving(device_handle, axis))
        self.check_error(attocube.PositionerClose(device_handle))

    def set_frequency(self, axis, freq):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :param freq: frequency to set in Hz
        '''
        assert (freq <= 2000)
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerFrequency(device_handle, axis, int32(int(freq))))
        self.check_error(attocube.PositionerClose(device_handle))

    def get_frequency(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: current frequency of axis in Hz
        '''
        device_handle = int32()
        freq = int32()
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

a = ANC350()
#a.load(axis_z, ctypes.c_char_p('C:/Users/Experiment/Downloads/Software_ANC350v2/ANC350_GUI/general_APS_files/ANPz101res.aps'))
#print(a.cap_measure(axis_z))
#print(a.get_frequency(axis_z))
#a.cont_move_piezo(axis_z,1)
#time.sleep(1)
#a.stop_piezo(axis_z)
#a.move_relative(axis_y,5000)