import matplotlib.pyplot as plt
from helper_functions import reading_writing as rw

import set_pusher as PC
from src.functions import ScanAPD

num_pushes = 70
push_step = 1
cur_voltage = 4
xVmin = -0.0805
yVmin = -0.0730
xVmax = -0.0399
yVmax = -0.0317
xPts = 120
yPts = 120
timePerPt = .002
print(cur_voltage)
PC.set_focus('Y', cur_voltage)
print('taking image')
scanner = ScanAPD.ScanNV(xVmin, xVmax, xPts, yVmin, yVmax, yPts, timePerPt)
imageData = scanner.scan()
print('finished imaging')
fig = plt.imshow(imageData, interpolation='nearest', extent = [xVmin, xVmax, yVmin, yVmax])
dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150807_PushingDiamonds'
tag = 'baseline'
rw.save_image_and_data_plt(imageData, dirpath, tag)




for n in xrange(0, num_pushes):
    cur_voltage += push_step
    print(cur_voltage)
    PC.set_focus('Y', cur_voltage)
    print('taking image')
    scanner = ScanAPD.ScanNV(xVmin, xVmax, xPts, yVmin, yVmax, yPts, timePerPt)
    imageData = scanner.scan()
    print('finished imaging')
    fig = plt.imshow(imageData, interpolation='nearest', extent = [xVmin, xVmax, yVmin, yVmax])
    tag = str(cur_voltage) + 'V'
    rw.save_image_and_data_plt(imageData, dirpath, tag)