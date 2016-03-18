import socket
import time
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema


#cryo = ctypes.WinDLL('C:\\Users\\Experiment\\Downloads\\Cryostation Release 3.46 or later\\CryostationComm.dll')
#cryo.IP_Address = "10.243.34.43"
#cryo.Port = 7773

class Cryostation:

    # The default number of seconds before a connection times out
    DEFAULT_TIMEOUT = None

    def __init__(self, ip_address, port):
        socket.setdefaulttimeout(self.DEFAULT_TIMEOUT)
        self.ip_address = ip_address
        self.port = int(port)

        self.test_connection(ip_address, port)

    @staticmethod
    def test_connection(ipAddress, port):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.connect((ipAddress, int(port)))
        except Exception, e:
            print ('Could not connect to cryostation. Make sure external control is on, and the IP address (set to %s)'
                   ' and port (set to %s) are correct. Exception: %s' % (ipAddress, str(port), type(e).__name__))
            raise

        soc.close()

    @staticmethod
    def extract_data(cryostat_response):
        size = int(cryostat_response[0:2])
        return cryostat_response[2:2+size]

    def query_cryostat(self, command):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.connect((self.ip_address, int(self.port)))
        except Exception, e:
            print('Connection was lost sometime since cryostation instantiation. Unable to query cryostation with'
                  'command ' + command)
            raise

        soc.sendall(command)
        cryostat_response = soc.recv(1024)
        soc.close()
        return cryostat_response

    def get_platform_temp(self):
        cryostat_response = self.query_cryostat('03GPT')
        time.sleep(.1)
        return float(self.extract_data(cryostat_response))

    def get_stage_one_heater_power(self):
        cryostat_response = self.query_cryostat('05GS1HP')
        return float(self.extract_data(cryostat_response))

    def get_stage_one_temp(self):
        cryostat_response = self.query_cryostat('04GS1T')
        time.sleep(.1)
        return float(self.extract_data(cryostat_response))

    def get_stage_two_temp(self):
        cryostat_response = self.query_cryostat('04GS2T')
        time.sleep(.1)
        return float(self.extract_data(cryostat_response))

    def get_sample_stability(self):
        cryostat_response = self.query_cryostat('03GSS')
        return float(self.extract_data(cryostat_response))

    def get_sample_temp(self):
        cryostat_response = self.query_cryostat('03GST')
        time.sleep(.1)
        data = float(self.extract_data(cryostat_response))
        if data == -1.0:
            print 'Warning: Cryostat sample temperature not available. The sample thermometer may be disconnected'

        return data

    def reset_pid_params(self):
        cryostat_response = self.query_cryostat('04RPID')
        return self.extract_data(cryostat_response)

    def start_cool_down(self):
        cryostat_response = self.query_cryostat('03SCD')
        return self.extract_data(cryostat_response)

    def start_standby(self):
        cryostat_response = self.query_cryostat('03SSB')
        return self.extract_data(cryostat_response)

    def start_warm_up(self):
        cryostat_response = self.query_cryostat('03SWU')
        return self.extract_data(cryostat_response)

    def set_temp_setpoint(self, setpoint_temp):
        setpoint_temp = float(setpoint_temp)
        assert (setpoint_temp >= 2.00) and (setpoint_temp <= 350.00)
        formatted_setpoint_temp = '{:.2f}'.format(setpoint_temp)
        total_string_length = len('STSP') + len(formatted_setpoint_temp)
        cryostat_command = '{:0>2}STSP'.format(total_string_length) + formatted_setpoint_temp
        cryostat_response = self.query_cryostat(cryostat_command)
        return self.extract_data(cryostat_response)

    def get_chamber_pressure(self):
        cryostat_response = self.query_cryostat('03GCP')
        return self.extract_data(cryostat_response)

class TemperatureData:
    @staticmethod
    def get_temp_data(date = None, initial_time = 0):
        if date == None:
            filepath = 'C:/Cryostation/Temperature Data/MI_DiagnosticsDataLog ' + time.strftime('%m_%d_%Y') + '.csv'
            print(filepath)
        else:
            filepath = 'C:/Cryostation/Temperature Data/MI_DiagnosticsDataLog ' + date + '.csv'
        mat = pd.read_csv(filepath)._probes
        times = [x.split(':') for x in mat[:,1]]
        times = [[float(x[0])*3600+float(x[1])*60+float(x[2])][0] for x in times]
        if initial_time == 0:
            times = [x - times[0] for x in times]
        else:
            times = [x + initial_time for x in times]
        temps = mat[:,3:8]
        data = np.column_stack((times,temps))
        return data


#if __name__ == '__main__':
#    a = Cryostation('10.243.34.189', 7773)
#    print a.get_platform_temp()

#print(TemperatureData.get_temp_data(date = '01_13_2016', initial_time=0))