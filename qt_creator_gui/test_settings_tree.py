"""
Created on Feb 2 2016

@author: Jan Gieseler

# is a test to implement an editable settings tree
"""

# from qt_creator_gui.mainwindow import Ui_MainWindow
import sys
# todo: resolve issue with namespace (get rid of from PySide.QtCore import * and from PySide.QtGui import *)
from PySide import QtCore, QtGui
from PySide.QtCore import *
from PySide.QtGui import *


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from PyQt4.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui') # with this we don't have to convert the .ui file into a python file!
# from qt_creator_gui.mainwindow import Ui_MainWindow # with this we have to first compile (pyside-uic mainwindow.ui -o mainwindow.py)



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






class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self._settings = settings_dict


        self._settings = settings_dict

        # add new item to tree
        # self.treeWidget.topLevelItem(0).child(0).setText(0,"New Subitem X")
        # child = QTreeWidgetItem()
        # child.setText(0, "XXX")
        # print(self.treeWidget.invisibleRootItem().isEditable())
        print(self.treeWidget.currentItem())
        # self.treeWidget.clear()
        x=QtGui.QTreeWidgetItem()
        x.setText(0,"asda")

        parent = QtGui.QTreeWidgetItem(self.treeWidget)
        parent.setText(0, "parent")
        item = QtGui.QTreeWidgetItem(parent)
        item.setText(0, 'ada')

        # self.fill_widget(self.treeWidget,  settings_dict)


        # todo: find out why flags can not be set, usually the flags would allow to make items editable
        # item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)



        # define variables and datasets
        parameters_Acq = self._settings["parameters_Acq"]
        self.number_of_reads = int(np.ceil(1.0 * parameters_Acq['data_length'] / parameters_Acq['block_size']))
        self.block_size = parameters_Acq['block_size']
        self.elements_left = np.ones(self.number_of_reads)
        self.data_AI1 = np.ones((self.number_of_reads, self.block_size))


        self.create_figures()


    def create_figures(self):
        # fill the empty widgets with a figure
        fig_live = Figure()
        self.canvas_live = FigureCanvas(fig_live)
        self.plot_data_live.addWidget(self.canvas_live)
        self.axes_live = fig_live.add_subplot(111)

        fig_timetrace = Figure()
        self.canvas_timetrace = FigureCanvas(fig_timetrace)
        self.plot_data_timetrace.addWidget(self.canvas_timetrace)
        self.axes_timetrace = fig_timetrace.add_subplot(111)
        self.axes_timetrace.set_xlabel('time (ms)')

        fig_psd = Figure()
        self.canvas_psd = FigureCanvas(fig_psd)
        self.plot_data_psd.addWidget(self.canvas_psd)
        self.axes_psd = fig_psd.add_subplot(111)
        self.axes_psd.set_xlabel('frequency (Hz)')


    def fill_widget(self, tree,  value):

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

        tree.clear()
        fill_item(tree.invisibleRootItem(), value)

    def __del__(self):
        '''
        Cleans up connections
        '''
        # self._thread_acq.stop()
        #
        # self.fpga.stop()


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

    import numpy as np

    # fig1 = Figure()
    # ax1f1 = fig1.add_subplot(111)
    # ax1f1.plot(np.random.rand(5))

    app = QtGui.QApplication(sys.argv)
    main = ControlMainWindow()
    # main.addmpl(fig1)
    main.show()
    sys.exit(app.exec_())
