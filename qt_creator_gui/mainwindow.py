# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Tue Feb 02 17:19:07 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(563, 436)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.buttonRecordData = QtGui.QPushButton(self.centralwidget)
        self.buttonRecordData.setGeometry(QtCore.QRect(230, 220, 169, 23))
        self.buttonRecordData.setObjectName("buttonRecordData")
        self.checkPIActive = QtGui.QCheckBox(self.centralwidget)
        self.checkPIActive.setGeometry(QtCore.QRect(10, 30, 101, 17))
        self.checkPIActive.setObjectName("checkPIActive")
        self.checkIRon = QtGui.QCheckBox(self.centralwidget)
        self.checkIRon.setGeometry(QtCore.QRect(10, 60, 70, 17))
        self.checkIRon.setObjectName("checkIRon")
        self.plotWidget = QtGui.QWidget(self.centralwidget)
        self.plotWidget.setGeometry(QtCore.QRect(149, 30, 291, 171))
        self.plotWidget.setObjectName("plotWidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 563, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRecordData.setText(QtGui.QApplication.translate("MainWindow", "Record Data", None, QtGui.QApplication.UnicodeUTF8))
        self.checkPIActive.setText(QtGui.QApplication.translate("MainWindow", "PI - loop active", None, QtGui.QApplication.UnicodeUTF8))
        self.checkIRon.setText(QtGui.QApplication.translate("MainWindow", "IR on", None, QtGui.QApplication.UnicodeUTF8))

