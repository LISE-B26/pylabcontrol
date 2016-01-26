from ctypes import *
# TODO: find a way to call lib from a folder which doesn't contrain the bitfile of the FPGA (now it has to be place in the same directory as the python file to work


_libfpga = WinDLL('C:/Users/Experiment/PycharmProjects/PythonLab/lib/FPGA_PID_lib.dll')

_libfpga.start_fpga.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.start_fpga.restype = None

_libfpga.stop_fpga.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.stop_fpga.restype = None

# read inputs
_libfpga.read_AI1.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI1.restype = c_int16

_libfpga.read_AI1_Filtered.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI1_Filtered.restype = c_int16

_libfpga.read_AI2.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI2.restype = c_int16

_libfpga.read_DeviceTemperature.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_DeviceTemperature.restype = c_int16

_libfpga.read_PiezoOut.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_PiezoOut.restype = c_int16

# set outputs
_libfpga.set_PiezoOut.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_PiezoOut.restype = None

def start_fpga(session, status):
    return _libfpga.start_fpga(byref(session), byref(status))

def stop_fpga(session, status):
    return _libfpga.stop_fpga(byref(session), byref(status))


# read Analog inputs
def read_AI1(session, status):
    return _libfpga.read_AI1(byref(session), byref(status))

def read_AI1_Filtered(session, status):
    return _libfpga.read_AI1_Filtered(byref(session), byref(status))

def read_AI2(session, status):
    return _libfpga.read_AI2(byref(session), byref(status))

def read_DeviceTemperature(session, status):
    return _libfpga.read_DeviceTemperature(byref(session), byref(status))

def read_PiezoOut(session, status):
    return _libfpga.read_PiezoOut(byref(session), byref(status))


def set_PiezoOut(value, session, status):
    return _libfpga.set_PiezoOut(value, byref(session), byref(status))