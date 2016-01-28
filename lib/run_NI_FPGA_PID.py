# test script for LavView FPGA
import time
import lib.FPGA_PID_Loop_Simple as NI


fpga = NI.NI7845R()

print(fpga.session, fpga.status)
fpga.start()

print(fpga.session, fpga.status)



PID = NI.NI_FPGA_PI(fpga)

x = PID.get_PI_status()
print(x)

PID.set_PI_status(False)
x = PID.get_PI_status()
print(x)



x = PID.get_detector()
print(x)


print('set detector')
PID.set_piezo(5000)
# time.sleep(0.1)
x = PID.get_detector()
print('actual detector value {:e}'.format(x))
print('set detector')
PID.set_piezo(2000)
# time.sleep(0.1)
x = PID.get_detector()
print('actual detector value {:e}'.format(x))



fpga.stop()

print(fpga.session, fpga.status)
