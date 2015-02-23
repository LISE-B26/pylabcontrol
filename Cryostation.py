import ctypes


cryo = ctypes.WinDLL('C:\\Users\\Experiment\\Downloads\\Cryostation Release 3.46 or later\\CryostationComm.dll')
cryo.IP_Address = "10.243.34.43"
cryo.Port = 7773

print(cryo.Connect())

#cryo.Exit()