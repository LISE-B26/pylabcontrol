from ctypes import *
# TODO: find a way to call lib from a folder which doesn't contrain the bitfile of the FPGA (now it has to be place in the same directory as the python file to work


_libfpga = WinDLL('C:/Users/Experiment/PycharmProjects/PythonLab/lib/FPGAlib.dll')

_libfpga.start_fpga.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.start_fpga.restype = None

_libfpga.stop_fpga.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.stop_fpga.restype = None

# read inputs
_libfpga.read_AI0.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI0.restype = c_uint16

_libfpga.read_AI1.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI1.restype = c_uint16

_libfpga.read_AI2.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI2.restype = c_uint16

_libfpga.read_AI3.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI3.restype = c_uint16

_libfpga.read_AI4.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI4.restype = c_uint16

_libfpga.read_AI5.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI5.restype = c_uint16

_libfpga.read_AI6.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI6.restype = c_uint16

_libfpga.read_AI7.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_AI7.restype = c_uint16


# set outputs
_libfpga.set_AO0.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO0.restype = None

_libfpga.set_AO1.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO1.restype = None

_libfpga.set_AO2.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO2.restype = None

_libfpga.set_AO3.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO3.restype = None

_libfpga.set_AO4.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO4.restype = None

_libfpga.set_AO5.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO5.restype = None

_libfpga.set_AO6.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO6.restype = None

_libfpga.set_AO7.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AO7.restype = None



def start_fpga(session, status):
    return _libfpga.start_fpga(byref(session), byref(status))

def stop_fpga(session, status):
    return _libfpga.stop_fpga(byref(session), byref(status))


# read Analog inputs
def read_AI0(session, status):
    return _libfpga.read_AI0(byref(session), byref(status))

def read_AI1(session, status):
    return _libfpga.read_AI1(byref(session), byref(status))

def read_AI2(session, status):
    return _libfpga.read_AI2(byref(session), byref(status))

def read_AI3(session, status):
    return _libfpga.read_AI3(byref(session), byref(status))

def read_AI4(session, status):
    return _libfpga.read_AI4(byref(session), byref(status))

def read_AI5(session, status):
    return _libfpga.read_AI5(byref(session), byref(status))

def read_AI6(session, status):
    return _libfpga.read_AI6(byref(session), byref(status))

def read_AI7(session, status):
    return _libfpga.read_AI7(byref(session), byref(status))


def set_AO0(value, session, status):
    return _libfpga.set_AO0(value, byref(session), byref(status))

def set_AO1(value, session, status):
    return _libfpga.set_AO1(value, byref(session), byref(status))

def set_AO2(value, session, status):
    return _libfpga.set_AO2(value, byref(session), byref(status))

def set_AO3(value, session, status):
    return _libfpga.set_AO3(value, byref(session), byref(status))

def set_AO4(value, session, status):
    return _libfpga.set_AO4(value, byref(session), byref(status))

def set_AO5(value, session, status):
    return _libfpga.set_AO5(value, byref(session), byref(status))

def set_AO6(value, session, status):
    return _libfpga.set_AO6(value, byref(session), byref(status))

def set_AO7(value, session, status):
    return _libfpga.set_AO7(value, byref(session), byref(status))