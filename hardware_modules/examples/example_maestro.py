import hardware_modules.maestro as maestro
import time

# define com port to communicate with servo (check in device manager for pololu  controler command port)
servo = maestro.Controller('COM8')
# set channel
channel = 5

# ================== test controler =======================
# # set ranges, acceleration etc.
# servo.setRange(channel, 2000, 12000)
# servo.setAccel(channel, 0)
# servo.setSpeed(channel, 0)
# servo.setTarget(channel, 6100)

# ================== test motor =======================
motor = maestro.Motor(servo, channel)
motor.rotate(1000)

time.sleep(1)
motor.rotate(0)
# ================== test beam block =======================
# block1 = maestro.BeamBlock(servo, 4)
# block1.open()
# block1.block()
# servo.setTarget(channel, 5000)
# read position
print(servo.getPosition(channel))
print([0] * 24)
# close communication channel
servo.close()