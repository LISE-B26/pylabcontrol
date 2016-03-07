"""
Created on Feb 2 2016

@author: Jan Gieseler

# this file creates the gui for data acquisition with the ZI lockin
# gui is designed with QT Designer that creates a .ui file (e.g. zi_control.ui)
# To get the resulting .py file use the batch (pyside-uic.bat) file that contains C:\Anaconda\python.exe C:\Anaconda\Lib\site-packages\PySide\scripts\uic.py %*
# This converts the .ui file into .py file (e.g. mainwindow.py) by executing pyside-uic mainwindow.ui -o mainwindow.py
"""

import sys
# todo: resolve issue with namespace (get rid of from PySide.QtCore import * and from PySide.QtGui import *)
from PySide import QtCore, QtGui
from PySide.QtCore import *
from PySide.QtGui import *
from helper_functions.reading_writing import save_json
import pandas as pd
from copy import deepcopy
import os
import hardware_modules.ZiControl as ZI
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from PyQt4.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('zi_control.ui') # with this we don't have to convert the .ui file into a python file!

import datetime
from collections import deque
import time
import helper_functions.reading_writing as rw

# ============= GENERAL SETTING ====================================
# ==================================================================

#
# SETTINGS_DICT = {
#     'zi_settings' : {
#         'amplitude' : 0.1e-3,
#         'offset' : 1,
#         'freq' : 1.88e6,
#         'ACCoupling':1,
#         'inChannel' : 0,
#         'outChannel' : 0,
#         'auxChannel' : 0,
#         'add' : 1,
#         'range' : 10e-3
#     },
#     'peak_search_settings' : {
#         'f_min': 1875.0e3,
#         'f_max': 1878.0e3,
#         'df_coarse' : 5,
#         'df_fine': 1,
#         'N_fine': 101,
#         'samplesPerPt' : 1
#     },
#     'find_peak_settings' : {
#         'f_min': 1875.0e3,
#         'f_max': 1878.0e3,
#         'df' : 5,
#         'samplesPerPt' : 1
#     }
# }
# SETTINGS_DICT =rw.load_json('./gui_zi_control_default_settings.json')

# SETTINGS_DICT = {
#         'sweep' : {
#             'start' : 0,
#             'stop' : 0,
#             'samplecount' : 0,
#             'gridnode' : 'oscs/0/freq',
#             'xmapping' : 0, #0 = linear, 1 = logarithmic
#             'bandwidthcontrol': 2, #2 = automatic bandwidth control
#             'scan' : 0, #scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)
#             'loopcount': 1,
#             'averaging/sample' : 2, #number of samples to average over
#             'start' : {'value': 0, 'valid_values': None, 'info':'start value of sweep', 'visible' : True},
#             'stop' : {'value': 0, 'valid_values': None, 'info':'end value of sweep', 'visible' : True},
#             'samplecount' : {'value': 0, 'valid_values': None, 'info':'end value of sweep', 'visible' : True},
#             'gridnode' : {'value': 'oscs/0/freq', 'valid_values': ['oscs/0/freq', 'oscs/1/freq'], 'info':'channel that\'s used in sweep', 'visible' : True},
#             'xmapping' : {'value': 0, 'valid_values': [0,1], 'info':'mapping 0 = linear, 1 = logarithmic', 'visible' : True}
#         }
# }

