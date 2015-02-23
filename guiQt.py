#!/usr/bin/env python

# embedding_in_qt4.py --- Simple Qt4 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

from __future__ import unicode_literals
import sys
import os
import random
import numpy
import numpy.random
import ZiControl
import time
import ScanTest as GalvoScan
import GalvoTest as DaqOut
from matplotlib.backends import qt_compat
from matplotlib.widgets import RectangleSelector
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, autoscale_on=False)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        self.axes.imshow([[1,2,3],[4,5,6],[7,8,9]], interpolation = "nearest")

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 10) for i in range(9)]
        m = numpy.reshape(l,(3,3))
        self.axes.imshow(m,interpolation = "nearest")
        self.draw()

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main_widget)
        hbox = QtGui.QHBoxLayout()
        self.sc = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.dc = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        hbox.addWidget(self.sc)
        hbox.addWidget(self.dc)
        vbox.addLayout(hbox)

        self.xVoltageMin = QtGui.QLineEdit(self.main_widget)
        self.yVoltageMin = QtGui.QLineEdit(self.main_widget)
        self.xVoltageMax = QtGui.QLineEdit(self.main_widget)
        self.yVoltageMax = QtGui.QLineEdit(self.main_widget)
        self.xPts = QtGui.QLineEdit(self.main_widget)
        self.yPts = QtGui.QLineEdit(self.main_widget)
        self.timePerPt = QtGui.QLineEdit(self.main_widget)
        self.xVoltage = QtGui.QLineEdit(self.main_widget)
        self.yVoltage = QtGui.QLineEdit(self.main_widget)
        self.xVoltageMinL = QtGui.QLabel(self.main_widget)
        self.xVoltageMinL.setText("xVoltsMin:")
        self.yVoltageMinL = QtGui.QLabel(self.main_widget)
        self.yVoltageMinL.setText("yVoltsMin:")
        self.xVoltageMaxL = QtGui.QLabel(self.main_widget)
        self.xVoltageMaxL.setText("xVoltsMax:")
        self.yVoltageMaxL = QtGui.QLabel(self.main_widget)
        self.yVoltageMaxL.setText("yVoltsMax:")
        self.xVoltageL = QtGui.QLabel(self.main_widget)
        self.xVoltageL.setText("xVolts:")
        self.yVoltageL = QtGui.QLabel(self.main_widget)
        self.yVoltageL.setText("yVolts:")
        self.xPtsL = QtGui.QLabel(self.main_widget)
        self.xPtsL.setText("Number of x Points:")
        self.yPtsL = QtGui.QLabel(self.main_widget)
        self.yPtsL.setText("Number of Y Points:")
        self.timePerPtL = QtGui.QLabel(self.main_widget)
        self.timePerPtL.setText("Timer Per Point:")
        self.buttonScan = QtGui.QPushButton('Scan', self.main_widget)
        self.buttonScan.clicked.connect(self.scanBtnClicked)
        self.buttonVSet = QtGui.QPushButton('Set Voltage', self.main_widget)
        self.buttonVSet.clicked.connect(self.vSetBtnClicked)


        grid = QtGui.QGridLayout()
        grid.addWidget(self.xVoltageMin, 2,1)
        grid.addWidget(self.yVoltageMin, 2,2)
        grid.addWidget(self.xVoltageMinL,1,1)
        grid.addWidget(self.yVoltageMinL,1,2)
        grid.addWidget(self.xVoltageMax, 2,3)
        grid.addWidget(self.yVoltageMax, 2,4)
        grid.addWidget(self.xVoltageMaxL,1,3)
        grid.addWidget(self.yVoltageMaxL,1,4)
        grid.addWidget(self.xPts,2,5)
        grid.addWidget(self.xPtsL,1,5)
        grid.addWidget(self.yPts, 2,6)
        grid.addWidget(self.yPtsL, 1,6)
        grid.addWidget(self.timePerPt,2,7)
        grid.addWidget(self.timePerPtL,1,7)
        grid.addWidget(self.xVoltage, 2,8)
        grid.addWidget(self.yVoltage, 2,9)
        grid.addWidget(self.xVoltageL,1,8)
        grid.addWidget(self.yVoltageL,1,9)
        grid.addWidget(self.buttonScan,1,10)
        grid.addWidget(self.buttonVSet,2,10)
        vbox.addLayout(grid)

        ZILayout = QtGui.QGridLayout()
        self.amp = QtGui.QLineEdit(self.main_widget)
        self.ampL = QtGui.QLabel(self.main_widget)
        self.ampL.setText("Amplitude")
        self.offset = QtGui.QLineEdit(self.main_widget)
        self.offsetL = QtGui.QLabel(self.main_widget)
        self.offsetL.setText("Offset")
        self.freqLow = QtGui.QLineEdit(self.main_widget)
        self.freqLowL = QtGui.QLabel(self.main_widget)
        self.freqLowL.setText("Low Frequency")
        self.freqHigh = QtGui.QLineEdit(self.main_widget)
        self.freqHighL = QtGui.QLabel(self.main_widget)
        self.freqHighL.setText("High Frequency")
        self.sampleNum = QtGui.QLineEdit(self.main_widget)
        self.sampleNumL = QtGui.QLabel(self.main_widget)
        self.sampleNumL.setText("Sample Number")
        self.samplePerPt = QtGui.QLineEdit(self.main_widget)
        self.samplePerPtL = QtGui.QLabel(self.main_widget)
        self.samplePerPtL.setText("Samples Per Point")
        self.buttonZI = QtGui.QPushButton('ZI',self.main_widget)
        self.buttonZI.clicked.connect(self.ZIBtnClicked)
        self.buttonZILog = QtGui.QPushButton('Log', self.main_widget)
        self.buttonZILog.setCheckable(True)
        self.buttonZISave = QtGui.QPushButton('Save Sweep', self.main_widget)
        self.buttonZISave.clicked.connect(self.ZISaveClicked)
        ZILayout.addWidget(self.amp,2,1)
        ZILayout.addWidget(self.ampL,1,1)
        ZILayout.addWidget(self.offset,2,2)
        ZILayout.addWidget(self.offsetL,1,2)
        ZILayout.addWidget(self.freqLow,2,3)
        ZILayout.addWidget(self.freqLowL,1,3)
        ZILayout.addWidget(self.freqHigh,2,4)
        ZILayout.addWidget(self.freqHighL,1,4)
        ZILayout.addWidget(self.sampleNum,2,5)
        ZILayout.addWidget(self.sampleNumL,1,5)
        ZILayout.addWidget(self.samplePerPt,2,6)
        ZILayout.addWidget(self.samplePerPtL,1,6)
        ZILayout.addWidget(self.buttonZI,1,7)
        ZILayout.addWidget(self.buttonZILog,2,7)
        ZILayout.addWidget(self.buttonZISave,1,8)
        vbox.addLayout(ZILayout)
        self.ZIData = None


        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.dc.mpl_connect('button_press_event', self.mouseNVImage)

        rectprops = dict(facecolor = 'black', edgecolor = 'black', alpha = 1.0, fill = True)
        self.RS = RectangleSelector(self.dc.axes, self.zoom, button = 3, drawtype='box', rectprops = rectprops)

        #Makes room for status bar at bottom so it doesn't resize the widgets when it is used later
        self.statusBar().showMessage("Temp",1)

    def zoom(self,eclick,erelease):
        self.xVoltageMin.setText(str(eclick.xdata))
        self.yVoltageMin.setText(str(eclick.ydata))
        self.xVoltageMax.setText(str(erelease.xdata))
        self.yVoltageMax.setText(str(erelease.ydata))
        self.dc.axes.set_xlim(left= min(eclick.xdata,erelease.xdata), right = max(eclick.xdata, erelease.xdata))
        self.dc.axes.set_ylim(top= min(eclick.ydata, erelease.ydata),bottom= max(eclick.ydata, erelease.ydata))
        self.dc.draw()


    def ZIBtnClicked(self):
        self.statusBar().showMessage("Taking Frequency Scan",0)
        self.ZIData = DeviceTriggers.ZIGui(self.sc, float(self.amp.text()),float(self.offset.text()), float(self.freqLow.text()),float(self.freqHigh.text()),float(self.sampleNum.text()),float(self.samplePerPt.text()),float(self.buttonZILog.isChecked()))
        self.statusBar().clearMessage()

    def ZISaveClicked(self):
        if(self.ZIData == None):
            QtGui.QMessageBox.about(self.main_widget, "Sweep Save Error", "There is no sweep data to save. Run a sweep first.")
        else:
            self.writeArray(self.ZIData, self.buttonZISave.text())
            self.statusBar().showMessage("Sweep Data Saved",2000)

    def scanBtnClicked(self):
        self.statusBar().showMessage("Taking Image",0)
        DeviceTriggers.scanGui(self.dc,float(self.xVoltageMin.text()),float(self.xVoltageMax.text()),float(self.xPts.text()),float(self.yVoltageMin.text()),float(self.yVoltageMax.text()),float(self.yPts.text()),float(self.timePerPt.text()))
        self.statusBar().clearMessage()

    def vSetBtnClicked(self):
        DeviceTriggers.setDaqPt(float(self.xVoltage.text()),float(self.yVoltage.text()))
        self.statusBar().showMessage("Galvo Position Updated",2000)

    def textUpdate(self):
        a = numpy.random.ranf()
        b = numpy.random.ranf()
        self.xVoltage.setText(str(a))
        self.yVoltage.setText(str(b))

    def mouseNVImage(self,event):
        if(not(event.xdata == None)):
            if(event.button == 1):
                self.xVoltage.setText(str(event.xdata))
                self.yVoltage.setText(str(event.ydata))

    #def writeArray(self, array, filepath):


    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""embedding_in_qt4.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale

