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
import test
from matplotlib.backends import qt_compat
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
        self.axes = fig.add_subplot(111)
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
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

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
        self.sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        vbox.addWidget(self.sc)
        vbox.addWidget(self.dc)
        self.buttonZI = QtGui.QPushButton('ZI',self.main_widget)
        self.buttonZI.clicked.connect(self.ZIBtnClicked)

        self.text = QtGui.QLineEdit(self.main_widget)
        self.text2 = QtGui.QLineEdit(self.main_widget)
        grid = QtGui.QGridLayout()
        grid.addWidget(self.buttonZI, 2,1)
        grid.addWidget(self.text, 1,1)
        grid.addWidget(self.text2, 1,2)
        vbox.addLayout(grid)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.textUpdate)
        timer.start(500)

    def ZIBtnClicked(self):
        #DeviceTriggers.ZIGui(self.sc.axes)
        test.plotTest(self.sc)

    def textUpdate(self):
        a = numpy.random.ranf()
        b = numpy.random.ranf()
        self.text.setText(str(a))
        self.text2.setText(str(b))


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

#class DeviceTriggers():
#    def ZIGui(self, axes):
#        test.plotTest(axes)



qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()