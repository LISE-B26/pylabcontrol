# B26 Lab Code
# Last Update: 1/28/15

# External Connections: Galvo x axis on DAQ channel 0
#                       Galvo y axis on DAQ channel 1
#                       APD input to counter 0 (PFI8)
#                       No external connection to counter 1 out (PFI13)


# import external files
import GalvoTest as DaqOut
import ZiControl as ZI
# import standard libraries
import numpy
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

class SweepScan():
    def __init__(self, xypairs):
        self.xypairs = xypairs
        self.dt = .001

    # runs scan
    def sweepscan(self, amplitude, offset, freqStart, freqEnd, sampleNum, samplesPerPt):
        self.sweeper = ZI.ZIHF2(amplitude, offset, 500000, ACCoupling=1)
        pointnum = 1
        for point in self.xypairs:
            self.initPt = numpy.transpose(numpy.column_stack((point[0], point[1])))
            self.initPt = (numpy.repeat(self.initPt, 2, axis=1))
            # move galvo to first point in line
            pointthread = DaqOut.DaqOutputWave(self.initPt, 1 / self.dt, "Dev1/ao0:1")
            pointthread.run()
            pointthread.waitToFinish()
            pointthread.stop()
            self.sweepData = self.sweeper.sweep(freqStart, freqEnd, sampleNum, samplesPerPt)
            self.filepath = 'C:\Users\Experiment\Desktop\Sweeptest\sweep' + str(pointnum) + '.txt'
            self.writeArray(self.sweepData, self.filepath, ['Frequency', 'Response'])
            pointnum += 1

    def resonancescan(self, amplitude, offset, freq):
        self.scanner = ZI.ZIHF2(amplitude, offset, freq, ACCoupling=1)
        x = []
        y = []
        R = []
        for point in self.xypairs:
            self.initPt = numpy.transpose(numpy.column_stack((point[0], point[1])))
            self.initPt = (numpy.repeat(self.initPt, 2, axis=1))
            # move galvo to first point in line
            pointthread = DaqOut.DaqOutputWave(self.initPt, 1 / self.dt, "Dev1/ao0:1")
            pointthread.run()
            pointthread.waitToFinish()
            pointthread.stop()
            x = numpy.append(x,point[0])
            y = numpy.append(y,point[1])
            R = numpy.append(R,self.scanner.poll())
        #self.filepath = 'C:\Users\Experiment\Desktop\Sweeptest\scan.txt'
        #self.writeArray(R, self.filepath, ['Frequency', 'Response'])
        plt.scatter(x,y,c=R,s=20, cmap = mpl.cm.pink)
        plt.show()

    def writeArray(self, array, filepath, columns = None):
        df = pd.DataFrame(array, columns = columns)
        if(columns == None):
            header = False
        else:
            header = True
        df.to_csv(filepath, index = False, header=header)

class defXYpairs():
    @staticmethod
    def getPairs(xMin, xMax, xPts, yMin, yMax, yPts, theta):
        theta = theta*numpy.pi/180
        xArray = numpy.linspace(xMin, xMax, xPts)
        yArray = numpy.linspace(yMin, yMax, yPts)
        xypairs = numpy.transpose([numpy.tile(xArray, len(yArray)), numpy.repeat(yArray, len(xArray))])
        xAve = (xMax+xMin)/2
        yAve = (yMax+yMin)/2
        shift = [xAve,yAve]
        rotmat = [[numpy.cos(theta),-numpy.sin(theta)],[numpy.sin(theta),numpy.cos(theta)]]
        i=0
        for point in xypairs:
            xypairs[i] = numpy.dot(rotmat,point-shift)+shift
            i+=1
        return xypairs

xypairs = defXYpairs.getPairs(.2058, .2295, 9, -.07713, -.003625, 25, -23.7)
#print(xypairs)
#x = [xypairs[0][0],xypairs[8][0],xypairs[216][0],xypairs[224][0]]
#y = [xypairs[0][1],xypairs[8][1],xypairs[216][1], xypairs[224][1]]
#plt.scatter(x,y)
#plt.show()
#scanner = SweepScan(xypairs)
#scanner.sweepscan(.2, 2, 551000, 553000, 50, 16)
#daq = ZI.ZIHF2(.2, 2, 2000000, ACCoupling=1)
#daq.poll()
scanner = SweepScan(xypairs)
scanner.resonancescan(.2,2,551900)

