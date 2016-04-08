"""
Created on Wed Oct 22 17:46:08 2014

@author: Jan Gieseler


Wrapper for c-compiled FPGA_PID_Loop_Simple.vi (complied into FPGA_PID_lib.dll)
here we wrap the c-functions that can are then accessed by the higher level
FPGA_PID_Loop_Simple.py which defines the higher level Python objects that are then used to interact with the NI FPGA

"""

# TODO: reading of analog input gives only positive values (as if cast into unsigned integer, try to figure out why that is

from ctypes import *

# =========================================================================
# ======= LOAD DLL ========================================================
# =========================================================================
_libfpga = WinDLL('C:/Users/Experiment/PycharmProjects/PythonLab/src/labview_fpga_lib/pid_loop_simple/pid_loop_simple.dll')
# =========================================================================
# ======= DEFINE SETTER FUNCTIONS =========================================
# =========================================================================
# name of dictionary entry is the name of the function
# value of the dictionary entry is the data type that is passed to the function

setter_functions = {
    "set_PiezoOut": c_int16,
    "set_Setpoint": c_int16,
    "set_AmplitudeScaleCoefficient": c_int16,
    "set_ScaledCoefficient_1": c_int32,
    "set_ScaledCoefficient_2": c_int32,
    "set_ScaledCoefficient_3": c_int32,
    "set_ElementsToWrite": c_int32,
    "set_TimeoutBuffer": c_int32,
    "set_SamplePeriodsPID": c_uint32,
    "set_SamplePeriodsAcq": c_uint32,
    "set_PI_gain_prop": c_uint32,
    "set_PI_gain_int": c_uint32,
    "set_LowPassActive": c_bool,
    "set_PIDActive": c_bool,
    "set_AcquireData": c_bool,
    "set_Stop": c_bool,
    "set_OutputSine" : c_bool
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
    "read_Min": c_int16,
    "read_Max": c_int16,
    "read_Mean": c_int16,
    "read_StdDev": c_uint16,
    "read_ElementsWritten": c_int32,
    "read_SamplePeriodsPID": c_uint32,
    "read_SamplePeriodsAcq": c_uint32,
    "read_LoopTicksPID": c_uint32,
    "read_LoopTicksAcq": c_uint32,
    "read_AcqTime": c_uint32,
    "read_LoopRateLimitPID": c_bool,
    "read_LoopRateLimitAcq": c_bool,
    "read_TimeOutAcq": c_bool,
    "read_LowPassActive": c_bool,
    "read_PIDActive": c_bool,
    "read_FPGARunning": c_bool,
    "read_DMATimeOut": c_bool,
    "read_AcquireData": c_bool,
    "read_OutputSine": c_bool
}

for fun_name in getter_functions:
    setattr( _libfpga, "{:s}.argtypes".format(fun_name), [POINTER(c_uint32), POINTER(c_int32)])
    setattr( _libfpga, "{:s}.restype".format(fun_name), getter_functions[fun_name])
    exec("""def {:s}(session, status):
        return _libfpga.{:s}(byref(session), byref(status))""".format(fun_name, fun_name))


# =========================================================================
# ======= DEFINE FIFO FUNCTIONS =========================================
# =========================================================================
_libfpga.configure_FIFO_AI.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.configure_FIFO_AI.restype = c_uint32
def configure_FIFO_AI(requestedDepth, session, status):
    return _libfpga.configure_FIFO_AI(requestedDepth, byref(session), byref(status))


# _libfpga.set_FifoTimeout.argtypes = [c_int32, POINTER(c_uint32),
#                                      POINTER(c_int32)]
# _libfpga.set_FifoTimeout.restype = None


# start FIFO
_libfpga.start_FIFO_AI.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.start_FIFO_AI.restype = None
def start_FIFO_AI(session, status):
    return _libfpga.start_FIFO_AI(byref(session), byref(status))

# stop FIFO
_libfpga.stop_FIFO_AI.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.stop_FIFO_AI.restype = None
def stop_FIFO_AI(session, status):
    return _libfpga.stop_FIFO_AI(byref(session), byref(status))


# read FIFO
_libfpga.read_FIFO_AI.argtypes = [POINTER(c_uint32), c_int32,
                                  POINTER(c_uint32), POINTER(c_int32),
                                  POINTER(c_int32)]
_libfpga.read_FIFO_AI.restype = None
def read_FIFO_AI(size, session, status):
    AI1 = (c_int16*size)()
    AI2 = (c_int16*size)()
    elements_remaining = c_int32()

    _libfpga.read_FIFO_AI_unpack(AI1, AI2, size, byref(session), byref(status), byref(elements_remaining))
    return [AI1, AI2, elements_remaining.value]



# _libfpga.read_FIFO_AI_unpack.argtypes = [POINTER(c_int16), POINTER(c_int16),
#                                          c_int32, POINTER(c_uint32),
#                                          POINTER(c_int32), POINTER(c_int32)]
# _libfpga.read_FIFO_AI_unpack.restype = None

#
def read_FIFO_conv(size, session, status, ticks=56):
    """Reads a block of elements from the FPGA FIFO and determines the time
    array corresponding to them.
    """
    set_LoopTicks(ticks, session, status)

    [ai1, ai2, elements_remaining] = read_FIFO_AI(size, session, status)

    if elements_remaining == size:
        print("Warning: FIFO full and elements might get lost.")

    # ai0 = int_to_voltage(array(list(ai0)))
    # ai1 = int_to_voltage(array(list(ai1)))
    # ai2 = int_to_voltage(array(list(ai2)))

    # times = cumsum(array(list(ticks))) * 25e-9

    return ai0, ai1, ai2, times





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