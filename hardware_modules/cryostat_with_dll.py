import ctypes

cryostation = ctypes.WinDLL('C:\Users\Experiment\Downloads\Cryostation Release 3.46 or later\CryostationComm.dll')

cryostation.IP_Address = '10.243.34.43'
cryostation.Port = 7773

print cryostation.Connect()

print cryostation.Exit()