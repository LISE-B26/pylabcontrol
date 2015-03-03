import numpy
import ScanTest as GalvoScan
import GalvoTest as DaqOut
import PiezoController

normalRange = 1.0
scanRange = normalRange/10




class Focus:
    def scan(self, minV, maxV, numPts, xChannel, yChannel):
        #voltRange = numpy.linspace(minV, maxV, numPts)
        #(xInit, yInit, ,) = DaqOut.getOutputVoltages()
        (self.xInit, self.yInit, _, _) = DaqOut.DaqOutputWave.getOutputVoltages()
        #for voltage in voltRange:


    #def fit(self):


a = Focus()
a.scan(0,1,2,0,1)