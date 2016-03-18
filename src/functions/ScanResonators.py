# B26 Lab Code
# Last Update: 1/28/15

# External Connections: Galvo x axis on DAQ channel 0
#                       Galvo y axis on DAQ channel 1
#                       APD input to counter 0 (PFI8)
#                       No external connection to counter 1 out (PFI13)


# import external files
import hardware_modules.ZiControl as ZI
from hardware_modules import GalvoMirrors as DaqOut

# import standard libraries
import numpy
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from src.functions import ScanTest as GalvoScan


class SweepScan():
    def __init__(self, xypairs):
        self.xypairs = xypairs
        self.dt = .001

    # runs scan
    def sweepscan(self, amplitude, offset, freqStart, freqEnd, sampleNum, samplesPerPt, name):
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
            self.filepath = 'C:\Users\Experiment\Desktop\Sweeptest\sweep' + name + str(pointnum) + '.txt'
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

class plotScannedResonator():
    def __init__(self, xminpair,xmaxpair,xpts,yminpair,ymaxpair,ypts,theta,results = False):
        xypairs = defXYpairs.getPairs(xminpair, xmaxpair, xpts, yminpair, ymaxpair, ypts, theta)
        self.x = []
        self.y = []
        self.R = []
        self.results = results
        for pointnum in range(1,self.xpts*self.ypts+1):
            self.x = numpy.append(self.x,xypairs[pointnum-1][0])
            self.y = numpy.append(self.y,xypairs[pointnum-1][1])
            if(self.results == True):
                filepath = 'C:\Users\Experiment\Desktop\Sweeptest\sweep4_' + str(pointnum) + '.txt'
                data = pd.read_csv(filepath)
                self.R = numpy.append(self.R, numpy.max(data['Response']._probes))

    def plotResSweep(self, xmin, xmax, ymin, ymax):
        if(self.results == False):
            raise Exception("In pre-sweep mode, use results=True when initializing to run in processing mode")
            return
        scanner = GalvoScan.ScanNV(xmin,xmax,120,ymin,ymax,120,.001)
        imageData = scanner.scan()
        plt.scatter(self.x,self.y,c=self.R, s=15, edgecolors = 'none', cmap = mpl.cm.cool, norm=mpl.colors.LogNorm())
        plt.colorbar()
        plt.imshow(imageData, cmap = 'pink',interpolation="nearest", extent = [xmin,xmax,ymax,ymin])
        plt.show()

    def plotPreSweep(self, xmin, xmax, ymin, ymax):
        scanner = GalvoScan.ScanNV(xmin,xmax,120,ymin,ymax,120,.001)
        imageData = scanner.scan()
        plt.scatter(self.x,self.y,s=10)
        plt.imshow(imageData, cmap = 'pink',interpolation="nearest", extent = [xmin,xmax,ymax,ymin])
        plt.show()

    def linPlotx(self, lineNum):
        if(self.results == False):
            raise Exception("In pre-sweep mode, use results=True when initializing to run in processing mode")
            return
        x = []
        R = []
        for i in range(0,self.xpts):
            x = numpy.append(x,i+1)
            R = numpy.append(R,self.R[i+(lineNum-1)*self.xpts])
        plt.plot(x,R)
        plt.show()

    def linPloty(self, lineNum):
        if(self.results == False):
            raise Exception("In pre-sweep mode, use results=True when initializing to run in processing mode")
            return
        y = []
        R = []
        for i in range(0,self.ypts):
            y = numpy.append(y,i+1)
            R = numpy.append(R,self.R[i*self.xpts+(lineNum-1)])
        plt.plot(y,R)
        plt.show()

    @staticmethod
    def plotImage():
        xmin = -.4
        xmax = .4
        ymin = -.4
        ymax = .4
        filepath = 'C:\Users\Experiment\Desktop\Sweeptest\\photodiode1.txt'
        imageData = pd.read_csv(filepath)
        plt.imshow(imageData,cmap='pink')
        plt.show()

#Pre-sweep sequence
#point specification
xminpair = 0
xmaxpair = .1
xpts = 9
yminpair = 0
ymaxpair = .1
ypts = 21
theta = -23.7

#image specification
xImMin = -.4
xImMax = .4
yImMin = -.4
yImMax = .4

#Pre-sweep helper_functions
temp = plotScannedResonator(xminpair,xmaxpair,xpts,yminpair,ymaxpair,ypts,theta)
temp.plotPreSweep(xImMin, xImMax, yImMin, yImMax)


#Run Sequence: uses points specified above
#Sweep specifications
amplitude = .2
offset = 2
freqMin = 2000000
freqMax = 2100000
averagingPerPt = 16


xypairs = defXYpairs.getPairs(xminpair, xmaxpair, xpts, yminpair, ymaxpair, ypts, theta)
scanner = SweepScan(xypairs)
scanner.sweepscan(amplitude, offset, freqMin, freqMax, 50, 16)






#amps = [2,.8,.2,.08,.02]
#offset = [4,4,2,2,2]
#name = ['1_','2_','3_','4_','5_']

#xypairs = defXYpairs.getPairs(.2, .228, 15, -.084, .01, 51, -23.7)
#scanner = SweepScan(xypairs)
#scanner.sweepscan(.2, 2, 551000, 553000, 50, 16)
#daq = ZI.ZIHF2(.2, 2, 2000000, ACCoupling=1)
#daq.poll()

#for a,off,n in zip(amps,offset,name):
#    scanner = SweepScan(xypairs)
#    scanner.sweepscan(a, off, 551250, 552250, 150, 16, n)

#temp = plotScannedResonator()
#temp.getData()
#temp.plotResSweep()
#temp.linPlotx(4)
#temp.linPloty(9)
#plotScannedResonator.plotImage()

