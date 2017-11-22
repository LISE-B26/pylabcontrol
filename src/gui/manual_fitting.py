from PyQt4 import QtGui, QtCore
from PyQt4.uic import loadUiType
from PyLabControl.src.core import Parameter, Instrument, Script, ReadProbes, Probe, ScriptIterator
from PyLabControl.src.gui import B26QTreeItem, LoadDialog, LoadDialogProbes
from PyLabControl.src.scripts.select_points import SelectPoints
from PyLabControl.src.core.read_write_functions import load_b26_file

import os.path
import numpy as np
import json as json
from PyQt4.QtCore import QThread, pyqtSlot, pyqtSignal, QObject

from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as Canvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from qt_b26_gui import MatplotlibWidget
import sys
import glob
import matplotlib.pyplot as plt
import time

Ui_MainWindow, QMainWindow = loadUiType('manual_fitting_window.ui') # with this we don't have to convert the .ui file into a python file!

class FittingWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        def create_figures():
            self.matplotlibwidget = MatplotlibWidget(self.plot)
            sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.matplotlibwidget.sizePolicy().hasHeightForWidth())
            self.matplotlibwidget.setSizePolicy(sizePolicy)
            self.matplotlibwidget.setMinimumSize(QtCore.QSize(200, 200))
            self.matplotlibwidget.setObjectName(QtCore.QString.fromUtf8("matplotlibwidget"))
            self.horizontalLayout_3.addWidget(self.matplotlibwidget)

        def setup_connections():
            self.btn_fit.clicked.connect(self.btn_clicked)
            self.btn_clear.clicked.connect(self.btn_clicked)
            self.btn_next.clicked.connect(self.btn_clicked)
            self.matplotlibwidget.mpl_connect('button_press_event', self.plot_clicked)
            self.btn_open.clicked.connect(self.open_file_dialog)
            self.btn_run.clicked.connect(self.btn_clicked)

        create_figures()
        setup_connections()

    def btn_clicked(self):
        sender = self.sender()
        if sender is self.btn_run:
            self.start_fitting()

    def plot_clicked(self, mouse_event):
        print('clicked')

    class do_fit(QObject):
        finished = pyqtSignal()  # signals the end of the script

        def __init__(self, filepath, plotwidget):
            QObject.__init__(self)
            self.filepath = filepath
            self.plotwidget = plotwidget

        def run(self):
            esr_folders = glob.glob(os.path.join(self.filepath, './data_subscripts/*esr*'))

            data_array = []
            for esr_folder in esr_folders[:-1]:
                data = Script.load_data(esr_folder)
                data_array.append(data)

            for data in data_array:
                self.plotwidget.axes.plot(data['frequency'], data['data'])
                self.plotwidget.draw()

            self.finished.emit()


    def start_fitting(self):
        print(QThread.currentThread())
        self.fit_thread = QThread() #must be assigned as an instance variable, not local, as otherwise thread is garbage
                                    #collected immediately at the end of the function before it runs
        self.fitobj = self.do_fit(str(self.data_filepath.text()), self.matplotlibwidget)
        self.fitobj.moveToThread(self.fit_thread)
        self.fit_thread.started.connect(self.fitobj.run)
        self.fitobj.finished.connect(self.fit_thread.quit)  # clean up. quit thread after script is finished
        print('starting?')
        self.fit_thread.start()
        print(QThread.currentThread())

    def open_file_dialog(self):
        """
        opens a file dialog to get the path to a file and
        """
        dialog = QtGui.QFileDialog
        filename = dialog.getExistingDirectory(self, 'Select a file:', self.data_filepath.text())
        if str(filename)!='':
            self.data_filepath.setText(filename)


app = QtGui.QApplication(sys.argv)
ex = FittingWindow()
ex.show()
ex.raise_()
sys.exit(app.exec_())