This program is a simple example of a Qt4 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
)

class DeviceTriggers():
    @staticmethod
    #def ZIGui(canvas):
    def ZIGui(canvas, amp, offset, freqLow, freqHigh, sampleNum, samplePerPt, xScale):
        zi = ZiControl.ZIHF2(amp, offset, canvas = canvas)
        data = zi.sweep(freqLow, freqHigh, sampleNum, samplePerPt, xScale=0)
        return data

    @staticmethod
    def scanGui(canvas, xVmin, xVmax, xPts, yVmin, yVmax,yPts, timePerPt):
        scanner = GalvoScan.ScanNV(xVmin,xVmax,xPts,yVmin,yVmax,yPts,timePerPt, canvas = canvas)
        scanner.scan()

    @staticmethod
    def setDaqPt(xVolt,yVolt):
        pt = numpy.transpose(numpy.column_stack((xVolt,yVolt)))
        pt = (numpy.repeat(pt, 2, axis=1))
        # prefacing string with b should do nothing in python 2, but otherwise this doesn't work
        pointthread = DaqOut.DaqOutputWave(pt, 1000.0, b"Dev1/ao0:1")
        pointthread.run()
        pointthread.waitToFinish()
        pointthread.stop()
        QtGui.QApplication.processEvents()





qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()