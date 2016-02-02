# test script for LavView FPGA
import time
import NI_read_FPGA_AI as NI

fpga = NI.NI7845R()

print(fpga.session, fpga.status)
fpga.start()

print(fpga.session, fpga.status)



AI = NI.AnalogInput(1,fpga)
AO = NI.AnalogOutput(0,fpga)

for i in range(-2000,10000,1000):
    y =AO.write(i)
    # print(y)
    time.sleep(0.1)
    x = AI.read()
    print(i, x, 100.* (x-i) / (x+i))
fpga.stop()

print(fpga.session, fpga.status)