SETTINGS_DICT = {
        'sweep' : {
            'start' : {'value': 0.0, 'valid_values': None, 'info':'start value of sweep', 'visible' : True},
            'stop' : {'value': 0.0, 'valid_values': None, 'info':'end value of sweep', 'visible' : True},
            'samplecount' : {'value': 0, 'valid_values': None, 'info':'number of data points', 'visible' : True},
            'gridnode' : {'value': 'oscs/0/freq', 'valid_values': ['oscs/0/freq', 'oscs/1/freq'], 'info':'channel that\'s used in sweep', 'visible' : True},
            'xmapping' : {'value': 0, 'valid_values': [0,1], 'info':'mapping 0 = linear, 1 = logarithmic', 'visible' : True},
            'bandwidthcontrol' : {'value': 2, 'valid_values': [2], 'info':'2 = automatic bandwidth control', 'visible' : True},
            'scan' : {'value': 0, 'valid_values': [0, 1, 2], 'info':'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)', 'visible' : True},
            'loopcount' : {'value': 1, 'valid_values': None, 'info':'number of times it sweeps', 'visible' : False},
            'averaging/sample' : {'value': 0, 'valid_values': None, 'info':'number of samples to average over', 'visible' : True}
        },
        'peak_search_settings' : {
            'f_min': 1875.0e3,
            'f_max': 1878.0e3,
            'df_coarse' : 5,
            'df_fine': 1,
            'N_fine': 101,
            'samplesPerPt' : 1,
            'samplesPerPt' : {'arthur':1, 'jan':2, 'aaron':{'1':1,'2':2}}
        }
}



from default_settings import SETTINGS_DICT


rw.save_json(SETTINGS_DICT, './gui_zi_control_default_settings.json')

