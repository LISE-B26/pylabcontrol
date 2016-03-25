from pylibftdi.examples import list_devices as ld
from pylibftdi import USB_VID_LIST, USB_PID_LIST

class TST001:
    def __init__(self):
        print('hi')

if __name__ == '__main__':
    USB_PID_LIST.append(0xfaf0)
    print(ld.get_ftdi_device_list())
    print(map(hex, USB_VID_LIST))
    print(map(hex, USB_PID_LIST))