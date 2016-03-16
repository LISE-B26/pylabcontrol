#!/usr/bin/env python

# Core of gui based on example:
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
sys.path.append('.')

from PyQt4 import QtGui, QtCore

from src.gui import gui_scan_layout


# Class corresponding to window in which all widgets (objects used to display things) are placed. Extends QtGui.QMainWindow
class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        '''
        Initializes the gui window
        '''
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        self.setMinimumSize(1500,800)

        #adds a bar menu with a file-quit and help-about at the top, can be expanded later if wished
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        # defines a main widget to put all of the plots, buttons, etc into
        self.main_widget = QtGui.QWidget(self)

        # creates a vertical box for widgets at the highest layer, creates a horizontal box intended for matplotlib
        # plots for the next layer, and put the horizontal box in the first (top) location in the vertical box
        self.vbox = QtGui.QVBoxLayout(self.main_widget)
        self.plotBox = QtGui.QHBoxLayout()
        self.vbox.addLayout(self.plotBox)

        # changes windows focus to the gui on launch
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        # our function to add all additional functionality to the layout
        gui_scan_layout.add_scan_layout(self, self.vbox, self.plotBox)

        #Makes room for status bar at bottom so it doesn't resize the widgets when it is used later
        self.statusBar().showMessage("Temp",1)

        # resizes to size hint
        self.adjustSize()

        # tells window what initial size to use
        def sizeHint(self):
            return QtCore.QSize(5000, 5000)

    # closes on pressing file-quit
    def fileQuit(self):
        self.close()

    # Automatically triggered on window close by any non-error means, including x-ing out. Saves settings to the default
    # location, to be read out on next open
    def closeEvent(self, event):
        gui_scan_layout.save_settings(self, 'Z://Lab//Cantilever//Measurements//default.set')

    # message to display on help-about
    def about(self):
        QtGui.QMessageBox.about(self, "About", """Temp""")

# Core application loop which starts and runs the GUI
qApp = QtGui.QApplication(sys.argv)
aw = ApplicationWindow()
progname = 'Experiment Gui'
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()