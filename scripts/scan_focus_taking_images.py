__author__ = 'Experiment'


import functions.ScanPhotodiode_DAQ as GalvoScan
import hardware_modules.PiezoController as pc
import matplotlib.pyplot as plt

import numpy as np

from functions.ReadWriteCommands import *

# set variables =============================================
# ===========================================================

axis = 'X'
xVmin,xVmax,xPts,yVmin,yVmax,yPts = -0.4, 0.4, 120.,  -0.4, 0.4, 120.
timePerPt = 0.001

dirpath = 'Z:/Lab/Cantilever/Measurements/150526_Silicon_nitride_with_1um_pads/Box_c4_r3_SCanFocus/'

tag = 'Si3Ni4_withPads'

voltages = np.arange(50,90,10)

#run script =================================================
# ===========================================================

for counter, voltage in enumerate(voltages):
    # set focus
    xController = pc.MDT693A('X')
    xController.setVoltage(voltage)

    # acquire data
    scanner = GalvoScan.ScanNV(xVmin,xVmax,xPts,yVmin,yVmax,yPts,timePerPt, canvas = None)
    imageData = scanner.scan()



    # plot image
    fig = plt.figure()
    ax = plt.subplot(1,1,1)
    ax.imshow(imageData, interpolation="nearest")

    # save image and data
    save_image_and_data(fig, imageData, dirpath, '{:s}_V_{:02d}'.format(tag, voltage))