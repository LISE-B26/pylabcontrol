from ctypes import *
import numpy as np
# TODO: find a way to call lib from a folder which doesn't contrain the bitfile of the FPGA (now it has to be place in the same directory as the python file to work

# =========================================================================
# ======= LOAD DLL ========================================================
# =========================================================================
_libfpga = WinDLL('C:/Users/Experiment/PycharmProjects/PythonLab/src/labview_fpga_lib/galvo_scan/galvo_scan.dll')

# =========================================================================
# ======= DEFINE SETTER FUNCTIONS =========================================
# =========================================================================
# name of dictionary entry is the name of the function
# value of the dictionary entry is the data type that is passed to the function
setter_functions = {
    "set_Nx": c_int16,
    "set_Vmin_x": c_int16,
    "set_dVmin_x": c_int16,
    "set_Ny": c_int16,
    "set_Vmin_y": c_int16,
    "set_dVmin_y": c_int16,
    "set_scanmode_x": c_uint8,
    "set_scanmode_y": c_uint8,
    "set_detector_mode": c_uint8,
    "set_settle_time": c_uint16,
    "set_meas_per_pt": c_uint16,
    'set_acquire': c_bool,
    'set_abort': c_bool,
    'set_piezo_voltage':c_uint16
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
    "reset_fpga": None,
    "read_loop_time": c_uint32,
    "read_DMA_elem_to_write": c_uint32,
    "read_DMATimeOut": c_bool,
    "read_elements_written_to_dma": c_int32,
    "read_detector_signal": c_int32,
    "read_ix": c_int32,
    "read_iy": c_int32,
    "read_Nx": c_int32,
    "read_Ny": c_int32,
    'read_acquire':c_bool,
    'read_abort':c_bool,
    'read_running':c_bool,
    'read_output_valid':c_bool,
    'read_meas_per_pt':c_uint16,
    'read_settle_time':c_uint16,
    'read_failed': c_int32
}

for fun_name in getter_functions:
    setattr( _libfpga, "{:s}.argtypes".format(fun_name), [POINTER(c_uint32), POINTER(c_int32)])
    setattr( _libfpga, "{:s}.restype".format(fun_name), getter_functions[fun_name])
    exec("""def {:s}(session, status):
        return _libfpga.{:s}(byref(session), byref(status))""".format(fun_name, fun_name))



# =========================================================================
# ======= DEFINE FIFO FUNCTIONS =========================================
# =========================================================================
_libfpga.configure_FIFO.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_int32)]
_libfpga.configure_FIFO.restype = c_uint32
def configure_FIFO(requestedDepth, session, status):
    return _libfpga.configure_FIFO(requestedDepth, byref(session), byref(status))

# start FIFO
_libfpga.start_FIFO.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.start_FIFO.restype = None
def start_FIFO(session, status):
    return _libfpga.start_FIFO(byref(session), byref(status))

# stop FIFO
_libfpga.stop_FIFO.argtypes = [POINTER(c_uint32), POINTER(c_int32)]
_libfpga.stop_FIFO.restype = None
def stop_FIFO(session, status):
    return _libfpga.stop_FIFO(byref(session), byref(status))


# read FIFO
_libfpga.read_FIFO.argtypes = [POINTER(c_int32), c_uint32,
                               POINTER(c_uint32), POINTER(c_int32),
                               POINTER(c_uint32)]

_libfpga.read_FIFO.restype = None

def read_FIFO(size, session, status):
    Signal = (c_int32*size)()
    elements_remaining = c_uint32()

    _libfpga.read_FIFO(Signal, size, byref(session), byref(status), byref(elements_remaining))


    return {'signal': np.array(Signal), 'elements_remaining': elements_remaining.value}

#
#
# # set values
# def set_scan_parameter(session, status,
#                        vmin_x, dv_x, n_x,
#                        vmin_y, dv_y, n_y,
#                        settle_time = 1000,
#                        loop_time = 10000,
#                        scan_mode = 'forward',
#                        forward_y = True,
#                        ):
#
#     _libfpga.settle_time_CountTicks(value, byref(session), byref(status))

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
        print('fpga started, status = ', self.status.value)
        # reset_fpga(self.session, self.status)
        # print('fpga reset, status = ', self.status.value)
        #
        # start_fpga(self.session, self.status)
        print('fpga started, status = ', self.status.value)
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