import maestro
from time import sleep
servo = maestro.Controller('COM5')
# servo.setAccel(0,3)      #set servo 0 acceleration to 4
# servo.setTarget(0,6000)  #set servo to move to center position
# servo.setTarget(0,1000)  #set servo to move to center position
channel = 5
servo.setRange(channel, 4500, 7500)
servo.setAccel(channel,4)      #set servo 0 acceleration to 4
servo.setSpeed(channel,10)
servo.setTarget(channel,6600)  #set servo to move to center position
# for channel in range(0, 5, 1):
#     # print('min {:d}\t max {:d}'.format(servo.getMin(channel), servo.getMax(channel)))
#     print(servo.getPosition(channel))
# servo.stopScript()


print servo.Targets
# print servo.getMovingState()
sleep(0.33)
print('x')

pos = servo.getPosition(channel)
print(pos)

servo.setTarget(channel,5400)  #set servo to move to center position
sleep(0.23)
pos = servo.getPosition(channel)
print(pos)
servo.goHome()
pos = servo.getPosition(channel)
print('x2')
print(pos)
servo.close()
import sys
import glob
import serial


# def serial_ports():
#     """ Lists serial port names
#
#         :raises EnvironmentError:
#             On unsupported or unknown platforms
#         :returns:
#             A list of the serial ports available on the system
#     """
#     if sys.platform.startswith('win'):
#         ports = ['COM%s' % (i + 1) for i in range(256)]
#     elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
#         # this excludes your current terminal "/dev/tty"
#         ports = glob.glob('/dev/tty[A-Za-z]*')
#     elif sys.platform.startswith('darwin'):
#         ports = glob.glob('/dev/tty.*')
#     else:
#         raise EnvironmentError('Unsupported platform')
#
#     result = []
#     for port in ports:
#         try:
#             s = serial.Serial(port)
#             s.close()
#             result.append(port)
#         except (OSError, serial.SerialException):
#             pass
#     return result
#
#
# if __name__ == '__main__':
#     print(serial_ports())