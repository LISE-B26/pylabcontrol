
# Feedback control of interferometer
# Author: Jan Gieseler
# Created:  01/21/2016
# Modified: 01/21/2016

import time
import lib.NI_read_FPGA_AI as NI
import hardware_modules.maestro as maestro
import numpy as np

import matplotlib.pyplot as plt


# ===========================================
#  === settings =============================
# ===========================================

tol = 500



# -------------------------------------------
#  === create handle for server motor control
# -------------------------------------------
# maestro connected to COM8,  (check in device manager for pololu  controler command port)
servo = maestro.Controller('COM8')
# motor connected to channel of maestro controler
motor = maestro.Motor(servo, 5)


# -------------------------------------------
#  === create handle inputs and outputs of FPGA
# -------------------------------------------
fpga = NI.NI7845R()
print(fpga.session, fpga.status)
fpga.start()
print(fpga.session, fpga.status)


# Detector is connected to channel AI1 of FPGA
AI = NI.AnalogInput(1,fpga)



# ===========================================
#  === helper functions
# ===========================================
def makeFig():
    plt.scatter(xList,yList) # I think you meant this



# ===========================================
#  === start script no more settings after this point
# ===========================================


# -------------------------------------------
#  === check if detector output is saturated, if so give warning
# -------------------------------------------
NumberOfAcq = 10
data = np.zeros(NumberOfAcq)
for i in range(NumberOfAcq):
    data[i] =  AI.read()

if np.abs(np.mean(data))> 25000:
    print('WARNING: Detector is saturated ({:0.0f}). Adjust polarization manually before running script.\n SCRIPT NOT EXECUTED '.format(np.mean(data)))
    stop = True
else:
    stop = False

# stop = False

# -------------------------------------------
#  === start PID control
# -------------------------------------------
i = 0

plt.ion() # enable interactivity
fig=plt.figure() # make a figure
xList=list()
yList=list()

while stop == False:
    i = i +1
    val = AI.read()

    xList.append(i)
    yList.append(val)

    if np.abs(val)>tol:
        if val > 0:
            motor.rotate(-500)
        else:
            motor.rotate(500)
    else:
        motor.rotate(0)


    print(i, val)


    # plot

    makeFig()
    plt.draw()
    plt.pause(0.01)


    if i> 50:
        stop = True

motor.stop()


# ===========================================
#  === end of script, close connections
# ===========================================
fpga.stop()
servo.close()
