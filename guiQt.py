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
import time
import pandas as pd
import Focusing
from matplotlib.backends import qt_compat
from matplotlib.widgets import RectangleSelector
import matplotlib.patches as patches
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import GuiDeviceTriggers as DeviceTriggers

# Extends the matplotlib backend FigureCanvas. A canvas for matplotlib figures with a constructed axis that is
# auto-expanding
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
        self.saveLocImage = QtGui.QLineEdit(self.main_widget)
        self.saveLocImageL = QtGui.QLabel(self.main_widget)
        self.saveLocImageL.setText("Image Save Location")
        self.buttonScan = QtGui.QPushButton('Scan', self.main_widget)
        self.buttonScan.clicked.connect(self.scanBtnClicked)
        self.buttonVSet = QtGui.QPushButton('Set Voltage', self.main_widget)
        self.buttonVSet.clicked.connect(self.vSetBtnClicked)
        self.buttonImageHome = QtGui.QPushButton('Reset Window', self.main_widget)
        self.buttonImageHome.clicked.connect(self.imageHomeClicked)
        self.buttonSaveImage = QtGui.QPushButton('Save Image', self.main_widget)
        self.buttonSaveImage.clicked.connect(self.saveImageClicked)


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
        grid.addWidget(self.saveLocImage,2,10)
        grid.addWidget(self.saveLocImageL,1,10)
        grid.addWidget(self.buttonScan,1,11)
        grid.addWidget(self.buttonVSet,2,11)
        grid.addWidget(self.buttonSaveImage,1,12)
        grid.addWidget(self.buttonImageHome,2,12)
        vbox.addLayout(grid)
        self.imageData = None

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
        self.saveLocZI = QtGui.QLineEdit(self.main_widget)
        self.saveLocZIL = QtGui.QLabel(self.main_widget)
        self.saveLocZIL.setText("Sweep Save Location")
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
        ZILayout.addWidget(self.saveLocZI,2,7)
        ZILayout.addWidget(self.saveLocZIL,1,7)
        ZILayout.addWidget(self.buttonZI,1,8)
        ZILayout.addWidget(self.buttonZILog,2,8)
        ZILayout.addWidget(self.buttonZISave,1,9)
        vbox.addLayout(ZILayout)
        self.ZIData = None

        self.testButton = QtGui.QPushButton('Run Test Code',self.main_widget)
        self.testButton.clicked.connect(self.testButtonClicked)
        vbox.addWidget(self.testButton)


        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.dc.mpl_connect('button_press_event', self.mouseNVImage)

        rectprops = dict(facecolor = 'black', edgecolor = 'black', alpha = 1.0, fill = True)
        self.RS = RectangleSelector(self.dc.axes, self.zoom, button = 3, drawtype='box', rectprops = rectprops)

        self.circ = None

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
            self.writeArray(self.ZIData, self.saveLocZI.text(), ['Frequency', 'Response'])
            self.statusBar().showMessage("Sweep Data Saved",2000)

    def saveImageClicked(self):
        if(self.imageData == None):
            QtGui.QMessageBox.about(self.main_widget, "Image Save Error", "There is no image data to save. Run a scan first.")
        else:
            self.writeArray(self.imageData, self.saveLocImage.text())
            self.statusBar().showMessage("Image Data Saved",2000)

    def scanBtnClicked(self):
        self.statusBar().showMessage("Taking Image",0)
        self.imageData = DeviceTriggers.scanGui(self.dc,float(self.xVoltageMin.text()),float(self.xVoltageMax.text()),float(self.xPts.text()),float(self.yVoltageMin.text()),float(self.yVoltageMax.text()),float(self.yPts.text()),float(self.timePerPt.text()))
        self.xMinHome = float(self.xVoltageMin.text())
        self.xMaxHome = float(self.xVoltageMax.text())
        self.yMinHome = float(self.yVoltageMin.text())
        self.yMaxHome = float(self.yVoltageMax.text())
        self.statusBar().clearMessage()
        self.circ = None

    def vSetBtnClicked(self):
        DeviceTriggers.setDaqPt(float(self.xVoltage.text()),float(self.yVoltage.text()))
        self.statusBar().showMessage("Galvo Position Updated",2000)

    def imageHomeClicked(self):
        self.dc.axes.set_xlim(left = self.xMinHome, right = self.xMaxHome)
        self.dc.axes.set_ylim(bottom = self.yMaxHome, top = self.yMinHome)
        self.dc.draw()

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
                self.drawDot()
                QtGui.QApplication.processEvents()

    def drawDot(self):
        if(not self.circ==None):
            self.circ.remove()
        self.circ = patches.Circle((self.xVoltage.text(), self.yVoltage.text()), .01, fc = 'g')
        self.dc.axes.add_patch(self.circ)
        self.dc.draw()

    def writeArray(self, array, filepath, columns = None):
        df = pd.DataFrame(array, columns = columns)
        if(columns == None):
            header = False
        else:
            header = True
        df.to_csv(filepath, index = False, header=header)

    def testButtonClicked(self):
        print("Test Code")
        Focusing.Focus.scan(48.5, 52.5, 3, waitTime = 0, canvas = self.sc)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""Temp"""
)
qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()