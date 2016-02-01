
# Feedback control of interferometer
# Author: Jan Gieseler
# Created:  01/21/2016
# Modified: 01/21/2016

import time
import lib.NI_read_FPGA_AI as NI
import hardware_modules.maestro as maestro
import numpy as np
import hardware_modules.PI_Controler as PI
import matplotlib.pyplot as plt


# ===========================================
#  === settings =============================
# ===========================================

parameter_feedback = {
    'set_point' : 0,
    'P' : 1.0,
    'I' : 0.0,
    'timestep' : 0.1,
    'integrator' : 0,
    'output_range' : {'min': -1000, 'max': 1000}
}


# -------------------------------------------
#  === create handle for server motor control
# -------------------------------------------
# maestro connected to COM8,  (check in device manager for pololu  controler command port)
servo = maestro.Controller('COM8')
# motor connected to channel of maestro controler
motor = maestro.LinearActuator(servo, 5)

# -------------------------------------------
#  === create PI controler ==================
# -------------------------------------------
feedback = PI.PI(**parameter_feedback)

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
plt.hold(True)
motor.position = 0

# todo: change loop such that it stops once it's close enough to the setpoint or some error occured (like detector saturates)
for i in range(20):
    detector_value = AI.read()
    motor_position = feedback.update(detector_value)
    # motor.position = motor_position
    motor.position = i*10
    print(i, int(detector_value), int(motor_position))

    xList.append(i)
    yList.append(detector_value)

    # plot

    makeFig()
    plt.draw()
    # todo: find a better timer  function similar to labview "wait until next ms multiple"
    # to take into account the execution time of the resto of the code in the loop
    plt.pause(parameter_feedback['timestep'])


motor.stop()


# ===========================================
#  === end of script, close connections
# ===========================================
fpga.stop()
servo.close()

raw_input("Please type enter to exit and close plot...")
