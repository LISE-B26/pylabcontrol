import visa
import time
import socket


#cryo = ctypes.WinDLL('C:\\Users\\Experiment\\Downloads\\Cryostation Release 3.46 or later\\CryostationComm.dll')
#cryo.IP_Address = "10.243.34.43"
#cryo.Port = 7773

class Cryostation:

    # The default number of seconds before a connection times out
    DEFAULT_TIMEOUT = 5

    def __init__(self, ipAddress, port):
        socket.setdefaulttimeout(self.DEFAULT_TIMEOUT)
        self.ipAddress = ipAddress
        self.port = int(port)

        self.test_connection(ipAddress, port)

    @staticmethod
    def test_connection(ipAddress, port):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.connect((ipAddress, int(port)))
        except Exception, e:
            print ('Could not connect to cryostation. Make sure external control is on, and the IP address (set to %s)'
                   ' and port (set to %s) are correct. Exception: %s' % (ipAddress, str(port), type(e).__name__))

        soc.close()

    @staticmethod
    def extract_data(cryo_response):
        size = int(cryo_response[0:2])
        return float(cryo_response[2:2+size])

    def query_cryostat(self, command):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((self.ipAddress, int(self.port)))
        soc.sendall(command)
        cryo_response = soc.recv(1024)
        soc.close()
        return cryo_response

    def get_platform_temp(self):
        cryo_response = self.query_cryostat('03GPT')
        return self.extract_data(cryo_response)

if __name__ == '__main__':
    a = Cryostation('10.243.34.43', 7773)
    print a.get_platform_temp()