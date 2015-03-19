import pylab
import time
import random
import matplotlib.pyplot as plt
import numpy


class Test:
    def test(self):
        x = numpy.linspace(-10,10)
        y = self.gaussian(x,1,0,5)
        plt.plot(x,y)

    def gaussian(x,a,x0,sigma):
        return a*numpy.exp(-(x-x0)**2/(2*sigma**2))


Test.test()