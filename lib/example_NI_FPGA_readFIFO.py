"""
Created on Jan 29 2016

@author: Jan Gieseler

# example code for how to read from FIFO
# connect AO0 (piezo out) to AI1 (detector in)
# Then run this example. You should see steps.
# This example increases the piezo output stepwise, while writting
# the detector input into the FIFO
"""


import time
import lib.FPGA_PID_Loop_Simple as NI
import matplotlib.pyplot as plt
import numpy as np



# ============= DEFINE PARAMETERS ==================================
# ==================================================================
parameters_PI = {
    "sample_period_PI" :4e5,
    "gains" : {'proportional': 1.0, 'integral':0.1},
    "setpoint" : 0,
    "piezo" : 0
}

parameters_Acq = {
    "sample_period_acq" : 100,
    "data_length" : 2000,
    "block_size" : 100
}



# ========== START FPGA =============
fpga = NI.NI7845R()
fpga.start()


AI = NI.NI_FPGA_READ_FIFO(fpga, **parameters_Acq)
# create PI (proportional integral) controler object to have access to piezo output channel (i.e. AO0)
PI = NI.NI_FPGA_PI(fpga, **parameters_PI)

print('sample rate', 40e6 / parameters_Acq['sample_period_acq'])

PI.piezo = 200

print('--------- start acquisition --------')
AI.start_acquisition()
print('--------- start piezo output --------')
for i in range(10):
    PI.piezo = i+2 * 100

status = AI.status
print("status after running acquisition:")
for elem in status:
    print(elem, ': ', AI.status[elem])


number_of_reads = int(np.ceil(1.0 * parameters_Acq['data_length'] / parameters_Acq['block_size']))
print('number_of_reads', number_of_reads)

data_AI1 = np.zeros((number_of_reads, parameters_Acq['block_size']))

elements_left = -1. * np.ones(number_of_reads)
for i in range(number_of_reads):
    fifo_data =AI.data_queue.get()
    data_AI1[i,:] =  np.array(fifo_data[0])
    elements_left[i] = int(fifo_data[2])

print('finished')


print('elements left after each block read from FIFO')
print(elements_left)

plt.ion() # enable interactivity
fig=plt.figure() # make a figure
plt.hold(True)
print('plot')
plt.plot(data_AI1.flatten())

plt.show()


# ============= STOP FPGA ==========================================
# ==================================================================
fpga.stop()


