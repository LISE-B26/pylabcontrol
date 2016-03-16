import matplotlib.pyplot as plt
from hardware_modules import MicrowaveGenerator
from helper_functions import reading_writing as rw

from src.functions import ScanAPD


def init_mwgen(rf_power):
    mwgen = MicrowaveGenerator.SG384()
    mwgen.setAmplitude(rf_power)
    return mwgen



num_images = 60
wait_time = 5
xVmin = 0.0206
yVmin = -0.1191
xVmax = 0.0787
yVmax = -0.0607
xPts = 120
yPts = 120
timePerPt = .002

print('taking image')
scanner = ScanAPD.ScanNV(xVmin, xVmax, xPts, yVmin, yVmax, yPts, timePerPt)
imageData = scanner.scan()
print('finished imaging')
fig = plt.imshow(imageData, interpolation='nearest', extent = [xVmin, xVmax, yVmin, yVmax])
dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150828_RFDrift'
tag = 'baseline'
rw.save_image_and_data_plt(imageData, dirpath, tag)

mw = init_mwgen(16)
mw.outputOn()

for n in xrange(0, num_images):
    print('taking image')
    scanner = ScanAPD.ScanNV(xVmin, xVmax, xPts, yVmin, yVmax, yPts, timePerPt)
    imageData = scanner.scan()
    print('finished imaging')
    fig = plt.imshow(imageData, interpolation='nearest', extent = [xVmin, xVmax, yVmin, yVmax])
    tag = 'iteration' + str(n)
    rw.save_image_and_data_plt(imageData, dirpath, tag)