import numpy, ctypes

CLOCK_FREQUENCY = 400E6
PULSE_PROGRAM = 0

pulseBlaster = ctypes.WinDLL('C:\SpinCore\SpinAPI\dll\spinapi64.dll')

a = pulseBlaster.pb_init()
print a

pulseBlaster.pb_core_clock(ctypes.c_double(CLOCK_FREQUENCY))
c = pulseBlaster.pb_start_programming(PULSE_PROGRAM)
print c



d = pulseBlaster.pb_stop_programming()
print d

b = pulseBlaster.pb_close()
print b