# test script for LavView FPGA
import time
import lib.NI_read_FPGA_AI as NI

fpga = NI.NI7845R()

print(fpga.session, fpga.status)
fpga.start()

print(fpga.session, fpga.status)



AI = NI.AnalogInput(1,fpga)
AO = NI.AnalogOutput(4,fpga)

for i in range(0,20000,1000):
    AO.write(i)
    time.sleep(0.1)
    x = AI.read()
    print(i, x, 100.* (x-i) / (x+i))
fpga.stop()

print(fpga.session, fpga.status)

