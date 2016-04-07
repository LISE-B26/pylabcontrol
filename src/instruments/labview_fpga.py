from src.core import Instrument, Parameter
from ctypes import c_uint32, c_int32



class NI7845R(Instrument):
    import src.labview_fpga_lib.reads_ai_ao.reads_ai_ao as FPGAlib
    session = c_uint32()
    status = c_int32()

    _DEFAULT_SETTINGS = Parameter()

    def __init__(self, name = None):
        super(NI7845R, self).__init__(name)

    def start(self):
        self.FPGAlib.start_fpga(self.session, self.status)
        return self.status

    def stop(self):
        self.FPGAlib.stop_fpga(self.session, self.status)

