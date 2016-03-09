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
# option A
Ui_MainWindow, QMainWindow = loadUiType('zi_control.ui') # with this we don't have to convert the .ui file into a python file!
# option B
# from qt_creator_gui.zi_control import Ui_MainWindow # with this we have to first compile (pyside-uic mainwindow.ui -o mainwindow.py)


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

# SETTINGS_DICT = {
#         'sweep' : {
#             'start' : {'value': 0.0, 'valid_values': None, 'info':'start value of sweep', 'visible' : True},
#             'stop' : {'value': 0.0, 'valid_values': None, 'info':'end value of sweep', 'visible' : True},
#             'samplecount' : {'value': 0, 'valid_values': None, 'info':'number of data points', 'visible' : True},
#             'gridnode' : {'value': 'oscs/0/freq', 'valid_values': ['oscs/0/freq', 'oscs/1/freq'], 'info':'channel that\'s used in sweep', 'visible' : True},
#             'xmapping' : {'value': 0, 'valid_values': [0,1], 'info':'mapping 0 = linear, 1 = logarithmic', 'visible' : True},
#             'bandwidthcontrol' : {'value': 2, 'valid_values': [2], 'info':'2 = automatic bandwidth control', 'visible' : True},
#             'scan' : {'value': 0, 'valid_values': [0, 1, 2], 'info':'scan direction 0 = sequential, 1 = binary (non-sequential, each point once), 2 = bidirecctional (forward then reverse)', 'visible' : True},
#             'loopcount' : {'value': 1, 'valid_values': None, 'info':'number of times it sweeps', 'visible' : False},
#             'averaging/sample' : {'value': 0, 'valid_values': None, 'info':'number of samples to average over', 'visible' : True}
#         },
#         'peak_search_settings' : {
#             'f_min': 1875.0e3,
#             'f_max': 1878.0e3,
#             'df_coarse' : 5,
#             'df_fine': 1,
#             'N_fine': 101,
#             'samplesPerPt' : 1,
#             'samplesPerPt' : {'arthur':1, 'jan':2, 'aaron':{'1':1,'2':2}}
#         }
# }



from default_settings import MAIN_SETTINGS, SCRIPTS, SWEEP_SETTINGS


