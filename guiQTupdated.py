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
from GuiDeviceTriggers import DeviceTriggers

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

        self.vbox = QtGui.QVBoxLayout(self.main_widget)
        self.plotBox = QtGui.QHBoxLayout()
        self.vbox.addLayout(self.plotBox)

        self.ZIPlot = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
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
        self.plotBox.addWidget(self.ZIPlot)
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
        self.vbox.addLayout(ZILayout)
        self.ZIData = None

        self.testButton = QtGui.QPushButton('Run Test Code',self.main_widget)
        self.testButton.clicked.connect(self.testButtonClicked)
        self.vbox.addWidget(self.testButton)


        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        #Makes room for status bar at bottom so it doesn't resize the widgets when it is used later
        self.statusBar().showMessage("Temp",1)

    def zoom(self,eclick,erelease):
        self.xVoltageMin.setText(str(eclick.xdata))
        self.yVoltageMin.setText(str(eclick.ydata))
        self.xVoltageMax.setText(str(erelease.xdata))
        self.yVoltageMax.setText(str(erelease.ydata))
        self.imPlot.axes.set_xlim(left= min(eclick.xdata,erelease.xdata), right = max(eclick.xdata, erelease.xdata))
        self.imPlot.axes.set_ylim(top= min(eclick.ydata, erelease.ydata),bottom= max(eclick.ydata, erelease.ydata))
        self.imPlot.draw()


    def ZIBtnClicked(self):
        self.statusBar().showMessage("Taking Frequency Scan",0)
        self.ZIData = DeviceTriggers.ZIGui(self.ZIPlot, float(self.amp.text()),float(self.offset.text()), float(self.freqLow.text()),float(self.freqHigh.text()),float(self.sampleNum.text()),float(self.samplePerPt.text()),float(self.buttonZILog.isChecked()))
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
        self.imageData = DeviceTriggers.scanGui(self.imPlot,float(self.xVoltageMin.text()),float(self.xVoltageMax.text()),float(self.xPts.text()),float(self.yVoltageMin.text()),float(self.yVoltageMax.text()),float(self.yPts.text()),float(self.timePerPt.text()))
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
        self.imPlot.axes.set_xlim(left = self.xMinHome, right = self.xMaxHome)
        self.imPlot.axes.set_ylim(bottom = self.yMaxHome, top = self.yMinHome)
        self.imPlot.draw()

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
        self.imPlot.axes.add_patch(self.circ)
        self.imPlot.draw()

    def writeArray(self, array, filepath, columns = None):
        df = pd.DataFrame(array, columns = columns)
        if(columns == None):
            header = False
        else:
            header = True
        df.to_csv(filepath, index = False, header=header)

    def cbarThreshClicked(self):
        DeviceTriggers.updateColorbar(self.imageData, self.imPlot, [self.xMinHome, self.xMaxHome, self.yMinHome, self.yMaxHome], float(self.cbarMax.text()))

    def testButtonClicked(self):
        print("Test Code")
        self.addScan(self.vbox, self.plotBox)
        time.sleep(2)
        self.removeScan(self.plotBox)


    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""Temp"""
)

    def addScan(self, vbox, plotBox):
        self.imPlot = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
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
        self.cbarMax = QtGui.QLineEdit(self.main_widget)
        self.cbarMaxL = QtGui.QLabel(self.main_widget)
        self.cbarMaxL.setText("Colorbar Threshold")
        self.buttonCbarThresh = QtGui.QPushButton('Update Colorbar', self.main_widget)
        self.buttonCbarThresh.clicked.connect(self.cbarThreshClicked)

        #set initial values for scan values
        self.xVoltageMin.setText('-.4')
        self.yVoltageMin.setText('-.4')
        self.xVoltageMax.setText('.4')
        self.yVoltageMax.setText('.4')
        self.xPts.setText('120')
        self.yPts.setText('120')
        self.timePerPt.setText('.001')



        plotBox.addWidget(self.imPlot)
        self.scanLayout = QtGui.QGridLayout()
        self.scanLayout.addWidget(self.xVoltageMin, 2,1)
        self.scanLayout.addWidget(self.yVoltageMin, 2,2)
        self.scanLayout.addWidget(self.xVoltageMinL,1,1)
        self.scanLayout.addWidget(self.yVoltageMinL,1,2)
        self.scanLayout.addWidget(self.xVoltageMax, 2,3)
        self.scanLayout.addWidget(self.yVoltageMax, 2,4)
        self.scanLayout.addWidget(self.xVoltageMaxL,1,3)
        self.scanLayout.addWidget(self.yVoltageMaxL,1,4)
        self.scanLayout.addWidget(self.xPts,2,5)
        self.scanLayout.addWidget(self.xPtsL,1,5)
        self.scanLayout.addWidget(self.yPts, 2,6)
        self.scanLayout.addWidget(self.yPtsL, 1,6)
        self.scanLayout.addWidget(self.timePerPt,2,7)
        self.scanLayout.addWidget(self.timePerPtL,1,7)
        self.scanLayout.addWidget(self.xVoltage, 2,8)
        self.scanLayout.addWidget(self.yVoltage, 2,9)
        self.scanLayout.addWidget(self.xVoltageL,1,8)
        self.scanLayout.addWidget(self.yVoltageL,1,9)
        self.scanLayout.addWidget(self.saveLocImage,2,10)
        self.scanLayout.addWidget(self.saveLocImageL,1,10)
        self.scanLayout.addWidget(self.buttonScan,1,11)
        self.scanLayout.addWidget(self.buttonVSet,2,11)
        self.scanLayout.addWidget(self.buttonSaveImage,1,12)
        self.scanLayout.addWidget(self.buttonImageHome,2,12)
        self.scanLayout.addWidget(self.cbarMax,2,13)
        self.scanLayout.addWidget(self.cbarMaxL,1,13)
        self.scanLayout.addWidget(self.buttonCbarThresh,2,14)
        vbox.addLayout(self.scanLayout)
        self.imageData = None

        self.imPlot.mpl_connect('button_press_event', self.mouseNVImage)
        rectprops = dict(facecolor = 'black', edgecolor = 'black', alpha = 1.0, fill = True)
        self.RS = RectangleSelector(self.imPlot.axes, self.zoom, button = 3, drawtype='box', rectprops = rectprops)

        self.circ = None

        QtGui.QApplication.processEvents()

    def removeScan(self, plotBox):
        self.clearLayout(self.scanLayout)
        self.imPlot.deleteLater()
        QtGui.QApplication.processEvents()

    def addZI(self):
        self.ZIPlot = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
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
        self.plotBox.addWidget(self.ZIPlot)
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
        self.vbox.addLayout(ZILayout)
        self.ZIData = None

    def clearLayout(self, layout):
        if layout != None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())



qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
progname = 'Experiment Gui'
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()