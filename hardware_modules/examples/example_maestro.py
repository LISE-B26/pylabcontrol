import hardware_modules.maestro as maestro
import time

# define com port to communicate with servo (check in device manager for pololu  controler command port)
servo = maestro.Controller('COM8')

# define what to test

test_case = 'filterwheel' # beamblock, motor, controller, filterwheel


# set channel
channel = 4

# ================== test filter wheel =======================
channel = 1
if test_case == 'filterwheel':
    filter = maestro.FilterWheel(servo, channel, {'ND1.0': 4*600, 'LP':4*1550, 'ND2.0':4*2500})
    # filter.goto('ND2.0')
    filter.goto('ND1.0')
    # block1.block()
    # close communication channel
    servo.close()

# ================== test controler =======================
# # set ranges, acceleration etc.
if test_case == 'controller':
    servo.setRange(channel, 2000, 12000)
    servo.setAccel(channel, 0)
    servo.setSpeed(channel, 0)
    servo.setTarget(channel, 6100)

# ================== test motor =======================
if test_case == 'motor':
    motor = maestro.Motor(servo, channel)
    motor.rotate(1000)

    time.sleep(2)
    # motor.rotate(0)

    motor.stop()
# ================== test beam block =======================
if test_case == 'beamblock':
    block1 = maestro.BeamBlock(servo, channel)
    # block1.open()
    block1.block()
    # close communication channel
    servo.close()


