"""
Created on Feb 2 2016

@author: Jan Gieseler

# this file creates the gui
# gui is designed with QT Designer that creates a .ui file (e.g. mainwindow.ui)
# To get the resulting .py file use the batch (pyside-uic.bat) file that contains C:\Anaconda\python.exe C:\Anaconda\Lib\site-packages\PySide\scripts\uic.py %*
# This converts the .ui file into .py file (e.g. mainwindow.py) by executing pyside-uic mainwindow.ui -o mainwindow.py
"""


import sys
from PySide import QtCore, QtGui
import hardware_modules.maestro as maestro

import hardware_modules.DCServo_Kinesis_dll as DCServo_Kinesis
# import to plot stuff
# import matplotlib
# matplotlib.use('Qt4Agg')
# matplotlib.rcParams['backend.qt4']='PySide'
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from PyQt4.uic import loadUiType

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from qt_creator_gui.mainwindow import Ui_MainWindow
# Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui') # with this we don't have to convert the .ui file into a python file!
#

from collections import deque


# ============= GENERAL SETTING ====================================
# ==================================================================

settings_dict = {
    "serial_port_maestro" : "COM5",
    "channel_beam_block_IR" : 4,
    "channel_beam_block_Green" : 5,
    "parameters_filterwheel" : {
        "channel" : 1,
        "position_list" : {'ND1.0': 4*600, 'LP':4*1550, 'ND2.0':4*2500}
    },
    "record_length" : 100,
    "parameters_PI" : {
        "sample_period_PI" :4e5,
        "gains" : {'proportional': 1.0, 'integral':0.1},
        "setpoint" : 0,
        "piezo" : 0
    },
    "parameters_Acq" : {
        "sample_period_acq" : 100,
        "data_length" : 2000,
        "block_size" : 100
    },
    "kinesis_serial_number" : 83832028,
    "detector_threshold" : 50


}



from PySide.QtCore import *
from PySide.QtGui import *

# class ControlMainWindow(QMainWindow, Ui_MainWindow):
#     def __init__(self, ):
#         super(ControlMainWindow, self).__init__()
#         self.setupUi(self)


class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self._settings = settings_dict
        tree = SettingsTree()
        self.settings.addWidget(tree)


class SettingsTree(QtGui.QTreeWidget):

    def __init__(self, parent = None):
        super(SettingsTree, self).__init__(parent)
        self.setColumnCount(1)
        self.setHeaderLabel("Settings")
        self.settings = settings_dict
        self.style()
        self.fill_widget(self.settings)

    def fill_widget(self, value):

        def fill_item(item, value):
            item.setExpanded(True)
            if type(value) is dict:
                for key, val in sorted(value.iteritems()):
                    child = QTreeWidgetItem()
                    child.setText(0, unicode(key))
                    item.addChild(child)
                    fill_item(child, val)
            elif type(value) is list:
                for val in value:
                    child = QTreeWidgetItem()
                    item.addChild(child)
                if type(val) is dict:
                    child.setText(0, '[dict]')
                    fill_item(child, val)
                elif type(val) is list:
                    child.setText(0, '[list]')
                    fill_item(child, val)
                else:
                    child.setText(0, unicode(val))
                child.setExpanded(True)

                child.setFlags(Qt.ItemIsSelectable |Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)

            else:
                child = QTreeWidgetItem()
                child.setText(0, unicode(value))
                item.addChild(child)
                child.setFlags(Qt.ItemIsSelectable |Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)

        self.clear()
        fill_item(self.invisibleRootItem(), value)

if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui

    app = QtGui.QApplication(sys.argv)
    main = ControlMainWindow()

    main.show()
    sys.exit(app.exec_())
