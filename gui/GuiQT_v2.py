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
import time
import Queue
import json

import numpy
import numpy.random
import pandas as pd
from matplotlib.widgets import RectangleSelector
import matplotlib.patches as patches
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import scipy.spatial
import matplotlib.pyplot as plt

import functions.Focusing as focusing
from functions.regions import *
from functions import track_NVs as track
from hardware_modules import PiezoController as PC
from scripts import ESR
from gui import GuiDeviceTriggers as DeviceTriggers, PlotAPDCounts





# Extends the matplotlib backend FigureCanvas. A canvas for matplotlib figures with a constructed axis that is
# auto-expanding
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a Fi   gureCanvasAgg, etc.)."""
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
        self.setMinimumSize(1500,800)

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

        self.testButton = QtGui.QPushButton('Run Test Code',self.main_widget)
        self.testButton.clicked.connect(self.testButtonClicked)
        self.vbox.addWidget(self.testButton)


        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.initUI()


        #Makes room for status bar at bottom so it doesn't resize the widgets when it is used later
        self.statusBar().showMessage("Temp",1)

        self.adjustSize()

        def sizeHint(self):
            return QtCore.QSize(5000, 5000)

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
        self.saveLocImage.setText('Z:\\Lab\\Cantilever\\Measurements\\Images')
        self.saveLocImageL = QtGui.QLabel(self.main_widget)
        self.saveLocImageL.setText("Image Location")
        self.saveTagImage = QtGui.QLineEdit(self.main_widget)
        self.saveTagImage.setText('Image')
        self.saveTagImageL = QtGui.QLabel(self.main_widget)
        self.saveTagImageL.setText("Tag")
        self.buttonScan = QtGui.QPushButton('Scan', self.main_widget)
        self.buttonScan.clicked.connect(self.scanBtnClicked)
        self.buttonVSet = QtGui.QPushButton('Set Voltage', self.main_widget)
        self.buttonVSet.clicked.connect(self.vSetBtnClicked)

        self.buttonSaveImage = QtGui.QPushButton('Save Image', self.main_widget)
        self.buttonSaveImage.clicked.connect(self.saveImageClicked)
        self.buttonLoadDefaulScanRange = QtGui.QPushButton('Large Scan', self.main_widget)
        self.buttonLoadDefaulScanRange.clicked.connect(self.largeScanButtonClicked)
        self.cbarMax = QtGui.QLineEdit(self.main_widget)
        self.cbarMaxL = QtGui.QLabel(self.main_widget)
        self.cbarMaxL.setText("Colorbar Threshold")
        self.buttonCbarThresh = QtGui.QPushButton('Update Colorbar', self.main_widget)
        self.buttonCbarThresh.clicked.connect(self.cbarThreshClicked)
        self.buttonStop = QtGui.QPushButton('Stop Scan', self.main_widget)
        self.buttonStop.clicked.connect(self.stopButtonClicked)
        self.autosaveCheck = QtGui.QCheckBox('AutoSave',self.main_widget)
        self.autosaveCheck.setChecked(True)
        self.buttonAPD = QtGui.QPushButton('Use APD',self.main_widget)
        self.buttonAPD.setCheckable(True)
        self.buttonAPD.setChecked(True)
        self.buttonAPD.clicked.connect(self.buttonAPDClicked)
        self.buttonRedrawLaser = QtGui.QPushButton('Redraw laser spot',self.main_widget)
        self.buttonRedrawLaser.clicked.connect(self.drawDot_RoI)
        self.buttonLoadScanRange = QtGui.QPushButton('Load scan range',self.main_widget)
        self.buttonLoadScanRange.clicked.connect(lambda: self.loadRoI())
        self.buttonZoomInRoI = QtGui.QPushButton('zoom in (RoI)',self.main_widget)
        self.buttonZoomInRoI.clicked.connect(self.zoom_RoI)
        self.buttonZoomOutRoI = QtGui.QPushButton('zoom out', self.main_widget)
        self.buttonZoomOutRoI.clicked.connect(self.imageHomeClicked)
        self.buttonAutofocusRoI = QtGui.QPushButton('auto focus (RoI)',self.main_widget)
        self.buttonAutofocusRoI.clicked.connect(self.autofcus_RoI)

        self.zPosL = QtGui.QLabel(self.main_widget)
        self.zPosL.setText("focus (V)")
        self.zPos = QtGui.QLineEdit(self.main_widget)
        self.zRangeL = QtGui.QLabel(self.main_widget)
        self.zRangeL.setText('range auto focus (V)')
        self.zRange = QtGui.QLineEdit(self.main_widget)
        self.zPtsL = QtGui.QLabel(self.main_widget)
        self.zPtsL.setText('pts auto focus (z)')
        self.zPts = QtGui.QLineEdit(self.main_widget)
        self.xyRange = QtGui.QLineEdit(self.main_widget)
        self.xyRangeL = QtGui.QLabel(self.main_widget)
        self.xyRangeL.setText('pts focus range (xy)')

        self.buttonESRSequence = QtGui.QPushButton("Choose NVs", self.main_widget)
        self.buttonESRFinished = QtGui.QPushButton("FinishedChoosing", self.main_widget)
        self.esrSaveLocL = QtGui.QLabel(self.main_widget)
        self.esrSaveLocL.setText("ESR Save Location")
        self.esrSaveLoc = QtGui.QLineEdit(self.main_widget)
        self.esrSaveLoc.setText('Z:\\Lab\\Cantilever\\Measurements')
        self.esrReadLocL = QtGui.QLabel(self.main_widget)
        self.esrReadLocL.setText("ESR Read Location")
        self.esrReadLoc = QtGui.QLineEdit(self.main_widget)
        self.buttonESRRun = QtGui.QPushButton("Run ESR", self.main_widget)
        self.errSquare = QtGui.QFrame(self.main_widget)
        self.errSquare.setGeometry(150, 20, 100, 100)
        self.errSquare.setStyleSheet("QWidget { background-color: %s }" % 'Green')
        self.errSquareMsg = QtGui.QLineEdit(self.main_widget)


        #set initial values for scan values
        # self.loadRoI('Z://Lab//Cantilever//Measurements//default_settings.config')
        self.loadSettings('Z://Lab//Cantilever//Measurements//default_settings.config')



        plotBox.addWidget(self.imPlot)
        self.scanLayout = QtGui.QGridLayout()


        # Scan area
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
        self.scanLayout.addWidget(self.buttonLoadScanRange,6,14)
        self.scanLayout.addWidget(self.buttonLoadDefaulScanRange,2,8)
        # execute commands
        self.scanLayout.addWidget(self.buttonScan,1,14)
        self.scanLayout.addWidget(self.buttonStop,2,14)


        # laser position
        self.scanLayout.addWidget(self.xVoltageL,1,9)
        self.scanLayout.addWidget(self.xVoltage, 2,9)
        self.scanLayout.addWidget(self.yVoltageL,1,10)
        self.scanLayout.addWidget(self.yVoltage, 2,10)
        self.scanLayout.addWidget(self.buttonRedrawLaser,3,9)
        self.scanLayout.addWidget(self.buttonVSet,3,10)


        # save image
        self.scanLayout.addWidget(self.saveLocImageL,6,1)
        self.scanLayout.addWidget(self.saveLocImage,6,2,1,4)

        self.scanLayout.addWidget(self.saveTagImageL,6,6)
        self.scanLayout.addWidget(self.saveTagImage,6,7)

        self.scanLayout.addWidget(self.buttonSaveImage,6,8)
        self.scanLayout.addWidget(self.autosaveCheck,6,9)



        # set RoI and zoom
        self.scanLayout.addWidget(self.buttonZoomOutRoI,1,11)
        self.scanLayout.addWidget(self.buttonZoomInRoI,2,11)

        # colar bar
        self.scanLayout.addWidget(self.cbarMaxL,3,1)
        self.scanLayout.addWidget(self.cbarMax,3,2)
        self.scanLayout.addWidget(self.buttonCbarThresh,3,3)


        # settings
        self.scanLayout.addWidget(self.buttonAPD,1,16)



        # autofocus settings
        self.scanLayout.addWidget(self.xyRangeL,3,12)
        self.scanLayout.addWidget(self.xyRange,4,12)
        self.scanLayout.addWidget(self.zPosL,3,13)
        self.scanLayout.addWidget(self.zPos,4,13)
        self.scanLayout.addWidget(self.zRangeL,3,14)
        self.scanLayout.addWidget(self.zRange,4,14)
        self.scanLayout.addWidget(self.zPtsL,3,15)
        self.scanLayout.addWidget(self.zPts,4,15)
        self.scanLayout.addWidget(self.buttonAutofocusRoI,3,16)

        self.scanLayout.addWidget(self.buttonESRSequence,5,1)
        self.scanLayout.addWidget(self.buttonESRFinished,5,2)
        self.scanLayout.addWidget(self.esrSaveLocL,5,3)
        self.scanLayout.addWidget(self.esrSaveLoc,5,4)
        self.scanLayout.addWidget(self.buttonESRRun,5,5)
        self.scanLayout.addWidget(self.esrReadLocL,5,6)
        self.scanLayout.addWidget(self.esrReadLoc,5,7)
        self.buttonESRSequence.clicked.connect(self.start_esr_sequence)
        self.buttonESRFinished.clicked.connect(self.finished_choosing)
        self.buttonESRRun.clicked.connect(self.run_esr)
        self.esr_running = False

        vbox.addLayout(self.scanLayout)
        #self.imageData = None
        self.imageData = numpy.array(pd.read_csv("Z:\\Lab\\Cantilever\\Measurements\\150627_ESRTest\\2015-06-27_18-41-56-NVBaselineTests.csv"))
        self.imPlot.axes.imshow(self.imageData, extent = [-.05,.05,-.05,.05])
        self.imPlot.draw()

        self.mouseNVImageConnect = self.imPlot.mpl_connect('button_press_event', self.mouseNVImage)
        rectprops = dict(facecolor = 'black', edgecolor = 'black', alpha = 1.0, fill = True)
        self.RS = RectangleSelector(self.imPlot.axes, self.select_RoI, button = 3, drawtype='box', rectprops = rectprops)


        # add button to execute script
        self.button_exec_script = QtGui.QPushButton('run script', self.main_widget)
        self.button_exec_script.clicked.connect(self.exec_scriptBtnClicked)
        self.scanLayout.addWidget(self.button_exec_script,6,16)

        # add button to execute script
        self.button_save_set = QtGui.QPushButton('save set', self.main_widget)
        self.button_save_set.clicked.connect(lambda: self.save_settings())
        self.scanLayout.addWidget(self.button_save_set,6,15)

        """
        ####### start testing (Jan)

        # colar bar
        row_start = 8
        column_start =  1
        self.label_scan_1a.setText("pt 1a (scan)")
        self.scanLayout.addWidget(self.label_scan_1a,row_start,column_start)
        self.label_scan_1b.setText("pt 1b (scan)")
        self.scanLayout.addWidget(self.label_scan_1b,row_start+1,column_start)
        self.button_scan_2a = QtGui.QPushButton('pt 2a', self.main_widget)
        self.scanLayout.addWidget(self.button_scan_2a,row_start+2,column_start)
        self.button_scan_2b = QtGui.QPushButton('pt 2b', self.main_widget)
        self.scanLayout.addWidget(self.button_scan_2b,row_start+3,column_start)

        self.label_x.setText("x")
        self.scanLayout.addWidget(self.label_x,row_start,column_start+1)
        self.txt_pt_1a.setText("pt 1a (scan)")
        self.scanLayout.addWidget(self.label_scan_1a,row_start,column_start+1)
        self.label_scan_1b.setText("pt 1b (scan)")
        self.scanLayout.addWidget(self.label_scan_1b,row_start+1,column_start+1)
        self.button_scan_2a.setText("pt 2a")
        self.scanLayout.addWidget(self.button_scan_2a,row_start+2,column_start+1)
        self.button_scan_2b.setText("pt 2b")
        self.scanLayout.addWidget(self.button_scan_2a,row_start+3,column_start+1)



        self.txt_pt_1a = QtGui.QLineEdit(self.main_widget)
        self.scanLayout.addWidget(self.txt_pt_1a,row_start,column_start+1)


        self.scanLayout.addWidget(self.cbarMax,3,2)
        self.scanLayout.addWidget(self.buttonCbarThresh,3,3)



        self.cmb_select_2pt_disp = QtGui.QComboBox(self.main_widget)
        self.cmb_select_2pt_disp.addItems(['RoI', 'Grid', 'Line', 'Laser (pt A)', 'None'])
        self.cmb_select_2pt_disp.activated.connect(self.visualize_2pt_disp)
        self.scanLayout.addWidget(self.cmb_select_2pt_disp,8,13)


        ####### end testing (Jan)
        """


        # self.scriptLoc = QtGui.QLineEdit(self.main_widget)
        # self.scriptLoc.setText('Z:\\Lab\\Cantilever\\Measurements')
        # self.scanLayout.addWidget(self.scriptLoc,6,15)
        # self.esrSaveLocL = QtGui.QLabel(self.main_widget)
        # self.scriptLocL.setText("Script:")
        # self.scanLayout.addWidget(self.scriptLocL,6,14)

        self.circ = None # marker for laser
        self.rect = None # marker for RoI

        self.queue = Queue.Queue()

        self.timer = QtCore.QTimer()
        self.timer.start(5000)



        self.timer.timeout.connect(self.checkValidImage)

        self.scanLayout.addWidget(self.errSquare, 7,1)
        self.scanLayout.addWidget(self.errSquareMsg, 7,2,1,4)

        self.laserPos = None
        self.imageRoI = {
            "dx": .8,
            "dy": .8,
            "xPts": 120,
            "xo": 0,
            "yPts": 120,
            "yo": 0
        }
        QtGui.QApplication.processEvents()



    def addZI(self, vbox, plotBox):
        self.ziPlot = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        plotBox.addWidget(self.ziPlot)
        self.ZILayout = QtGui.QGridLayout()
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
        self.ZILayout.addWidget(self.amp,2,1)
        self.ZILayout.addWidget(self.ampL,1,1)
        self.ZILayout.addWidget(self.offset,2,2)
        self.ZILayout.addWidget(self.offsetL,1,2)
        self.ZILayout.addWidget(self.freqLow,2,3)
        self.ZILayout.addWidget(self.freqLowL,1,3)
        self.ZILayout.addWidget(self.freqHigh,2,4)
        self.ZILayout.addWidget(self.freqHighL,1,4)
        self.ZILayout.addWidget(self.sampleNum,2,5)
        self.ZILayout.addWidget(self.sampleNumL,1,5)
        self.ZILayout.addWidget(self.samplePerPt,2,6)
        self.ZILayout.addWidget(self.samplePerPtL,1,6)
        self.ZILayout.addWidget(self.saveLocZI,2,7)
        self.ZILayout.addWidget(self.saveLocZIL,1,7)
        self.ZILayout.addWidget(self.buttonZI,1,8)
        self.ZILayout.addWidget(self.buttonZILog,2,8)
        self.ZILayout.addWidget(self.buttonZISave,1,9)
        self.vbox.addLayout(self.ZILayout)
        self.ZIData = None

    def addCounter(self):
        self.counterPlot = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.buttonStartCounter = QtGui.QPushButton('Start Counter',self.main_widget)
        self.buttonStartCounter.clicked.connect(self.StartCounterBtnClicked)
        self.buttonStopCounter = QtGui.QPushButton('Stop Counter',self.main_widget)
        self.buttonStopCounter.clicked.connect(self.StopCounterBtnClicked)
        self.counterLayout = QtGui.QGridLayout()
        self.counterLayout.addWidget(self.buttonStartCounter,1,1)
        self.counterLayout.addWidget(self.buttonStopCounter,1,2)
        self.vbox.addLayout(self.counterLayout)
        self.plotBox.addWidget(self.counterPlot)
        self.counterQueue = Queue.Queue()

    # Not Yet Implemented
    def addESR(self):
        self.esrPlot = MyMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.rfPower = QtGui.QLineEdit(self.main_widget)
        self.rfPowerL = QtGui.QLabel(self.main_widget)
        self.rfPowerL.setText("Rf Power (dBm):")
        self.freqMin = QtGui.QLineEdit(self.main_widget)
        self.freqMinL = QtGui.QLabel(self.main_widget)
        self.freqMinL.setText("Minimum Frequency (Hz)")
        self.freqMax = QtGui.QLineEdit(self.main_widget)
        self.freqMaxL = QtGui.QLabel(self.main_widget)
        self.freqMaxL.setText("Maximum Frequency (Hz)")
        self.numPtsESR = QtGui.QLineEdit(self.main_widget)
        self.numPtsESRL = QtGui.QLabel(self.main_widget)
        self.numPtsESRL.setText("Num Points")
        self.buttonStartESR = QtGui.QPushButton('Start ESR',self.main_widget)
        self.buttonStartESR.clicked.connect(self.StartESRBtnClicked)
        self.buttonStopESR = QtGui.QPushButton('Stop ESR',self.main_widget)
        self.buttonStopESR.clicked.connect(self.StopESRBtnClicked)

        self.esrLayout = QtGui.QGridLayout()
        self.esrLayout.addWidget(self.rfPower,1,1)
        self.esrLayout.addWidget(self.rfPowerL,1,2)
        self.esrLayout.addWidget(self.freqMin,2,1)
        self.esrLayout.addWidget(self.freqMinL,2,2)
        self.esrLayout.addWidget(self.freqMax,3,1)
        self.esrLayout.addWidget(self.freqMaxL,3,2)
        self.esrLayout.addWidget(self.numPtsESR,4,1)
        self.esrLayout.addWidget(self.numPtsESRL,4,2)
        self.esrLayout.addWidget(self.buttonStartESR,5,1)
        self.esrLayout.addWidget(self.buttonStopCounter,5,2)
        self.vbox.addLayout(self.esrLayout)
        self.plotBox.addWidget(self.esrPlot)
        self.esrQueue = Queue.Queue()


    def visualize_2pt_disp(self):

        case_2pt = self.cmb_select_2pt_disp.currentText()
        # print('asda')
        self.statusBar().showMessage('selected {:s}'.format(case_2pt),1000)

        if case_2pt == 'Grid':
            self.disp_Grid()
        elif case_2pt == 'RoI':
            self.disp_RoI()
        elif case_2pt == 'Line':
            self.disp_Line()



    def exec_scriptBtnClicked(self):
        '''
            run script to repeatedly take images and set laser pointer to predefined location
        '''


        dirpath = self.saveLocImage.text()
        tag = self.saveTagImage.text()
        start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        filepath_set = dirpath + "\\" + start_time + '_' + tag + '.set'

        self.save_settings(filepath_set)


        nr_meas = 20
        i = 0
        while i < nr_meas:
            self.scanBtnClicked()
            self.vSetBtnClicked()
            self.saveImageClicked()


            waittime = 60 # 1 min
            while waittime > 0:
                waittime -= 1
                time.sleep(1)
                self.statusBar().showMessage('scan {:d}/{:d}: time until next scan: {:d}s'.format(i, nr_meas, waittime),1000)
                QtGui.QApplication.processEvents()

            i += 1




    def StartCounterBtnClicked(self):
        apdPlotter = PlotAPDCounts.PlotAPD(self.counterPlot)
        apdPlotter.startPlot(self.counterQueue)

    def StopCounterBtnClicked(self):
        self.counterQueue.put('STOP')

    def StartESRBtnClicked(self):
        DeviceTriggers.runESR(float(self.rfPower.text),float(self.freqMin.text),float(self.freqMax.text),float(self.numPtsESR.text), self.esrQueue)

    def StopESRBtnClicked(self):
        self.esrQueue.put('STOP')


    def buttonAPDClicked(self):
        if self.buttonAPD.isChecked():
            self.buttonAPD.setText('Use APD')
        else:
            self.buttonAPD.setText('Use Photodiode')



    def autofcus_RoI(self):

        zo = float(self.zPos.text())
        dz = float(self.zRange.text())
        zPts = float(self.zPts.text())
        xyPts = float(self.xyRange.text())

        zMin, zMax = zo - dz/2., zo + dz/2.
        roi_focus = self.RoI.copy()
        roi_focus['xPts'] = xyPts
        roi_focus['yPts'] = xyPts
        print roi_focus
        voltage_focus = focusing.Focus.scan(zMin, zMax, zPts, 'Z', waitTime = .1, APD=True, scan_range_roi = roi_focus)

        self.zPos.setText('{:0.4f}'.format(voltage_focus))

    def select_RoI(self,eclick,erelease):


        self.RoI = min_max_to_roi(
            min(eclick.xdata,erelease.xdata),
            max(eclick.xdata, erelease.xdata),
            min(eclick.ydata,erelease.ydata),
            max(eclick.ydata, erelease.ydata)
        )

        self.RoI.update({"xPts": int(self.xPts.text())})
        self.RoI.update({"yPts": int(self.yPts.text())})

        self.draw_RoI()
        # self.xVoltageMin.setText(str(min(eclick.xdata,erelease.xdata)))
        # self.yVoltageMin.setText(str(min(eclick.ydata,erelease.ydata)))
        # self.xVoltageMax.setText(str(max(eclick.xdata, erelease.xdata)))
        # self.yVoltageMax.setText(str(max(eclick.ydata, erelease.ydata)))
        #
        # self.imPlot.axes.set_xlim(left= min(eclick.xdata,erelease.xdata), right = max(eclick.xdata, erelease.xdata))
        # self.imPlot.axes.set_ylim(top= min(eclick.ydata, erelease.ydata),bottom= max(eclick.ydata, erelease.ydata))
        # if(not self.circ==None):
        #     self.drawDot()
        # self.imPlot.draw()

    def zoom_RoI(self):
        self.setRoI(self.RoI)

        xmin, xmax, ymin, ymax = roi_to_min_max(self.RoI)
        self.imPlot.axes.set_xlim(left= xmin, right =xmax)
        self.imPlot.axes.set_ylim(top=ymin,bottom= ymax)
        if(not self.circ==None):
            self.drawDot()
        self.imPlot.draw()

    def ZIBtnClicked(self):
        self.statusBar().showMessage("Taking Frequency Scan",0)
        self.ZIData = DeviceTriggers.ZIGui(self.ziPlot, float(self.amp.text()),float(self.offset.text()), float(self.freqLow.text()),float(self.freqHigh.text()),float(self.sampleNum.text()),float(self.samplePerPt.text()),float(self.buttonZILog.isChecked()))
        self.statusBar().clearMessage()

    def ZISaveClicked(self):
        if(self.ZIData == None):
            QtGui.QMessageBox.about(self.main_widget, "Sweep Save Error", "There is no sweep data to save. Run a sweep first.")
        else:
            self.writeArray(self.ZIData, self.saveLocZI.text(), ['Frequency', 'Response'])
            self.statusBar().showMessage("Sweep Data Saved",2000)

    def saveImageClicked(self):
        if(self.imageData is None):
            QtGui.QMessageBox.about(self.main_widget, "Image Save Error", "There is no image data to save. Run a scan first.")
        else:
            self.writeArray(self.imageData, self.saveLocImage.text(), self.saveTagImage.text())
            self.statusBar().showMessage("Image Data Saved",2000)

    def scanBtnClicked(self):
        self.statusBar().showMessage("Taking Image",0)
        self.imageData, self.imageRoI = DeviceTriggers.scanGui(self.imPlot,float(self.xVoltageMin.text()),float(self.xVoltageMax.text()),float(self.xPts.text()),float(self.yVoltageMin.text()),float(self.yVoltageMax.text()),float(self.yPts.text()),float(self.timePerPt.text()), self.queue, self.buttonAPD.isChecked())
        self.xMinHome = float(self.xVoltageMin.text())
        self.xMaxHome = float(self.xVoltageMax.text())
        self.yMinHome = float(self.yVoltageMin.text())
        self.yMaxHome = float(self.yVoltageMax.text())
        self.statusBar().clearMessage()
        self.circ = None
        self.rect = None
        if(self.autosaveCheck.isChecked() == True):
            self.saveImageClicked()

    def vSetBtnClicked(self):
        DeviceTriggers.setDaqPt(float(self.xVoltage.text()),float(self.yVoltage.text()))
        self.drawDot()
        self.laserPos = (self.xVoltage.text(), self.yVoltage.text())
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
                self.xVoltage.setText('{:0.5f}'.format(event.xdata))
                self.yVoltage.setText('{:0.5f}'.format(event.ydata))
                self.drawDot()
                QtGui.QApplication.processEvents()

    def drawDot(self):
        if(not self.circ==None):
            self.circ.remove()
        xrange = self.imPlot.axes.get_xlim()[1]-self.imPlot.axes.get_xlim()[0]
        yrange = self.imPlot.axes.get_ylim()[1]-self.imPlot.axes.get_ylim()[0]
        size= .01*min(xrange,yrange)

        # if a point had been selected draw it
        # if (xVoltage.text() != '' and yVoltage.text() != ''):
        try:
            self.circ = patches.Circle((self.xVoltage.text(), self.yVoltage.text()), size, fc = 'g')
            self.imPlot.axes.add_patch(self.circ)
            self.imPlot.draw()
        except:
            pass

    def draw_RoI(self):
        if(not self.rect==None):
            self.rect.remove()

        # if RoI exists, draw it
        try:
            self.rect = patches.Rectangle((self.RoI['xo']-self.RoI['dx']/2., self.RoI['yo']-self.RoI['dy']/2.),
                                          width = self.RoI['dx'], height = self.RoI['dy'] , fc = 'none' , ec = 'r')
            self.imPlot.axes.add_patch(self.rect)
            self.imPlot.draw()
        except:
            pass

    def drawDot_RoI(self):
        self.drawDot()
        self.draw_RoI()

    def loadSettings(self, filename = None):

        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'Z://Lab//Cantilever//Measurements//')
        with open(filename, 'r') as infile:
            settings = json.load(infile)

        self.setRoI(settings)
        current_zPos = PC.MDT693A('Z').getVoltage()
        self.xyRange.setText('{:d}'.format(settings['xyRange']))
        self.zPts.setText('{:d}'.format(settings['zPts']))
        self.zPos.setText('{:0.5f}'.format(current_zPos))
        self.zRange.setText('{:0.5f}'.format(settings['dz']))


        self.statusBar().showMessage('loaded {:s}'.format(filename),0)

    def save_settings(self, set_filename = 'Z://Lab//Cantilever//Measurements//default.set'):
        '''
         saves the setting
        '''

        set = {
            "xVoltageMin": str(self.xVoltageMin.text()),
            "xVoltageMax": str(self.xVoltageMax.text()),
            "yVoltageMin": str(self.yVoltageMin.text()),
            "yVoltageMax": str(self.yVoltageMax.text()),
            "xPts": str(self.xPts.text()),
            "yPts": str(self.yPts.text()),
            "timePerPt": str(self.timePerPt.text()),
            "xVoltage": str(self.xVoltage.text()),
            "yVoltage": str(self.yVoltage.text()),
            "saveLocImage": str(self.saveLocImage.text()),
            "saveTagImage": str(self.saveTagImage.text()),
            "cbarMax": str(self.cbarMax.text())
        }

        print set
        with open(set_filename, 'w') as outfile:
            tmp = json.dump(set, outfile, indent=4)

    def loadRoI(self, roi_filename = None):

        if roi_filename is None:
            roi_filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'Z://Lab//Cantilever//Measurements//')
        with open(roi_filename, 'r') as infile:
            roi = json.load(infile)

        self.setRoI(roi)

        self.RoI = roi

        self.statusBar().showMessage('loaded {:s}'.format(roi_filename),0)

    def saveRoI(self, roi, roi_filename):

        with open(roi_filename, 'w') as outfile:
            roi = json.dump(roi, outfile)

    def setRoI(self, roi):
        print roi
        xmin, xmax, ymin, ymax = roi_to_min_max(roi)

        # xmin, xmax = roi['xo'] -  roi['dx']/2.,  roi['xo'] +  roi['dx']/2.
        # ymin, ymax = roi['yo'] -  roi['dy']/2.,  roi['yo'] +  roi['dy']/2.

        self.xVoltageMin.setText('{:0.5f}'.format(xmin))
        self.yVoltageMin.setText('{:0.5f}'.format(ymin))
        self.xVoltageMax.setText('{:0.5f}'.format(xmax))
        self.yVoltageMax.setText('{:0.5f}'.format(ymax))
        self.xPts.setText('{:d}'.format(int(roi['xPts'])))
        self.yPts.setText('{:d}'.format(int(roi['xPts'])))
        self.timePerPt.setText('.001')
        self.RoI = {
            "dx": float(self.xVoltageMax.text())-float(self.xVoltageMin.text()),
            "dy": float(self.yVoltageMax.text())-float(self.yVoltageMin.text()),
            "xPts": float(self.xPts.text()),
            "xo": (float(self.xVoltageMax.text())+float(self.xVoltageMin.text()))/2,
            "yPts": float(self.yPts.text()),
            "yo": (float(self.yVoltageMax.text())+float(self.yVoltageMin.text()))/2
        }

    def start_esr_sequence(self):
        if self.esr_running == True:
            self.imPlot.mpl_disconnect(self.chooseNVsConnect)
        self.esr_running = True
        self.statusBar().showMessage("Choose NVs for ESR", 0)
        self.esr_select_patches = []
        coordinates = track.locate_NVs(self.imageData, self.RoI['dx'], self.RoI['xPts'])
        coordinates[:,[0,1]] = coordinates[:,[1,0]]
        coordinates_v = track.pixel_to_voltage(coordinates, self.imageData,self.RoI)
        print("dx:" + str(self.RoI['dx']))
        print("dy:" + str(self.RoI['dy']))
        for pt in coordinates_v:
            circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'r')
            self.imPlot.axes.add_patch(circ)
        self.imPlot.draw()
        self.imPlot.mpl_disconnect(self.mouseNVImageConnect)
        self.chooseNVsConnect = self.imPlot.mpl_connect('button_press_event', lambda x: self.chooseNVs(x, coordinates_v))
        self.esr_NVs = list()
        self.choosingNVs = True
        while self.choosingNVs:
            QtGui.QApplication.processEvents()
            time.sleep(.05)
        self.imPlot.mpl_disconnect(self.chooseNVsConnect)
        self.mouseNVImageConnect = self.imPlot.mpl_connect('button_press_event', self.mouseNVImage)
        QtGui.QApplication.processEvents()
        nv_num = 1
        for nv_pt in self.esr_NVs:
            self.imPlot.axes.text(nv_pt[0], nv_pt[1], ' ' + str(nv_num), color = 'k')
            nv_num += 1
        df = pd.DataFrame(self.esr_NVs)
        dfimg = pd.DataFrame(self.imageData)
        dirpath = self.esrSaveLoc.text()
        start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        filepath = dirpath + "\\" + start_time
        filepathCSV = filepath + '.csv'
        filepathImg = filepath + 'baselineimg.csv'
        filepathJPG = filepath + '.jpg'
        filepathRoI = filepath + '.roi'
        df.to_csv(filepathCSV, index = False, header=False)
        dfimg.to_csv(filepathImg, index = False, header=False)
        self.imPlot.fig.savefig(str(filepathJPG), format = 'jpg')
        self.saveRoI(self.RoI, filepathRoI)
        self.esrReadLoc.setText(filepath)
        self.statusBar().clearMessage()
        self.esr_running = False

    def chooseNVs(self, event, coordinates):
        if(not(event.xdata == None)):
            if(event.button == 1):
                pt = numpy.array([event.xdata,event.ydata])
                tree = scipy.spatial.KDTree(coordinates)
                _,i = tree.query(pt)
                nv_pt = coordinates[i].tolist()
                if (nv_pt in self.esr_NVs):
                    self.esr_NVs.remove(nv_pt)
                    for circ in self.esr_select_patches:
                        if (nv_pt == numpy.array(circ.center)).all():
                            self.esr_select_patches.remove(circ)
                            circ.remove()
                            break
                else:
                    self.esr_NVs.append(nv_pt)
                    circ = patches.Circle((nv_pt[0], nv_pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'b')
                    self.imPlot.axes.add_patch(circ)
                    self.esr_select_patches.append(circ)
                self.imPlot.draw()


    def finished_choosing(self):
        self.choosingNVs = False
        print(self.esr_NVs)

    def run_esr(self):
        nv_locs = numpy.array(pd.read_csv(str(self.esrReadLoc.text()) + '.csv', header = None))
        print(nv_locs)
        print(len(nv_locs))
        img_baseline = numpy.array(pd.read_csv(str(self.esrReadLoc.text()) + 'baselineimg.csv'))
        self.loadRoI(str(self.esrReadLoc.text()) + '.roi')
        esr_num = 0
        RF_Power = -12
        avg = 100
        while esr_num < len(nv_locs):
            print(esr_num)

            self.statusBar().showMessage("Focusing", 0)
            zo = float(self.zPos.text())
            dz = float(self.zRange.text())
            zPts = float(self.zPts.text())
            xyPts = float(self.xyRange.text())
            zMin, zMax = zo - dz/2., zo + dz/2.
            roi_focus = self.RoI.copy()
            roi_focus['dx'] = .005
            roi_focus['dy'] = .005
            roi_focus['xo'] = nv_locs[0][0]
            roi_focus['yo'] = nv_locs[0][1]
            roi_focus['xPts'] = xyPts
            roi_focus['yPts'] = xyPts
            print roi_focus
            voltage_focus = focusing.Focus.scan(zMin, zMax, zPts, 'Z', waitTime = .1, APD=True, scan_range_roi = roi_focus)
            self.zPos.setText('{:0.4f}'.format(voltage_focus))
            self.statusBar().clearMessage()
            plt.close()


            self.statusBar().showMessage("Scanning and Correcting for Shift", 0)
            xmin, xmax, ymin, ymax = roi_to_min_max(self.RoI)
            img_new, self.imageRoI = DeviceTriggers.scanGui(self.imPlot, xmin, xmax, self.RoI['xPts'], ymin, ymax, self.RoI['xPts'], .001)
            shift = track.corr_NVs(img_baseline, img_new)
            print(shift)
            self.RoI = track.update_roi(self.RoI, shift)
            nv_locs = track.shift_points_v(nv_locs, self.RoI, shift)
            xmin, xmax, ymin, ymax = roi_to_min_max(self.RoI)
            self.imPlot.axes.set_xlim(left= xmin, right =xmax)
            self.imPlot.axes.set_ylim(top=ymin,bottom= ymax)
            img_new, self.imageRoI = DeviceTriggers.scanGui(self.imPlot, xmin, xmax, self.RoI['xPts'], ymin, ymax, self.RoI['xPts'], .001)
            self.statusBar().clearMessage()
            for pt in nv_locs:
                circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'b')
                self.imPlot.axes.add_patch(circ)

            #print(self.RoI)
            #huh = track.locate_NVs(img_new, self.RoI['dx'], self.RoI['xPts'])
            #print(huh)
            #huh[:,[0,1]]= huh[:,[1,0]]
            #print(huh)
            #huh = track.pixel_to_voltage(huh, img_new, self.RoI)
            #print(huh)
            #for pt in huh:
            #    circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'b')
            #    self.imPlot.axes.add_patch(circ)
            #self.imPlot.draw()
            #break

            nv_locs = track.locate_shifted_NVs(img_new, nv_locs, self.RoI)
            for pt in nv_locs:
                circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'r')
                self.imPlot.axes.add_patch(circ)
            self.imPlot.draw()
            pt = nv_locs[esr_num]
            #circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'r')
            #self.imPlot.axes.add_patch(circ)
            #self.imPlot.draw()
            if(pt[0] == 0 and pt[1] == 0): # failed to find matching NV in shifted frame
                esr_num += 1
                continue
            self.statusBar().showMessage("Running ESR", 0)
            test_freqs = numpy.linspace(2820000000, 2920000000, 200)
            esr_data, fit_params, fig = ESR.run_esr(RF_Power, test_freqs, pt, num_avg=avg, int_time=.002)
            dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150712_GuiTest'
            tag = 'NV{:00d}_RFPower_{:03d}mdB_NumAvrg_{:03d}'.format(esr_num, RF_Power, avg)
            ESR.save_esr(esr_data, fig, dirpath, tag)
            esr_num += 1
            self.statusBar().clearMessage()

        self.circ = None
        self.rect = None


    def writeArray(self, array, dirpath, tag, columns = None):
        df = pd.DataFrame(array, columns = columns)
        if(columns == None):
            header = False
        else:
            header = True


        start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        filepathCSV = dirpath + "\\" + start_time + '_' + tag + '.csv'
        filepathJPG = dirpath + "\\" + start_time + '_' + tag + '.jpg'
        # filepathCSV = dirpath + filename + '.csv'
        # filepathJPG = dirpath + filename + '.jpg'
        df.to_csv(filepathCSV, index = False, header=header)
        self.imPlot.fig.savefig(str(filepathJPG), format = 'jpg')

    def cbarThreshClicked(self):
        DeviceTriggers.updateColorbar(self.imageData, self.imPlot, [self.xMinHome, self.xMaxHome, self.yMinHome, self.yMaxHome], float(self.cbarMax.text()))

    def testButtonClicked(self):
        self.addScan(self.vbox, self.plotBox)
        time.sleep(2)
        self.removeScan(self.plotBox)

    def largeScanButtonClicked(self):

        self.loadRoI('Z://Lab//Cantilever//Measurements//default_settings.config')
        # self.xVoltageMin.setText('-.4')
        # self.yVoltageMin.setText('-.4')
        # self.xVoltageMax.setText('.4')
        # self.yVoltageMax.setText('.4')
        # self.xPts.setText('120')
        # self.yPts.setText('120')
        # self.timePerPt.setText('.001')
        # self.statusBar().showMessage("Large Scan Values Set",2000)

    def stopButtonClicked(self):
        self.queue.put('STOP')

    def addPB(self):
        self.buttonStartPB = QtGui.QPushButton('PB Start',self.main_widget)
        self.buttonStartPB.clicked.connect(self.StartPBBtnClicked)
        self.buttonStopPB = QtGui.QPushButton('PB Stop',self.main_widget)
        self.buttonStopPB.clicked.connect(self.StopPBBtnClicked)
        self.PBLayout = QtGui.QGridLayout()
        self.PBLayout.addWidget(self.buttonStartPB,1,1)
        self.PBLayout.addWidget(self.buttonStopPB,1,2)
        self.vbox.addLayout(self.PBLayout)

    def StartPBBtnClicked(self):
        pass

    def StopPBBtnClicked(self):
        pass

    def removeScan(self, plotBox):
        self.clearLayout(self.scanLayout)
        self.imPlot.deleteLater()
        QtGui.QApplication.processEvents()

    def removeZI(self, plotBox):
        self.clearLayout(self.ZILayout)
        self.ziPlot.deleteLater()
        QtGui.QApplication.processEvents()

    def removeCounter(self):
        self.clearLayout(self.counterLayout)
        self.counterPlot.deleteLater()
        QtGui.QApplication.processEvents()

    def removePB(self):
        self.clearLayout(self.PBLayout)
        QtGui.QApplication.processEvents()

    def removeCounter(self):
        self.clearLayout(self.ESRLayout)
        self.ESRPlot.deleteLater()
        QtGui.QApplication.processEvents()

    def clearLayout(self, layout):
        if layout != None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    def initUI(self):
        self.toolbarImage = QtGui.QAction(QtGui.QIcon('C:\\Users\\Experiment\\Desktop\\GuiIcons\\diamondIcon.jpg'), 'addImaging', self)
        self.toolbarImage.setCheckable(True)
        self.toolbarImage.setChecked(False)
        self.toolbarImage.triggered.connect(self.toolbarImageChecked)
        self.toolbarImage.setToolTip('Imaging Tools')
        self.toolbar = self.addToolBar('addImaging')
        self.toolbar.addAction(self.toolbarImage)
        self.toolbarZI = QtGui.QAction(QtGui.QIcon('C:\\Users\\Experiment\\Desktop\\GuiIcons\\ZIIcon.png'), 'addZI', self)
        self.toolbarZI.setCheckable(True)
        self.toolbarZI.setChecked(False)
        self.toolbarZI.triggered.connect(self.toolbarZIChecked)
        self.toolbarZI.setToolTip('ZI Tools')
        self.toolbar.addAction(self.toolbarZI)
        self.toolbarCounter = QtGui.QAction(QtGui.QIcon('C:\\Users\\Experiment\\Desktop\\GuiIcons\\CountIcon.jpg'), 'addCounter', self)
        self.toolbarCounter.setCheckable(True)
        self.toolbarCounter.setChecked(False)
        self.toolbarCounter.triggered.connect(self.toolbarCounterChecked)
        self.toolbarCounter.setToolTip('Counter Tool')
        self.toolbar.addAction(self.toolbarCounter)
        self.toolbarPB = QtGui.QAction(QtGui.QIcon('C:\\Users\\Experiment\\Desktop\\GuiIcons\\LaserIcon.jpg'), 'addPB', self)
        self.toolbarPB.setCheckable(True)
        self.toolbarPB.setChecked(False)
        self.toolbarPB.triggered.connect(self.toolbarPBChecked)
        self.toolbarPB.setToolTip('PulseBlaster Tool')
        self.toolbar.addAction(self.toolbarPB)
        self.toolbarESR = QtGui.QAction(QtGui.QIcon('C:\\Users\\Experiment\\Desktop\\GuiIcons\\LaserIcon.jpg'), 'addPB', self)
        self.toolbarESR.setCheckable(True)
        self.toolbarESR.setChecked(False)
        self.toolbarESR.triggered.connect(self.toolbarESRChecked)
        self.toolbarESR.setToolTip('ESR Tool')
        #self.toolbar.addAction(self.toolbarESR)
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)
        self.toolbarLock = QtGui.QAction(QtGui.QIcon('C:\\Users\\Experiment\\Desktop\\GuiIcons\\LockIcon.png'), 'lockToolbar', self)
        self.toolbarLock.setCheckable(True)
        self.toolbarLock.setChecked(False)
        self.toolbarLock.triggered.connect(self.toolbarLockChecked)
        self.toolbarLock.setToolTip('Lock Toolbar')
        self.toolbar.addAction(self.toolbarLock)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Toolbar')
        self.show()

    def toolbarImageChecked(self):
        if(not self.toolbarLock.isChecked()):
            if(self.toolbarImage.isChecked()):
                self.addScan(self.vbox, self.plotBox)
            else:
                self.removeScan(self.plotBox)

    def toolbarZIChecked(self):
        if(not self.toolbarLock.isChecked()):
            if(self.toolbarZI.isChecked()):
                self.addZI(self.vbox, self.plotBox)
            else:
                self.removeZI(self.plotBox)

    def toolbarCounterChecked(self):
        if(not self.toolbarLock.isChecked()):
            if(self.toolbarCounter.isChecked()):
                self.addCounter()
            else:
                self.removeCounter()

    def toolbarPBChecked(self):
        if(not self.toolbarLock.isChecked()):
            if(self.toolbarPB.isChecked()):
                self.addPB()
            else:
                self.removePB()

    def toolbarESRChecked(self):
        if(not self.toolbarLock.isChecked()):
            if(self.toolbarESR.isChecked()):
                self.addESR()
            else:
                self.removeESR()

    def toolbarLockChecked(self):
        if(self.toolbarLock.isChecked()):
            self.toolbarImage.setDisabled(True)
            self.toolbarZI.setDisabled(True)
            self.toolbarCounter.setDisabled(True)
            self.toolbarPB.setDisabled(True)
            self.statusBar().showMessage("Toolbar Locked",2000)
        else:
            self.toolbarImage.setDisabled(False)
            self.toolbarZI.setDisabled(False)
            self.toolbarCounter.setDisabled(False)
            self.toolbarPB.setDisabled(False)
            self.statusBar().showMessage("Toolbar Unlocked",2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def checkValidImage(self):
        boxRoI = {
            "dx": float(self.xVoltageMax.text())-float(self.xVoltageMin.text()),
            "dy": float(self.yVoltageMax.text())-float(self.yVoltageMin.text()),
            "xPts": float(self.xPts.text()),
            "xo": (float(self.xVoltageMax.text())+float(self.xVoltageMin.text()))/2,
            "yPts": float(self.yPts.text()),
            "yo": (float(self.yVoltageMax.text())+float(self.yVoltageMin.text()))/2
        }
        if not (not (self.imageRoI == None) and self.imageRoI['dx'] == self.RoI['dx'] and self.imageRoI['dy'] == self.RoI['dy'] and self.imageRoI['xo'] == self.RoI['xo']  and self.imageRoI['yo'] == self.RoI['yo'] and self.imageRoI['xPts'] == self.RoI['xPts'] and self.imageRoI['yPts'] == self.RoI['yPts']):
            self.errSquare.setStyleSheet("QFrame { background-color: %s }" % 'Red')
            self.errSquareMsg.setText('Image RoI mismatched from internal RoI')
        elif not (self.imageRoI == boxRoI):
            self.errSquare.setStyleSheet("QFrame { background-color: %s }" % 'Red')
            self.errSquareMsg.setText('Image RoI mismatched from text RoI')
        elif not(self.laserPos == (self.xVoltage.text(), self.yVoltage.text())):
            self.errSquare.setStyleSheet("QFrame { background-color: %s }" % 'Red')
            self.errSquareMsg.setText('Laser Position mismatched from image')
        else:
            self.errSquare.setStyleSheet("QFrame { background-color: %s }" % 'Green')
            self.errSquareMsg.setText('')


    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""Temp"""
)
qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
progname = 'Experiment Gui'
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()