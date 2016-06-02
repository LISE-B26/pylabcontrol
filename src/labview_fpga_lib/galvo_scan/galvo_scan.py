from ctypes import *
# TODO: find a way to call lib from a folder which doesn't contrain the bitfile of the FPGA (now it has to be place in the same directory as the python file to work


_libfpga = WinDLL('C:/Users/Experiment/PycharmProjects/PythonLab/src/labview_fpga_lib/read_ai_ao/read_ai_ao.dll')

_libfpga.start_fpga.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.start_fpga.restype = None

_libfpga.stop_fpga.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.stop_fpga.restype = None

# read inputs
_libfpga.Detector_signal.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.Detector_signal.restype = c_int16

# set outputs
_libfpga.set_AO0.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO0.restype = None

_libfpga.settle_time_CountTicks.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.settle_time_CountTicks.restype = None


def start_fpga(session, status):
    return _libfpga.start_fpga(byref(session), byref(status))

def stop_fpga(session, status):
    return _libfpga.stop_fpga(byref(session), byref(status))


# read vaues
def get_detector_signal(session, status):
    return _libfpga.Detector_signal(byref(session), byref(status))

def get_detector_signal(session, status):
    return _libfpga.Detector_signal(byref(session), byref(status))

# set values
def set_scan_parameter(session, status,
                       vmin_x, dv_x, n_x,
                       vmin_y, dv_y, n_y,
                       settle_time = 1000,
                       loop_time = 10000,
                       scan_mode = 'forward',
                       forward_y = True,
                       ):

    _libfpga.settle_time_CountTicks(value, byref(session), byref(status))

class NI7845R(object):
    session = c_uint32()
    status = c_int32()

    def __init__(self):
        """
        object to establish communication with the NI FPGA
        note this has to be implemented for each bitfile (i.e. labview fpga program)
        because the extual implementation of start in the .c code calls a different bitfile
        """
        pass


    def start(self):
        start_fpga(self.session, self.status)
        # print(self.status.value)
        if self.status.value != 0:
            if int(self.status.value) ==  -63101:
                print("ERROR 63101: Bitfile not found")
            else:
                print('ERROR IN STARTING FPGA  (ERROR CODE: ', self.status.value, ')')
        return self.status

    def stop(self):
        stop_fpga(self.session, self.status)

    # @property
    # def device_temperature(self):
    #     read_DeviceTemperature(self.session, self.status)



if __name__ == '__main__':

    fpga = NI7845R()
    fpga.start()
    fpga.stop()