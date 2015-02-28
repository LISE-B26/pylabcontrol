import visa
import time


#cryo = ctypes.WinDLL('C:\\Users\\Experiment\\Downloads\\Cryostation Release 3.46 or later\\CryostationComm.dll')
#cryo.IP_Address = "10.243.34.43"
#cryo.Port = 7773

class Cryostation:
    def __init__(self):
        rm = visa.ResourceManager()
        self.srs = rm.open_resource(u'TCPIP0::10.243.34.43::7773::SOCKET')
        print(self.srs.query('GCP'))

a = Cryostation()