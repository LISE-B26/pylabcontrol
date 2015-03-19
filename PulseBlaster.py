import numpy, ctypes, time

CLOCK_FREQUENCY = 400E6
PULSE_PROGRAM = 0


pulse_blaster = ctypes.WinDLL('C:\Windows\System32\spinapi64.dll')

a = pulse_blaster.pb_init()
print a

pulse_blaster.pb_core_clock(ctypes.c_double(CLOCK_FREQUENCY))
c = pulse_blaster.pb_start_programming(PULSE_PROGRAM)
print c

channel = 0
start = pulse_blaster.pb_inst_pbonly(0xE00000 | 1, 0, 0, ctypes.c_double(200000))
print start
ins1 = pulse_blaster.pb_inst_pbonly(0, 0, 0, ctypes.c_double(100000))
ins2 = pulse_blaster.pb_inst_pbonly(0, 6, start, ctypes.c_double(100000))
print ins1
print ins2
d = pulse_blaster.pb_stop_programming()
print d

pulse_blaster.pb_start()

e = pulse_blaster.pb_read_status()
print e

pulse_blaster.pb_stop()
b = pulse_blaster.pb_close()
print b