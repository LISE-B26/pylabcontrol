import clr
import sys
sys.path.insert(0,"C:\\Users\\Experiment\\Downloads\\DLL for SW 4.0\\Cryostation Release 3.46 or later")

#cryostation = ctypes.WinDLL('C:\Users\Experiment\Downloads\CryostationComm.dll')

print(clr.FindAssembly('CryostationComm'))
clr.AddReference('CryostationComm')

from CryostationComm import cryostation

cryostation.IP_Address = '10.243.34.189'
cryostation.Port = 7773


print cryostation.Connect()

print cryostation.Exit()