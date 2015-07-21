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

import numpy
import numpy.random
import pandas as pd


import matplotlib.patches as patches

from PyQt4 import QtGui, QtCore

import scipy.spatial
import matplotlib.pyplot as plt

import json
import functions.Focusing as focusing
from functions.regions import *
from functions import track_NVs as track
from hardware_modules import PiezoController as PC
from scripts import ESR

from gui import GuiDeviceTriggers as DeviceTriggers


import gui_scan_layout, gui_counter_layout, gui_esr_layout, gui_zi_layout


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


# THIS SHOULD BE MOVED TO THE RESPECTIVE GUI_xx_LAYOUT.PY FILES ####################################################

    # def visualize_2pt_disp(self):
    #
    #     case_2pt = self.cmb_select_2pt_disp.currentText()
    #     # print('asda')
    #     self.statusBar().showMessage('selected {:s}'.format(case_2pt),1000)
    #
    #     if case_2pt == 'Grid':
    #         self.disp_Grid()
    #     elif case_2pt == 'RoI':
    #         self.disp_RoI()
    #     elif case_2pt == 'Line':
    #         self.disp_Line()
    #
    #




    def StartCounterBtnClicked(self):
        apdPlotter = PlotAPDCounts.PlotAPD(self.counterPlot)
        apdPlotter.startPlot(self.counterQueue)

    def StopCounterBtnClicked(self):
        self.counterQueue.put('STOP')

    def StartESRBtnClicked(self):
        DeviceTriggers.runESR(float(self.rfPower.text),float(self.freqMin.text),float(self.freqMax.text),float(self.numPtsESR.text), self.esrQueue)

    def StopESRBtnClicked(self):
        self.esrQueue.put('STOP')





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

    # def mouseNVImage(self,event):
    #     if(not(event.xdata == None)):
    #         if(event.button == 1):
    #             self.xVoltage.setText('{:0.5f}'.format(event.xdata))
    #             self.yVoltage.setText('{:0.5f}'.format(event.ydata))
    #             self.drawDot()
    #             QtGui.QApplication.processEvents()

    # def drawDot(self):
    #     if(not self.circ==None):
    #         self.circ.remove()
    #     xrange = self.imPlot.axes.get_xlim()[1]-self.imPlot.axes.get_xlim()[0]
    #     yrange = self.imPlot.axes.get_ylim()[1]-self.imPlot.axes.get_ylim()[0]
    #     size= .01*min(xrange,yrange)
    #
    #     # if a point had been selected draw it
    #     # if (xVoltage.text() != '' and yVoltage.text() != ''):
    #     try:
    #         self.circ = patches.Circle((self.xVoltage.text(), self.yVoltage.text()), size, fc = 'g')
    #         self.imPlot.axes.add_patch(self.circ)
    #         self.imPlot.draw()
    #     except:
    #         pass
    #
    # def draw_RoI(self):
    #     if(not self.rect==None):
    #         self.rect.remove()
    #
    #     # if RoI exists, draw it
    #     try:
    #         self.rect = patches.Rectangle((self.RoI['xo']-self.RoI['dx']/2., self.RoI['yo']-self.RoI['dy']/2.),
    #                                       width = self.RoI['dx'], height = self.RoI['dy'] , fc = 'none' , ec = 'r')
    #         self.imPlot.axes.add_patch(self.rect)
    #         self.imPlot.draw()
    #     except:
    #         pass
    #
    # def drawDot_RoI(self):
    #     self.drawDot()
    #     self.draw_RoI()
    #
    # def loadRoI(self, roi_filename = None):
    #
    #     if roi_filename is None:
    #         roi_filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'Z://Lab//Cantilever//Measurements//')
    #     with open(roi_filename, 'r') as infile:
    #         roi = json.load(infile)
    #
    #     self.setRoI(roi)
    #
    #     self.RoI = roi
    #
    #     self.statusBar().showMessage('loaded {:s}'.format(roi_filename),0)
    #
    # def saveRoI(self, roi, roi_filename):
    #
    #     with open(roi_filename, 'w') as outfile:
    #         roi = json.dump(roi, outfile)
    #
    # def setRoI(self, roi):
    #     print roi
    #     xmin, xmax, ymin, ymax = roi_to_min_max(roi)
    #
    #     # xmin, xmax = roi['xo'] -  roi['dx']/2.,  roi['xo'] +  roi['dx']/2.
    #     # ymin, ymax = roi['yo'] -  roi['dy']/2.,  roi['yo'] +  roi['dy']/2.
    #
    #     self.xVoltageMin.setText('{:0.5f}'.format(xmin))
    #     self.yVoltageMin.setText('{:0.5f}'.format(ymin))
    #     self.xVoltageMax.setText('{:0.5f}'.format(xmax))
    #     self.yVoltageMax.setText('{:0.5f}'.format(ymax))
    #     self.xPts.setText('{:d}'.format(int(roi['xPts'])))
    #     self.yPts.setText('{:d}'.format(int(roi['xPts'])))
    #     self.timePerPt.setText('.001')
    #     self.RoI = {
    #         "dx": float(self.xVoltageMax.text())-float(self.xVoltageMin.text()),
    #         "dy": float(self.yVoltageMax.text())-float(self.yVoltageMin.text()),
    #         "xPts": float(self.xPts.text()),
    #         "xo": (float(self.xVoltageMax.text())+float(self.xVoltageMin.text()))/2,
    #         "yPts": float(self.yPts.text()),
    #         "yo": (float(self.yVoltageMax.text())+float(self.yVoltageMin.text()))/2
    #     }

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

    # def chooseNVs(self, event, coordinates):
    #     if(not(event.xdata == None)):
    #         if(event.button == 1):
    #             pt = numpy.array([event.xdata,event.ydata])
    #             tree = scipy.spatial.KDTree(coordinates)
    #             _,i = tree.query(pt)
    #             nv_pt = coordinates[i].tolist()
    #             if (nv_pt in self.esr_NVs):
    #                 self.esr_NVs.remove(nv_pt)
    #                 for circ in self.esr_select_patches:
    #                     if (nv_pt == numpy.array(circ.center)).all():
    #                         self.esr_select_patches.remove(circ)
    #                         circ.remove()
    #                         break
    #             else:
    #                 self.esr_NVs.append(nv_pt)
    #                 circ = patches.Circle((nv_pt[0], nv_pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'b')
    #                 self.imPlot.axes.add_patch(circ)
    #                 self.esr_select_patches.append(circ)
    #             self.imPlot.draw()


    # def finished_choosing(self):
    #     self.choosingNVs = False
    #     print(self.esr_NVs)

    # def run_esr(self):
    #     nv_locs = numpy.array(pd.read_csv(str(self.esrReadLoc.text()) + '.csv', header = None))
    #     print(nv_locs)
    #     print(len(nv_locs))
    #     img_baseline = numpy.array(pd.read_csv(str(self.esrReadLoc.text()) + 'baselineimg.csv'))
    #     self.loadRoI(str(self.esrReadLoc.text()) + '.roi')
    #     esr_num = 0
    #     RF_Power = -12
    #     avg = 100
    #     while esr_num < len(nv_locs):
    #         print(esr_num)
    #
    #         self.statusBar().showMessage("Focusing", 0)
    #         zo = float(self.zPos.text())
    #         dz = float(self.zRange.text())
    #         zPts = float(self.zPts.text())
    #         xyPts = float(self.xyRange.text())
    #         zMin, zMax = zo - dz/2., zo + dz/2.
    #         roi_focus = self.RoI.copy()
    #         roi_focus['dx'] = .005
    #         roi_focus['dy'] = .005
    #         roi_focus['xo'] = nv_locs[0][0]
    #         roi_focus['yo'] = nv_locs[0][1]
    #         roi_focus['xPts'] = xyPts
    #         roi_focus['yPts'] = xyPts
    #         print roi_focus
    #         voltage_focus = focusing.Focus.scan(zMin, zMax, zPts, 'Z', waitTime = .1, APD=True, scan_range_roi = roi_focus)
    #         self.zPos.setText('{:0.4f}'.format(voltage_focus))
    #         self.statusBar().clearMessage()
    #         plt.close()
    #
    #
    #         self.statusBar().showMessage("Scanning and Correcting for Shift", 0)
    #         xmin, xmax, ymin, ymax = roi_to_min_max(self.RoI)
    #         img_new, self.imageRoI = DeviceTriggers.scanGui(self.imPlot, xmin, xmax, self.RoI['xPts'], ymin, ymax, self.RoI['xPts'], .001)
    #         shift = track.corr_NVs(img_baseline, img_new)
    #         print(shift)
    #         self.RoI = track.update_roi(self.RoI, shift)
    #         nv_locs = track.shift_points_v(nv_locs, self.RoI, shift)
    #         xmin, xmax, ymin, ymax = roi_to_min_max(self.RoI)
    #         self.imPlot.axes.set_xlim(left= xmin, right =xmax)
    #         self.imPlot.axes.set_ylim(top=ymin,bottom= ymax)
    #         img_new, self.imageRoI = DeviceTriggers.scanGui(self.imPlot, xmin, xmax, self.RoI['xPts'], ymin, ymax, self.RoI['xPts'], .001)
    #         self.statusBar().clearMessage()
    #         for pt in nv_locs:
    #             circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'b')
    #             self.imPlot.axes.add_patch(circ)
    #
    #         #print(self.RoI)
    #         #huh = track.locate_NVs(img_new, self.RoI['dx'], self.RoI['xPts'])
    #         #print(huh)
    #         #huh[:,[0,1]]= huh[:,[1,0]]
    #         #print(huh)
    #         #huh = track.pixel_to_voltage(huh, img_new, self.RoI)
    #         #print(huh)
    #         #for pt in huh:
    #         #    circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'b')
    #         #    self.imPlot.axes.add_patch(circ)
    #         #self.imPlot.draw()
    #         #break
    #
    #         nv_locs = track.locate_shifted_NVs(img_new, nv_locs, self.RoI)
    #         for pt in nv_locs:
    #             circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'r')
    #             self.imPlot.axes.add_patch(circ)
    #         self.imPlot.draw()
    #         pt = nv_locs[esr_num]
    #         #circ = patches.Circle((pt[0], pt[1]), .01*min(self.RoI['dx'],self.RoI['dy']), fc = 'r')
    #         #self.imPlot.axes.add_patch(circ)
    #         #self.imPlot.draw()
    #         if(pt[0] == 0 and pt[1] == 0): # failed to find matching NV in shifted frame
    #             esr_num += 1
    #             continue
    #         self.statusBar().showMessage("Running ESR", 0)
    #         test_freqs = numpy.linspace(2820000000, 2920000000, 200)
    #         esr_data, fit_params, fig = ESR.run_esr(RF_Power, test_freqs, pt, num_avg=avg, int_time=.002)
    #         dirpath = 'Z:\\Lab\\Cantilever\\Measurements\\20150712_GuiTest'
    #         tag = 'NV{:00d}_RFPower_{:03d}mdB_NumAvrg_{:03d}'.format(esr_num, RF_Power, avg)
    #         ESR.save_esr(esr_data, fig, dirpath, tag)
    #         esr_num += 1
    #         self.statusBar().clearMessage()
    #
    #     self.circ = None
    #     self.rect = None


    # def writeArray(self, array, dirpath, tag, columns = None):
    #     df = pd.DataFrame(array, columns = columns)
    #     if(columns == None):
    #         header = False
    #     else:
    #         header = True
    #
    #
    #     start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    #     filepathCSV = dirpath + "\\" + start_time + '_' + tag + '.csv'
    #     filepathJPG = dirpath + "\\" + start_time + '_' + tag + '.jpg'
    #     # filepathCSV = dirpath + filename + '.csv'
    #     # filepathJPG = dirpath + filename + '.jpg'
    #     df.to_csv(filepathCSV, index = False, header=header)
    #     self.imPlot.fig.savefig(str(filepathJPG), format = 'jpg')

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
        self.clearLayout(self.scanCoorGrid)
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
        self.toolbarImage.setChecked(True)
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
        self.toolbarImageChecked()
        self.show()

    def toolbarImageChecked(self):
        if(not self.toolbarLock.isChecked()):
            if(self.toolbarImage.isChecked()):
                gui_scan_layout.add_scan_layout(self, self.vbox, self.plotBox)
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

{
    "pt_1a_x": "0.0496",
    "pt_1b_x": "0.0496",
    "pt_1a_y": "-0.0658",
    "pt_1b_y": "0.0630",
    "pt_1_x": "20",
    "pt_1_y": "20"
}