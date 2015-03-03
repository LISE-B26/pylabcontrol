import visa
import time
import socket


#cryo = ctypes.WinDLL('C:\\Users\\Experiment\\Downloads\\Cryostation Release 3.46 or later\\CryostationComm.dll')
#cryo.IP_Address = "10.243.34.43"
#cryo.Port = 7773

class Cryostation:
    def __init__(self):
        rm = visa.ResourceManager()
        #self.cryostation = rm.open_resource(u'TCPIP0::10.243.34.43::7773::SOCKET')
        #self.cryostation.write_binary_values('0000000000000011010001110101000001010100')
        #self.cryostation.write_termination = ''
        #print self.cryostation.query('03GPT')
        #print self.cryostation.read()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('10.243.34.43', 7773))

        s.sendall('03GPT')
        data = s.recv(1024)
        s.close()
        print('hi')
        print('received data:', data)
a = Cryostation()