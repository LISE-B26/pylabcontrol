import ctypes

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double

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

class PositionerInfo(ctypes.Structure):
    _fields_ = [(("id"), ctypes.c_int32), (("locked"), ctypes.c_bool)]

class ANC350:

    def __init__(self):
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
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerSetOutput(device_handle, axis, ctypes.c_bool(on)))
        self.check_error(attocube.PositionerClose(device_handle))

    def get_position(self, axis):
        device_handle = int32()
        position = float64()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetPosition(device_handle, axis, ctypes.byref(position)))
        self.check_error(attocube.PositionerClose(device_handle))
        return position.value

    def cap_measure(self, axis):
        device_handle = int32()
        capacitance = float64()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerCapMeasure(device_handle, axis, ctypes.byref(capacitance)))
        self.check_error(attocube.PositionerClose(device_handle))
        return capacitance.value

    def set_origin(self, axis):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerResetPosition(device_handle, axis))
        self.check_error(attocube.PositionerClose(device_handle))

    # Check that float is correct format for input
    def move_absolute(self, axis, position):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveAbsolute(device_handle, axis, float64(position)))
        self.check_error(attocube.PositionerClose(device_handle))

    def move_relative(self, axis, distance):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveRelative(device_handle, axis, float64(distance)))
        self.check_error(attocube.PositionerClose(device_handle))

    def stop_move_to_pos(self, axis):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerStopApproach(device_handle, axis))
        self.check_error(attocube.PositionerClose(device_handle))

    def set_amplitude(self, axis, amplitude):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerAmplitude(device_handle, axis, float64(amplitude)))
        self.check_error(attocube.PositionerClose(device_handle))

    def get_amplitude(self, axis):
        device_handle = int32()
        amplitude = float64()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerGetAmplitude(device_handle, axis, ctypes.byref(amplitude)))
        self.check_error(attocube.PositionerClose(device_handle))
        return amplitude.value

    # direction: 0 = forwards, 1 = backwards
    def step_piezo(self, axis, direction):
        device_handle = int32()
        self.check_error(attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(attocube.PositionerMoveSingleStep(device_handle, axis, int32(direction)))
        self.check_error(attocube.PositionerClose(device_handle))

    def cont_move_piezo(self, axis, direction):
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
print(a.get_position(axis_x))