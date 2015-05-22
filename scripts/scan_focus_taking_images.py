__author__ = 'Experiment'


# no finished at all
import functions.ScanPhotodiode as GalvoScan
import hardware_modules.PiezoController as pc
import matplotlib.pyplot as plt

import numpy as np

from functions.save_array_to_disk import *
# set variables

axis = 'X'
xVmin,xVmax,xPts,yVmin,yVmax,yPts = -0.4, 0.4, 120.,  -0.4, 0.4, 120.
timePerPt = 0.001

dirpath = 'Z:/Lab/Cantilever/Measurements/150521_FindSiNi_Beams/ScanZ_and _take_image/'

tag = 'Si3Ni4'

voltages = np.arange(10,70,10)

#run script

for counter, voltage in enumerate(voltages):
    # acquire data
    scanner = GalvoScan.ScanNV(xVmin,xVmax,xPts,yVmin,yVmax,yPts,timePerPt, canvas = None)
    imageData = scanner.scan()

    # change focus
    xController = pc.MDT693A('X')
    xController.setVoltage(voltage)

    # plot image
    fig = plt.figure()
    ax = plt.subplot(1,1,1)
    ax.imshow(imageData, interpolation="nearest")

    # save image and data
    save_image_and_data(fig, imageData, dirpath, '{:s}_V_{:02d}'.format(tag, voltage))