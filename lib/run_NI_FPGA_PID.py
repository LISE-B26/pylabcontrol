# test script for LavView FPGA
import time
import lib.FPGA_PID_Loop_Simple as NI


fpga = NI.NI7845R()

print(fpga.session, fpga.status)
fpga.start()

print(fpga.session, fpga.status)



PID = NI.NI_FPGA_PID(fpga)

x = PID.get_detector()
print(x)

PID.set_piezo(1000)
# time.sleep(0.1)
x = PID.get_detector()
print(x)

PID.set_piezo(-2000)
# time.sleep(0.1)
x = PID.get_detector()
print(x)

fpga.stop()

print(fpga.session, fpga.status)