# rw.save_json(SETTINGS_DICT, './gui_zi_control_default_settings.json')

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
            # self.tree_scripts.itemChanged.connect(lambda: self.update_parameters())
            self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts, self._script_settings))
            self.tree_main_settings.itemChanged.connect(lambda: self.update_parameters(self.tree_main_settings, self._main_settings))
            self.zi.updateProgress.connect(self.update_status)

        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self._script_settings = set_settings(SCRIPTS)
        self._main_settings = set_settings(MAIN_SETTINGS)

        self.fill_treeWidget(self.tree_scripts, self._script_settings)
        self.fill_treeWidget(self.tree_main_settings, self._main_settings)

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

        # self.tree_scripts.collapseAll()
        self._scripts = ['sweep', 'measure Q high res']


    def __del__(self):
        '''
        Cleans up connections
        '''
        self.zi.stop()

    def btn_clicked(self):
        sender = self.sender()

        if sender.objectName() == "btn_start":
            if self.tree_scripts.currentItem() == None:
                self.log('No script selected. Select script first!')
            else:
                parents = []
                parent = self.tree_scripts.currentItem()
                script_name = None
                while parent != None:
                    if str(parent.text(0)) in self._scripts and script_name == None:
                        script_name = parent.text(0)
                    parents.insert(0,str(parent.text(0)))
                    parent = parent.parent()

                if script_name == None:
                    script_name = str(self.tree_scripts.currentItem().text(0))
                    parents.insert(0, script_name)

                script_parameter = self._script_settings
                for i in parents:
                    script_parameter = script_parameter[i]

                if script_name in self._scripts:
                    self._script_name = script_name
                    self.run_script(script_parameter)




            # self.zi.run_sweep(self.sweep_data)
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

    def run_script(self, script_parameter = None):

        if self._script_name == 'sweep':
            self.zi.run_sweep(self.sweep_data)
        elif self._script_name == 'measure Q high res':
            pass

    def stop_script(self):
        if self._script_name == 'sweep':
            self.zi.stop()





    def update_parameters(self, treeWidget, parameter_dict):
        '''
        is called when a parameter in the tree is changed
        this function updates the dictionary that holds all the parameter
        :param treeWidget: treeWiget object where some element has been changed
        :param parameter_dict: a map of the current values of the treeWidget
        :return: None
        '''



        def send_parameter_to_harware(parameter, value_new, target):
            '''
            for certain parameters we want to send the changes to the hardware
            :param parameter: paranmeter that has been changed
            :param value_new: new parameter value
            :return:
            '''

            if target  == 'ZI sweep':
                self.zi.sweep_settings = {parameter : value_new}
                updated_success = True
                self.log("parameter ({:s}) change sent to {:s}.".format(parameter, target))

        def set_type(value, valid_values):

            '''
            checks if value is in valid_values
            :param value: value to be checked
            :param valid_values: list of valid values | type | tuple of types
            :return: value_new the value cast into the type of value_default
            '''
            msg = ''
            def cast_type(var, typ):
                '''
                cast variable var into type typ
                :param var:
                :param typ:
                :return: variable cast into the same type as typ or None if not recognized
                '''
                try:
                    if typ == int:
                        var = int(var)
                    elif typ == float:
                        var = float(var)
                    elif typ  == str:
                        var = str(var)
                    else:
                        var = None
                except ValueError:
                    var = None
                return var

            if isinstance(valid_values, list):
                # if valid_values is a list, we cast into the same type (because we receive a unicode type from the GUI) and check if value is
                # contained in the list
                value = cast_type(value, type(valid_values[0])) # cast into same type as valid values
                if value in valid_values:
                    value_new = value
                else:
                    msg = '{:s} is wrong value. Should be {:s}'.format(str(value), str(valid_values))
                    value_new = None
            elif isinstance(valid_values, type):
                # if valid value is a type we cast into value into same type
                value_new = cast_type(value, valid_values)
            elif isinstance(valid_values, tuple):
                # if valid values is a tuple is is most likely (inf, float)
                # in that case min(int, float) gives float, which is the more general type
                value = cast_type(value, min(valid_values))
                if isinstance(value, valid_values):
                    value_new = value
                else:
                    msg = '{:s} is wrong value. Should be of type {:s}'.format(str(value), str(valid_values))
                    value_new = None

            return value_new, msg
        if not treeWidget.currentItem() == None:
            parameter = str(treeWidget.currentItem().text(0))
            value = unicode(treeWidget.currentItem().text(1))
            parents = []
            if treeWidget.currentColumn() == 0:
                self.log("Tried to edit parameter name. This is not allowed!!", 1000)
                self.fill_treeWidget(treeWidget, parameter_dict) # set tree back to status before it was edited by user
            else:
                parent = treeWidget.currentItem().parent()
                while parent != None:
                    parents.insert(0,str(parent.text(0)))
                    parent = parent.parent()
                try:
                    # get the value before it was changed in the treeWidget
                    dictator = parameter_dict
                    for i in parents:
                        dictator = dictator[i]
                    print(dictator[parameter])
                    value_old = dictator[parameter]['value']
                    valid_values = dictator[parameter]['valid_values']

                    # verify that the new value is valid
                    value, msg = set_type(value, valid_values)
                    print('value, msg')
                    print(value, msg)
                    if value == None:
                        self.log(msg)
                        self.fill_treeWidget(treeWidget, parameter_dict)
                    else:
                        self.log("Updated {:s} from {:s} to {:s}!!".format(parameter,str(value_old), str(value)), 1000)
                        print('send_parameter_to_harware(parameter, value)')
                        if 'target' in dictator[parameter].keys():
                            send_parameter_to_harware(parameter, value, dictator[parameter]['target'])
                        dictator[parameter].update({'value' : value})

                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise



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

        model = QtGui.QStandardItemModel(self.list_history)
        for item in self.past_commands:
            model.insertRow(0,QtGui.QStandardItem(item))

            # model.appendRow(QtGui.QStandardItem(item))
        self.list_history.setModel(model)
        self.list_history.show()

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

        QTreeWidget.setColumnWidth(0,300)


class ScriptThread(QtCore.QThread):
    '''
    This class starts a script on its own thread
    '''

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(int)

    #You can do any extra things in this init you need
    def __init__(self):
        """

        :param PI: lib.FPGA_PID_Loop_Simple.NI_FPGA_PI object that handles the feedback loop
        :return:
        """
        self._recording = False

        QtCore.QThread.__init__(self)


    def __del__(self):
        self.stop()
    #A QThread is run by calling it's start() function, which calls this run()
    #function in it's own "thread".
    def run(self):
        self._recording = True
        while self._recording:
            #Emit the signal so it can be received on the UI side.
            # data_point = np.random.randint(-32000, 32000)
            # try statement
            # try:
            data_point = self._PI.detector
            self.updateProgress.emit(data_point[0])
            time.sleep(0.2)


        print("acquisition ended")
    def stop(self):
        self._recording = False


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
