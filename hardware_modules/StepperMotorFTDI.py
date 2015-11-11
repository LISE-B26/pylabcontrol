from pylibftdi.examples import list_devices as ld

class TST001:
    def __init__(self):
        print('hi')

(ld.get_ftdi_device_list())
