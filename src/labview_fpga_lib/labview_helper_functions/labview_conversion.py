"""

some helper function for conversion of units and such


"""




def int_to_voltage(integer):
    return (10*integer)/32767.

def voltage_to_int(voltage):
    # TODO: make it work for arrays and lists
    return int((voltage * 32767)/10)

def time_to_buffersize(time, ticks=56):
    return int(time / (ticks*0.000000025))

def buffersize_to_time(size, ticks=56):
    return size * (ticks*0.000000025)