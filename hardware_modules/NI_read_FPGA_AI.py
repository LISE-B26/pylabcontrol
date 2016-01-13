#
# from ctypes import *
# from numpy import array, cumsum
#
# _libfpga = CDLL('libfpga_bundle')
#
#
#
# _libfpga.read_AI0.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
# _libfpga.read_AI0.restype = c_int16
#
# def read_AI0(session, status):
#     return _libfpga.read_AI0(byref(session), byref(status))


import ctypes

_dll = ctypes.WinDLL("Z:\\Lab\\Cantilever\\tmp_jan\\mydll.dll")

_dll.add2.argtypes = [POINTER(c_uint16)]
_dll.add2.restype = c_int16

def tmp(x):
    return _dll.add2(byref(x))



