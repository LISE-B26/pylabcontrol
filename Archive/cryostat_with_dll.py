import ctypes

cryostation = ctypes.WinDLL('C:\Users\Experiment\Downloads\CryostationComm.dll')

cryostation.IP_Address = '10.243.34.189'
cryostation.Port = 7773


print cryostation.Connect()

print cryostation.Exit()