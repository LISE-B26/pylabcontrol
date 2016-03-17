import ctypes
import time
import sys

import src.core.instruments as inst

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

# c struct used as return type for some functions
class PositionerInfo(ctypes.Structure):
    _fields_ = [(("id"), ctypes.c_int32), (("locked"), ctypes.c_bool)]

class Attocube(inst.Instrument):
    def __init__(self, name = None, parameters = []):
        super(Attocube, self).__init__(name, parameters)
        self._is_connected = False
        self.probes = ['capacitance']
        try:
            self.attocube = ctypes.WinDLL('C:/Users/Experiment/Downloads/attocube/Software/ANC350_Software_v1.5.15/ANC350_DLL/Win_64Bit/src/anc350v2.dll')
            dll_detected = True
        except WindowsError:
            # make a fake Attocube instrument
            dll_detected = False
        if dll_detected == True:
            try:
                self.pi = PositionerInfo()
                dev_count = self.attocube.PositionerCheck(ctypes.byref(self.pi))
                device_handle = int32()
                self.check_error(self.attocube.PositionerConnect(0,ctypes.byref(device_handle)))
                self.check_error(self.attocube.PositionerClose(device_handle))
            except Exception:
                print('Attocube not detected. Check connection.')

    @property
    def parameters_default(self):
        '''
        returns the default parameter_list of the instrument
        :return:
        '''
        parameter_list_default = [
            inst.Parameter('x',
                [
                    inst.Parameter('on', False, [True, False], 'x axis on'),
                    inst.Parameter('pos', 0, (int, float), 'x axis position in um'),
                    inst.Parameter('voltage', 30, (int, float), 'voltage on x axis'),
                    inst.Parameter('freq', 1000, (int, float), 'x frequency in Hz')
                ]
                ),
            inst.Parameter('y',
                [
                    inst.Parameter('on', False, [True, False], 'y axis on'),
                    inst.Parameter('pos', 0, (int, float), 'y axis position in um'),
                    inst.Parameter('voltage', 30, (int, float), 'voltage on y axis'),
                    inst.Parameter('freq', 1000, (int, float), 'y frequency in Hz')
                ]
                ),
            inst.Parameter('z',
                [
                    inst.Parameter('on', False, [True, False], 'z axis on'),
                    inst.Parameter('pos', 0, (int, float), 'x axis position in um'),
                    inst.Parameter('voltage', 30, (int, float), 'voltage on x axis'),
                    inst.Parameter('freq', 1000, (int, float), 'x frequency in Hz')
                ]
                ),
        ]
        return parameter_list_default

    def toggle_axis(self, axis, on):
        '''
        Turn axis on or off
        :param axis: axis_x, axis_y, or axis_z
        :param on: True or False
        '''
        device_handle = int32()
        self.check_error(self.attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(self.attocube.PositionerSetOutput(device_handle, axis, ctypes.c_bool(on)))
        self.check_error(self.attocube.PositionerClose(device_handle))

    def set_frequency(self, axis, freq):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :param freq: frequency to set in Hz
        '''
        assert (freq <= 2000)
        device_handle = int32()
        self.check_error(self.attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(self.attocube.PositionerFrequency(device_handle, axis, int32(int(freq))))
        self.check_error(self.attocube.PositionerClose(device_handle))

    def get_frequency(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: current frequency of axis in Hz
        '''
        device_handle = int32()
        freq = int32()
        self.check_error(self.attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(self.attocube.PositionerGetFrequency(device_handle, axis, ctypes.byref(freq)))
        self.check_error(self.attocube.PositionerClose(device_handle))
        return freq.value

    def get_position(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: position of axis in um
        '''
        device_handle = int32()
        position = int32()
        self.check_error(self.attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        # wait command needed since polling rate of attocube is 20 Hz. Empirically determined that .2 is lowest value
        # that always works. No idea why no other function also needs this wait command
        time.sleep(.2)
        self.check_error(self.attocube.PositionerGetPosition(device_handle, axis, ctypes.byref(position)))
        self.check_error(self.attocube.PositionerClose(device_handle))
        return position.value/1000.0

    def cap_measure(self, axis):
        '''
        :param axis: axis_x, axis_y, or axis_z
        :return: Capacitance in uF
        '''
        device_handle = int32()
        capacitance = int32()
        self.check_error(self.attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(self.attocube.PositionerCapMeasure(device_handle, axis, ctypes.byref(capacitance)))
        self.check_error(self.attocube.PositionerClose(device_handle))
        return capacitance.value

    def move_absolute(self, axis, position):
        '''
        Precondition: Must set voltage and frequency sufficiently low that ANC's internal feedback will be able to
        settle on the appropriate position (ex. 7V, 100Hz). Otherwise, fluctuates around target position and never stops
        :param axis: axis_x, axis_y, or axis_z
        :param position: position of axis to move to in um
        '''
        device_handle = int32()
        self.check_error(self.attocube.PositionerConnect(0,ctypes.byref(device_handle)))
        self.check_error(self.attocube.PositionerMoveAbsolute(device_handle, axis, int32(int(position*1000.0))))
        self.check_error(self.attocube.PositionerClose(device_handle))



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

if __name__ == '__main__':
    a = Attocube()