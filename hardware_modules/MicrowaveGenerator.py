import visa
from tendo import singleton
import time

class SG384():
    def __init__(self):
        s = singleton.SingleInstance()
        rm = visa.ResourceManager()
        self.srs = rm.open_resource(u'GPIB0::27::INSTR')

    def outputOn(self):
        self.srs.write('ENBR' + str(1))

    def outputOff(self):
        self.srs.write('ENBR' + str(0))

    def setFreq(self, frequency):
        self.srs.write('FREQ ' + str(frequency))

    def setPhase(self, phase):
        self.srs.write('PHAS ' + str(phase))

    def setAmplitude(self, amplitude):
        self.srs.write('AMPR ' + str(amplitude))

    def modOn(self):
        self.srs.write('MODL' + str(1))

    def modOff(self):
        self.srs.write('MODL' + str(0))

    def setModFreq(self):
        self.srs.write('TYPE 1')

    def setModExt(self):
        self.srs.write('MFNC 5')

    def setModIQ(self):
        self.srs.write('TYPE 6')

    def setIQExt(self):
        self.srs.write('PFNC 5')

    def setModFreqDeviation(self, dev):
        self.srs.write('FDEV' + str(dev))