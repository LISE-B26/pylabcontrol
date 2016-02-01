"""
Created on Wed Oct 22 17:46:08 2014

@author: Jan Gieseler


Wrapper for c-compiled FPGA_PID_Loop_Simple.vi (complied into FPGA_PID_lib.dll)
here we wrap the c-functions that can are then accessed by the higher level
FPGA_PID_Loop_Simple.py which defines the higher level Python objects that are then used to interact with the NI FPGA

"""

# TODO: find a way to call lib from a folder which doesn't contrain the bitfile of the FPGA (now it has to be place in the same directory as the python file to work


from ctypes import *

# =========================================================================
# ======= LOAD DLL ========================================================
# =========================================================================
_libfpga = WinDLL('C:/Users/Experiment/PycharmProjects/PythonLab/lib/FPGA_PID_lib.dll')

# =========================================================================
# ======= DEFINE SETTER FUNCTIONS =========================================
# =========================================================================
# name of dictionary entry is the name of the function
# value of the dictionary entry is the data type that is passed to the function

setter_functions = {
    "set_PiezoOut": c_int16,
    "set_Setpoint": c_int16,
    "set_ScaledCoefficient_1": c_int32,
    "set_ScaledCoefficient_2": c_int32,
    "set_ScaledCoefficient_3": c_int32,
    "set_ElementsToWrite": c_int32,
    "set_SamplePeriodsPID": c_uint32,
    "set_SamplePeriodsAcq": c_uint32,
    "set_PI_gain_prop": c_uint32,
    "set_PI_gain_int": c_uint32,
    "set_LowPassActive": c_bool,
    "set_PIDActive": c_bool,
    "set_AcquireData": c_bool,
    "set_Stop": c_bool
}

for fun_name in setter_functions:
    setattr( _libfpga, "{:s}.argtypes".format(fun_name), [setter_functions[fun_name], POINTER(c_uint32), POINTER(c_int32)])
    setattr( _libfpga, "{:s}.restype".format(fun_name), None)
    exec("""def {:s}(value, session, status):
        return _libfpga.{:s}(value, byref(session), byref(status))""".format(fun_name, fun_name))

# =========================================================================
# ======= DEFINE GETTER FUNCTIONS =========================================
# =========================================================================
# name of dictionary entry is the name of the function
# value of the dictionary entry is the data type that is returned from the function
getter_functions = {
    "start_fpga": None,
    "stop_fpga": None,
    "read_AI1": c_int16,
    "read_AI1_Filtered": c_int16,
    "read_AI2": c_int16,
    "read_DeviceTemperature": c_int16,
    "read_PiezoOut": c_int16,
    "read_ElementsWritten": c_int32,
    "read_SamplePeriodsPID": c_uint32,
    "read_SamplePeriodsAcq": c_uint32,
    "read_LoopTicksPID": c_uint32,
    "read_LoopTicksAcq": c_uint32,
    "read_LoopRateLimitPID": c_bool,
    "read_LoopRateLimitAcq": c_bool,
    "read_TimeOutAcq": c_bool,
    "read_LowPassActive": c_bool,
    "read_PIDActive": c_bool,
    "read_FPGARunning": c_bool,
    "read_DMATimeOut": c_bool,
    "read_AcquireData": c_bool
}

for fun_name in getter_functions:
    setattr( _libfpga, "{:s}.argtypes".format(fun_name), [POINTER(c_uint32), POINTER(c_int32)])
    setattr( _libfpga, "{:s}.restype".format(fun_name), getter_functions[fun_name])
    exec("""def {:s}(session, status):
        return _libfpga.{:s}(byref(session), byref(status))""".format(fun_name, fun_name))

