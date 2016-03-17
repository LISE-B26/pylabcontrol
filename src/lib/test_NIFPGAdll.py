# from ctypes import c_uint32, c_int32
# import time
# import lib.FPGAlib as FPGAlib
#
# session = c_uint32()
# status = c_int32()
# print('open')
# print(session, status)
# FPGAlib.start_fpga(session, status)
# time.sleep(1)
# for i in range(10):
#     x = FPGAlib.read_AI0(session, status)
#     print(x)
# print('close')
# FPGAlib.stop_fpga(session, status)
#
# print(session, status)
# #

from src import lib as NI

if __name__ == '__main__':
    fpga = NI.NI7845R()
    fpga.start()

    AI = NI.AnalogInput(0, fpga)
    for i in range(10):
        x = AI.read()
        print(x)
    fpga.stop()

