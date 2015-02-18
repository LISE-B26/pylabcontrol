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
from matplotlib.backends import qt_compat
from matplotlib.widgets import RectangleSelector
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, autoscale_on=False)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
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
        #timer = QtCore.QTimer(self)
        #timer.timeout.connect(self.update_figure)
        #timer.start(1000)

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
        self.sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        hbox.addWidget(self.sc)
        hbox.addWidget(self.dc)
        vbox.addLayout(hbox)

        self.xVoltageMin = QtGui.QLineEdit(self.main_widget)
        self.yVoltageMin = QtGui.QLineEdit(self.main_widget)
        self.xVoltageMax = QtGui.QLineEdit(self.main_widget)
        self.yVoltageMax = QtGui.QLineEdit(self.main_widget)
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

        grid = QtGui.QGridLayout()
        grid.addWidget(self.xVoltageMin, 2,1)
        grid.addWidget(self.yVoltageMin, 2,2)
        grid.addWidget(self.xVoltageMinL,1,1)
        grid.addWidget(self.yVoltageMinL,1,2)
        grid.addWidget(self.xVoltageMax, 2,3)
        grid.addWidget(self.yVoltageMax, 2,4)
        grid.addWidget(self.xVoltageMaxL,1,3)
        grid.addWidget(self.yVoltageMaxL,1,4)
        grid.addWidget(self.xVoltage, 2,5)
        grid.addWidget(self.yVoltage, 2,6)
        grid.addWidget(self.xVoltageL,1,5)
        grid.addWidget(self.yVoltageL,1,6)
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
        vbox.addLayout(ZILayout)



        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.dc.mpl_connect('button_press_event', self.mouseNVImage)

        self.RS = RectangleSelector(self.dc.axes, self.zoom, button = 3, drawtype='box')

        #timer = QtCore.QTimer(self)
        #timer.timeout.connect(self.textUpdate)
        #timer.start(500)


    def zoom(self,eclick,erelease):
        self.xVoltageMin.setText(str(eclick.xdata))
        self.yVoltageMin.setText(str(eclick.ydata))
        self.xVoltageMax.setText(str(erelease.xdata))
        self.yVoltageMax.setText(str(erelease.ydata))
        self.dc.axes.set_xlim(left= min(eclick.xdata,erelease.xdata), right = max(eclick.xdata, erelease.xdata))
        self.dc.axes.set_ylim(top= min(eclick.ydata, erelease.ydata),bottom= max(eclick.ydata, erelease.ydata))
        self.dc.draw()


    def ZIBtnClicked(self):
        DeviceTriggers.ZIGui(self.sc, float(self.amp.text()),float(self.offset.text()), float(self.freqLow.text()),float(self.freqHigh.text()),float(self.sampleNum.text()),float(self.samplePerPt.text()),float(self.buttonZILog.isChecked()))

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
        zi.sweep(freqLow, freqHigh, sampleNum, samplePerPt, xScale)
        #zi.sweep( 1e6, 50e6, 100, 10, xScale = 0)




qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()