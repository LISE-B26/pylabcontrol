"""
Created on Wed Oct 22 17:46:08 2014

@author: Jan Gieseler


Wrapper for c-compiled FPGA_PID_Loop_Simple.vi (complied into FPGA_PID_lib.dll)
here we wrap the c-functions that can are then accessed by the higher level
FPGA_PID_Loop_Simple.py which defines the higher level Python objects that are then used to interact with the NI FPGA

"""

# TODO: find a way to call lib from a folder which doesn't contrain the bitfile of the FPGA (now it has to be place in the same directory as the python file to work


from ctypes import *

_libfpga = WinDLL('C:/Users/Experiment/PycharmProjects/PythonLab/lib/FPGA_PID_lib.dll')

# =========================================================================
# ======= DEFINE TYPES ====================================================
# =========================================================================
_libfpga.start_fpga.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.start_fpga.restype = None
_libfpga.stop_fpga.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.stop_fpga.restype = None


# read logical indicators
_libfpga.read_LoopRateLimitPID.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_LoopRateLimitPID.restype = c_bool
_libfpga.read_LoopRateLimitAcq.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_LoopRateLimitAcq.restype = c_bool
_libfpga.read_TimeOutAcq.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_TimeOutAcq.restype = c_bool
_libfpga.read_PIDActive.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_PIDActive.restype = c_bool
_libfpga.read_FPGARunning.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_FPGARunning.restype = c_bool
_libfpga.read_DMATimeOut.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.read_DMATimeOut.restype = c_bool

# set logical values
_libfpga.set_PIDActive.argtypes = [c_bool, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_PIDActive.restype = None
_libfpga.set_AcquireData.argtypes = [c_bool, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_AcquireData.restype = None
_libfpga.set_Stop.argtypes = [c_bool, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.set_Stop.restype = None

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

# set Analog outputs
# _libfpga.set_PiezoOut.argtypes = [c_int16, POINTER(c_uint32), POINTER(c_int32)]
# _libfpga.set_PiezoOut.restype = None

fun_name = "set_PiezoOut"


# =========================================================================
# ======= DEFINE FUNCTIONS ================================================
# =========================================================================
setattr( _libfpga, "{:s}.argtypes".format(fun_name), [c_int16, POINTER(c_uint32), POINTER(c_int32)])
setattr( _libfpga, "{:s}.restype".format(fun_name), None)
exec("""def {:s}(value, session, status):
    return _libfpga.{:s}(value, byref(session), byref(status))""".format(fun_name, fun_name))
#
# def set_PiezoOut(value, session, status):
#     return _libfpga.set_PiezoOut(value, byref(session), byref(status))

# =========================================================================
# ======= DEFINE FUNCTIONS ================================================
# =========================================================================

def start_fpga(session, status):
    return _libfpga.start_fpga(byref(session), byref(status))
def stop_fpga(session, status):
    return _libfpga.stop_fpga(byref(session), byref(status))

# read times
def read_LoopRateLimitPID(session, status):
    return _libfpga.read_LoopRateLimitPID(byref(session), byref(status))

# read logical indicators
def read_LoopRateLimitPID(session, status):
    return _libfpga.read_LoopRateLimitPID(byref(session), byref(status))
def read_LoopRateLimitAcq(session, status):
    return _libfpga.read_LoopRateLimitAcq(byref(session), byref(status))
def read_TimeOutAcq(session, status):
    return _libfpga.read_TimeOutAcq(byref(session), byref(status))
def read_PIDActive(session, status):
    return _libfpga.read_PIDActive(byref(session), byref(status))
def read_FPGARunning(session, status):
    return _libfpga.read_FPGARunning(byref(session), byref(status))
def read_DMATimeOut(session, status):
    return _libfpga.read_DMATimeOut(byref(session), byref(status))

# set logical indicators
def set_PIDActive(value, session, status):
    return _libfpga.set_PIDActive(value, byref(session), byref(status))

def set_AcquireData(value, session, status):
    return _libfpga.set_AcquireData(value, byref(session), byref(status))

def set_Stop(value, session, status):
    return _libfpga.set_Stop(value, byref(session), byref(status))

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

