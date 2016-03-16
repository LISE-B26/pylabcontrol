"""
Created on Jan 29 2016

@author: Jan Gieseler

# example code for read and write analog inputs of labview FPGA
# connect AO0 (piezo out) to AI1 (detector in)
# Then run this example.
"""

import time

from src import lib as NI

fpga = NI.NI7845R()

print(fpga.session, fpga.status)
fpga.start()

print(fpga.session, fpga.status)



AI = NI.AnalogInput(1,fpga)
AO = NI.AnalogOutput(0,fpga)

for i in range(0,20000,1000):
    AO.write(i)
    time.sleep(0.1)
    x = AI.read()
    print('set {:05d}\t actual {:05d}\t error {:0.2f}%'.format(i, x, 100.* (x-i) / (x+i)))
fpga.stop()

print(fpga.session, fpga.status)

