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

# # Feedback control of interferometer
# # Author: Jan Gieseler
# # Created:  01/21/2016
# # Modified: 01/21/2016
#
# import time
# import lib.NI_read_FPGA_AI as NI
# import hardware_modules.maestro as maestro
#
#
# # ===========================================
# #  === create handle for server motor control
# # ===========================================
# # maestro connected to COM8,  (check in device manager for pololu  controler command port)
# # servo = maestro.Controller('COM8')
# # motor connected to channel of maestro controler
# # motor = maestro.Motor(servo, 5)
#
#
# # ===========================================
# #  === create handle inputs and outputs of FPGA
# # ===========================================
# fpga = NI.NI7845R()
# print(fpga.session, fpga.status)
# fpga.start()
# print(fpga.session, fpga.status)
#
#
#
# AI = NI.AnalogInput(1,fpga)
# AO = NI.AnalogOutput(4,fpga)
#
# # Detector is connected to channel AI1 of FPGA
# AI = NI.AnalogInput(1,fpga)
# # Servo-motor is connected to channel AO4 of FPGA
# AO = NI.AnalogOutput(4,fpga)
#
#
#
# # ===========================================
# #  === check if detector output is saturated, if so give warning
# # ===========================================
#
#
#
#
# # ===========================================
# #  === start PID control
# # ===========================================
# i = 0
# stop = False
# while stop == False:
#     i = i +1
#     x = AI.read()
#     print(i, x)
#
#     if i> 5:
#         stop = True
#
#
# # for i in range(0,20000,1000):
# #     AO.write(i)
# #     time.sleep(0.1)
# #     x = AI.read()
# #     print(i, x, 100.* (x-i) / (x+i))
#
#
# # ===========================================
# #  === end of script, close connections
# # ===========================================
# fpga.stop()
# # servo.close()
