# B26 Lab Code
# Last Update: 2/3/15
import serial

def scan():
   # scan for available ports. return a list of tuples (num, name)
   available = []
   for i in range(256):
       try:
           s = serial.Serial(i)
           available.append( (i, s.portstr))
           s.close()
       except serial.SerialException:
           pass
   return available

print "Found ports:"
for n,s in scan(): print "(%d) %s" % (n,s)
print('done')