class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        def set_settings(settings_dict):
            '''
            here we could add to fill the dictionary with some derived values, like total acquisition time
            :param settings_dict:
            :return:
            '''
            settings = settings_dict

            # settings['parameters_Acq'].update({'acquisition_time': })
            return settings
        def create_figures():
            # fill the empty widgets with a figure
            fig_live = Figure()
            self.canvas_live = FigureCanvas(fig_live)
            self.plot_data_live.addWidget(self.canvas_live)
            self.axes_live = fig_live.add_subplot(111)

            fig_sweep = Figure()
            self.canvas_sweep = FigureCanvas(fig_sweep)
            self.plot_data_sweep.addWidget(self.canvas_sweep)
            self.axes_sweep = fig_sweep.add_subplot(111)
        def connect_hardware():
            # create connections to hardware
            self.zi = ZI.ZIHF2_v2()
        def connect_controls():
            # =============================================================
            # ===== LINK WIDGETS TO FUNCTIONS =============================
            # =============================================================

            # # link slider to functions
            # print(self.servo_polarization.get_position() * 100)
            # self.sliderPosition.setValue(int(self.servo_polarization.get_position() * 100))
            # self.sliderPosition.valueChanged.connect(lambda: self.set_position())
            #
            # # link buttons to functions
            self.btn_start.clicked.connect(lambda: self.btn_clicked())
            # self.btn_stop_record.clicked.connect(lambda: self.btn_clicked())
            # self.btn_clear_record.clicked.connect(lambda: self.btn_clicked())
            # self.btn_start_record_fpga.clicked.connect(lambda: self.btn_clicked())
            # self.btn_clear_record_fpga.clicked.connect(lambda: self.btn_clicked())
            # self.btn_save_to_disk.clicked.connect(lambda: self.btn_clicked())
            #
            # self.btn_plus.clicked.connect(lambda: self.set_position())
            # self.btn_minus.clicked.connect(lambda: self.set_position())
            # self.btn_center.clicked.connect(lambda: self.set_position())
            # self.btn_to_zero.clicked.connect(lambda: self.set_position())
            #
            #
            #
            # # link checkboxes to functions
            # self.checkIRon.stateChanged.connect(lambda: self.control_light())
            # self.checkGreenon.stateChanged.connect(lambda: self.control_light())
            # self.checkWhiteLighton.stateChanged.connect(lambda: self.control_light())
            # self.checkCameraon.stateChanged.connect(lambda: self.control_light())
            # self.checkPIActive.stateChanged.connect(lambda: self.switch_PI_loop())
            #
            # # link combo box
            # self.cmb_filterwheel.addItems(self._settings['hardware']['parameters_filterwheel']['position_list'].keys())
            # self.cmb_filterwheel.currentIndexChanged.connect(lambda: self.control_light())
            #
            # print("servopos",self.servo_polarization.get_position())
            self.treeWidget.itemChanged.connect(lambda: self.update_parameters())
            self.zi.updateProgress.connect(self.update_status)

        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self._settings = set_settings(SETTINGS_DICT)

        self.fill_treeWidget(self.treeWidget, self._settings)

        # define some data sets
        # todo: use maxlength to limit number of commands, the we don't have to pop them manually
        self.past_commands = deque() # history of executed commands
        # also for recorded data in the live plot but can me easy extended to take more data
        self._live_data = {}
        self.sweep_data = {'frequency' : [], 'x' : [], 'y' : [], 'phase': [], 'r':[]}
        # for id in self._settings['live_data_ids']:
        #     self._live_data.update({id: deque()})

        connect_hardware()
        create_figures()
        connect_controls()
        # create_threads()

        self.treeWidget.collapseAll()

    def __del__(self):
        '''
        Cleans up connections
        '''
        self.zi.stop()

    def btn_clicked(self):
        sender = self.sender()
        # self.statusBar().showMessage(sender.objectName() + ' was pressed')
        if sender.objectName() == "btn_start":
            self.zi.run_sweep(self.sweep_data)
        elif sender.objectName() == "btn_stop":
            self.zi.stop()
        # elif str(sender.objectName()) in {"btn_clear_record","btn_clear_record_fpga"}:
        #     self.clear_plot(sender)
        elif str(sender.objectName()) in {"btn_save_to_disk"}:
            print(self.zi.sweep_data)
        # elif sender.objectName() == "btn_start_record_fpga":
        #     self._thread_acq_fifo.start()
        else:
            print('unknown sender: ', sender.objectName())




    def update_parameters(self):
        '''
        is called when a parameter in the tree is changed
        this function updates the dictionary that holds all the parameter
        :return:
        '''

        def change_parameter(parameter, value_old, value_new):
            updated_success = True

            if parameter in (SETTINGS_DICT['sweep'].keys()):
                print({parameter : value_new})
                self.zi.sweep_settings = {parameter : value_new}
                updated_success = True
            else:
                updated_success = False
                self.log("unknown parameter {:s}. No change applied!".format(parameter))

            return updated_success

        if not self.treeWidget.currentItem() == None:
            parameter = str(self.treeWidget.currentItem().text(0))
            value = unicode(self.treeWidget.currentItem().text(1))
            parents = []
            if self.treeWidget.currentColumn() == 0:
                self.log("Tried to edit parameter name. This is not allowed!!", 1000)
            else:
                parent = self.treeWidget.currentItem().parent()
                while parent != None:
                    parents.insert(0,str(parent.text(0)))
                    parent = parent.parent()
                try:
                    dictator = self._settings
                    for i in parents:
                        dictator = dictator[i]
                    value_old = dictator[parameter]

                    dictator = SETTINGS_DICT
                    for i in parents:
                        print i
                        dictator = dictator[i]
                    value_default = dictator[parameter]
                    value, msg = self.set_type(value, value_default)
                    print('value, msg')
                    print(value, msg)
                    if value == None:
                        change_success = False
                        self.log(msg)
                    else:
                        change_success = change_parameter(parameter, value_old, value)

                    if change_success:
                        dictator.update({parameter : value})
                        if isinstance(value, dict) and 'value' in value:
                            self.log("changed parameter {:s} from {:s} to {:s}!".format(parameter, str(value_old['value']), str(value['value'])))
                        else:
                            self.log("changed parameter {:s} from {:s} to {:s}!".format(parameter, str(value_old), str(value)))
                    else:
                        # set back to original values if value entered value is not valid
                        print(self._settings)
                        self.fill_treeWidget(self.treeWidget, self._settings)

                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise

    def set_type(self, value, value_default, valid_values = None):
        '''
        casts value to the same type as value_default
        :param value:
        :param value_default:
        :return: value_new the value cast into the type of value_default
        '''

        msg = 'everything ok'
        try:
            if isinstance(value_default, bool):
                value_new = value == 'True'
            elif isinstance(value_default, int):
                value_new = int(value)
            elif isinstance(value_default, float):
                value_new = float(value)
            elif isinstance(value_default, str):
                value_new = str(value)
            elif isinstance(value_default, dict) and 'value' in value_default:
                # construct dictionary
                value_new = deepcopy(value_default)
                value_new['value'], msg = self.set_type(value, value_default['value'], value_default['valid_values'])
                if value_new['value'] == None:
                    value_new = None
            else:
                value_new = None
        except ValueError:
            value_new = None
            msg = 'wrong type - no change applied'

        if value_new != None and valid_values!=None:
            if (value_new in valid_values) == False:
                value_new = None
                #todo: more detailed msg
                msg = 'value not valid !'

        return value_new, msg

    def plot_psd(self, freq, psd,  axes):
        '''
        plots the power spectral density on to the canvas
        :param freq: x-values array of length N
        :param psd: y-values array of length N
        :param axes: target axes object
        :return: None
        '''
        axes.clear()

        axes.semilogy(freq, psd)

        axes.set_xlabel('frequency (Hz)')


    def update_status(self, progress):
        self.progressBar.setValue(progress)
        # retrieve elements from queue
        if self.zi.sweep_data:
            for key, value in self.sweep_data.iteritems():
                x = self.zi.sweep_data[0][key]
                self.sweep_data[key] = x[np.isfinite(x)] # filter out NaN elements
            self.zi.sweep_data.popleft() # remove from queue

        self.plot_psd(self.sweep_data['frequency'], self.sweep_data['r'], self.axes_sweep)
        self.canvas_sweep.draw()


    def get_time(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    def log(self, msg, wait_time = 1000):
        self.statusbar.showMessage(msg, wait_time)
        time = self.get_time()
        self.past_commands.append("{:s}\t {:s}".format(time, msg))
        if len(self.past_commands) > 10:
            self.past_commands.popleft()

        model = QtGui.QStandardItemModel(self.listView)
        for item in self.past_commands:
            model.insertRow(0,QtGui.QStandardItem(item))

            # model.appendRow(QtGui.QStandardItem(item))
        self.listView.setModel(model)
        self.listView.show()

    def clear_plot(self, sender):
        if sender.objectName() == "btn_clear_record":
            self._recorded_data.clear()

            for ID in self.live_data_ids:
                 if self.live_data_ids[ID]:
                    self.live_data[ID].clear()

            self.axes_live.clear()
            self.canvas_live.draw()
            self.log("Cleared live Data",1000)
        elif sender.objectName() == "btn_clear_record_fpga":
            # get which items are selected. Each entry is of the form {time}\t{tag}. We select only the dataset which were taken at the time of the selected items.
            selected_timetraces = [index.data().toString().split("\t")[0] for index in self.list_timetraces.selectedIndexes()]
            self._time_traces = [x for x in self._time_traces if not (x.get('time') in  selected_timetraces)]
            # delete selected items from data
            # self._time_traces = []
            # update plot
            self.update_plot_fifo()
            self.log("Cleared FIFO Data",1000)

    def fill_treeWidget(self, QTreeWidget, value):

        def fill_item(item, value):
            # item.setExpanded(True)
            if type(value) is dict and not 'value' in value:

                for key, val in sorted(value.iteritems()):
                    # don't show the items that have porperty invisible = False
                    if type(val) is dict and 'value' in val and val['visible'] == False:
                        pass
                    else:
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
                child.setFlags(child.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)
            #
            # elif type(value) is bool:
            #     item.setText(0, unicode(value))
            #     item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)
            #     if value == True:
            #         item.checkState(0) == Qt.Checked
            #         # item.setCheckState(0, Qt.Checked)
            #     elif value == False:
            #         # item.setCheckState(0, Qt.Unchecked)
            #         item.checkState(0) == Qt.Unchecked
            #     else:
            #         print('XXXXX')
            elif type(value) is dict and 'value' in value:
                # instead of a value we have a dictionary that contains additional metadata
                if value['visible']:
                    item.setText(1, unicode(value['value']))
                    item.setToolTip(1, unicode(value['info']))
                    item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)

            else:
                item.setText(1, unicode(value))
                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)


        QTreeWidget.clear()
        fill_item(QTreeWidget.invisibleRootItem(), value)

        QTreeWidget.setColumnWidth(0,200)


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
