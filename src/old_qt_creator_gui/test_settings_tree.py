"""
Created on Feb 2 2016

@author: Jan Gieseler

# this file creates the gui
# gui is designed with QT Designer that creates a .ui file (e.g. mainwindow.ui)
# To get the resulting .py file use the batch (pyside-uic.bat) file that contains C:\Anaconda\python.exe C:\Anaconda\Lib\site-packages\PySide\scripts\uic.py %*
# This converts the .ui file into .py file (e.g. mainwindow.py) by executing pyside-uic mainwindow.ui -o mainwindow.py
"""

# from qt_creator_gui.mainwindow import Ui_MainWindow
# todo: resolve issue with namespace (get rid of from PySide.QtCore import * and from PySide.QtGui import *)
from PySide import QtGui
from PySide.QtCore import *
from PySide.QtGui import *

# import to plot stuff
# import matplotlib
# matplotlib.use('Qt4Agg')
# matplotlib.rcParams['backend.qt4']='PySide'
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas



from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas)

from PyQt4.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui') # with this we don't have to convert the .ui file into a python file!
# from qt_creator_gui.mainwindow import Ui_MainWindow # with this we have to first compile (pyside-uic mainwindow.ui -o mainwindow.py)


# from qt_creator_gui.mainwindow import Ui_MainWindow

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
        "data_length" : 10000,
        "block_size" : 1000
    },
    "kinesis_serial_number" : 83832028,
    "detector_threshold" : 50


}



# todo: write generic thread function that takes arbitrary functions for threading
# class GenericThread(QtCore.QThread):
#     '''
#     Generic thread class see: https://joplaete.wordpress.com/2010/07/21/threading-with-pyqt4/
#     '''
#     def __init__(self, function, *args, **kwargs):
#         QtCore.QThread.__init__(self)
#         self.function = function
#         self.args = args
#         self.kwargs = kwargs
#
#     def __del__(self):
#         self.wait()
#
#     def run(self):
#         self.function(*self.args,**self.kwargs)
#         return


class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self._settings = settings_dict


        # self.fill_widget(self.treeWidget, self._settings)
        self.fill_widget(self.treeWidget_2, self._settings)

        # define variables and datasets
        parameters_Acq = self._settings["parameters_Acq"]
        self.number_of_reads = int(np.ceil(1.0 * parameters_Acq['data_length'] / parameters_Acq['block_size']))
        self.block_size = parameters_Acq['block_size']
        self.elements_left = np.ones(self.number_of_reads)
        self.data_AI1 = np.ones((self.number_of_reads, self.block_size))

        self._recorded_data = deque()
        self.past_commands = deque()

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

    def fill_widget(self, QTreeWidget, value):

        def fill_item(item, value):
            item.setExpanded(True)
            if type(value) is dict:
                for key, val in sorted(value.iteritems()):
                    child = QtGui.QTreeWidgetItem()
                    child.setText(0, unicode(key))
                    item.addChild(child)

                    fill_item(child, val)
            elif type(value) is list:
                for val in value:
                    child = QtGui.QTreeWidgetItem()
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
                # child.setFlags(QtCore.Qt.ItemIsEditable)
                # child.setFlags(QtCore.Qt.ItemIsEnabled)
                child.setFlags(child.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)


            else:
                # child = QtGui.QTreeWidgetItem()
                item.setText(1, unicode(value))
                # item.addChild(child)
                print(value)
                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)

                # child = QtGui.QTreeWidgetItem()
                # child.setText(0, unicode(value))
                # item.addChild(child)
                # print(value)
                # child.setFlags(child.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)


        QTreeWidget.clear()
        fill_item(QTreeWidget.invisibleRootItem(), value)

        QTreeWidget.setColumnWidth(0,150)



class SettingsTree(QtGui.QTreeWidget):

    def __init__(self, parent = None):
        super(SettingsTree, self).__init__(parent)
        self.setColumnCount(1)
        self.setHeaderLabel("Settings")
        self.settings = settings_dict
        self.style()
        self.fill_widget_2_columns(self.settings)

    def fill_widget_2_columns(self, value):

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
                item.setText(1,  unicode(value))
                # child = QTreeWidgetItem()
                # child.setText(0, unicode(value))
                # item.addChild(child)
                print(value)
                item.setFlags(Qt.ItemIsSelectable |Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)

        self.clear()
        fill_item(self.invisibleRootItem(), value)

    # def fill_widget(self, value):
    #
    #     def fill_item(item, value):
    #         item.setExpanded(True)
    #         if type(value) is dict:
    #             for key, val in sorted(value.iteritems()):
    #                 child = QTreeWidgetItem()
    #                 child.setText(0, unicode(key))
    #                 item.addChild(child)
    #                 fill_item(child, val)
    #         elif type(value) is list:
    #             for val in value:
    #                 child = QTreeWidgetItem()
    #                 item.addChild(child)
    #             if type(val) is dict:
    #                 child.setText(0, '[dict]')
    #                 fill_item(child, val)
    #             elif type(val) is list:
    #                 child.setText(0, '[list]')
    #                 fill_item(child, val)
    #             else:
    #                 child.setText(0, unicode(val))
    #             child.setExpanded(True)
    #
    #             child.setFlags(Qt.ItemIsSelectable |Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)
    #
    #         else:
    #             child = QTreeWidgetItem()
    #             child.setText(0, unicode(value))
    #             item.addChild(child)
    #             child.setFlags(Qt.ItemIsSelectable |Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)
    #
    #     self.clear()
    #     fill_item(self.invisibleRootItem(), value)



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
