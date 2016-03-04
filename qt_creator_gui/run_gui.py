"""
Created on Feb 2 2016

@author: Jan Gieseler

# this file creates the gui
# gui is designed with QT Designer that creates a .ui file (e.g. mainwindow.ui)
# To get the resulting .py file use the batch (pyside-uic.bat) file that contains C:\Anaconda\python.exe C:\Anaconda\Lib\site-packages\PySide\scripts\uic.py %*
# This converts the .ui file into .py file (e.g. mainwindow.py) by executing pyside-uic mainwindow.ui -o mainwindow.py
"""

# from qt_creator_gui.mainwindow import Ui_MainWindow
import sys
# todo: resolve issue with namespace (get rid of from PySide.QtCore import * and from PySide.QtGui import *)
from PySide import QtCore, QtGui
from PySide.QtCore import *
from PySide.QtGui import *
from helper_functions.reading_writing import save_json
import pandas as pd
import hardware_modules.maestro as maestro
from copy import deepcopy
import hardware_modules.DCServo_Kinesis_dll as DCServo_Kinesis
import os
from helper_functions.test_types import dict_difference

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from PyQt4.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui') # with this we don't have to convert the .ui file into a python file!
# from qt_creator_gui.mainwindow import Ui_MainWindow # with this we have to first compile (pyside-uic mainwindow.ui -o mainwindow.py)


# from qt_creator_gui.mainwindow import Ui_MainWindow

import datetime
from collections import deque
import numpy as np
import lib.FPGA_PID_Loop_Simple as NI
import time
import hardware_modules.PI_Controler as PI_Controler


# ============= GENERAL SETTING ====================================
# ==================================================================

# todo: asign data containers to thread objects and read those datacontainers in gui where it is written to the guis data container
# todo: at startup execute the settings or set the controls such that they match the actual situation of the experiment
# todo: actually turn the servos after position has reached. Now the servo is trying to adjust the position and one can hear a little noise
# this is a example for the settings. do not delete. The type is the variables defined here is used to cast the parameters into the right format
SETTINGS_DICT = {
    "record_length" : 100,
    "parameters_PI" : {
        "sample_period_PI" : int(8e5),
        "gains" : {'proportional': 1.0, 'integral':0.1},
        "setpoint" : 0,
        "piezo" : 0
    },
    "parameters_Acq" : {
        "sample_period_acq" : 100,
        "data_length" : int(1e5),
        "block_size" : 2000
    },
    "detector_threshold" : 50,
    "data_path" : "Z:/Lab/Cantilever/Measurements/20160209_InterferometerStabilization/data",
    "hardware" : {
        "serial_port_maestro" : "COM5",
        "parameters_whitelight" : {
            "channel" : 0,
            "position_list" : {'on': 4*600, 'off':4*1750},
            "settle_time" : 0.2
        },
        "parameters_filterwheel" : {
            "channel" : 1,
            "position_list" : {'ND1.0': 4*600, 'LP':4*1550, 'ND2.0':4*2500}
        },
        "parameters_camera" : {
            "channel" : 2,
            "position_list" : {'on': 4*600, 'off':4*1750},
            "settle_time" : 0.2
        },
        "channel_beam_block_IR" : 4,
        "channel_beam_block_Green" : 5,
    "kinesis_serial_number" : 83832028,
    },
    'live_data_ids' : {
        'AI1': True, 'AI1_raw': True,  'min': False, 'max': True, 'mean': True, 'stddev': True
    }
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
        def create_threads():

            # ============= threading ====================================
            # self._thread_acq = AcquisitionThread(self)
            # self._thread_acq.updateProgress.connect(self.update_plot_live)

            self._thread_acq_new = AcquisitionThreadNew(self)
            self._thread_acq_new.updateProgress.connect(self.update_plot_live_new)

            self._thread_acq_fifo = AcquisitionFIFOThread(self)
            self._thread_acq_fifo.updateProgress.connect(self.update_status)

            self._thread_pol = PolarizationControlThread(self)

            self._thread_pol_stab = PolarizationStabilizationThread(self)
        def connect_hardware():
            # create connections to hardware
            hardware_settings = self._settings['hardware']
            self._servo = maestro.Controller(hardware_settings['serial_port_maestro'])
            self.beam_block_IR = maestro.BeamBlock(self._servo, hardware_settings['channel_beam_block_IR'])
            self.beam_block_Green = maestro.BeamBlock(self._servo, hardware_settings['channel_beam_block_Green'])
            self.filterwheel = maestro.FilterWheel(self._servo, **hardware_settings['parameters_filterwheel'])
            self.whitelight = maestro.FilterWheel(self._servo, **hardware_settings['parameters_whitelight'])
            self.camera = maestro.FilterWheel(self._servo, **hardware_settings['parameters_camera'])
            self.servo_polarization = DCServo_Kinesis.TDC001(hardware_settings["kinesis_serial_number"])


            # =============================================================
            # ===== NI FPGA ===============================================
            # =============================================================
            # connect to FPGA and start it
            self.fpga = NI.NI7845R()
            self.fpga.start()


            # create PI (proportional integral) controler object
            self.FPGA_PI = NI.NI_FPGA_PI(self.fpga, **self._settings["parameters_PI"])
            self.FPGA_READ_FIFO = NI.NI_FPGA_READ_FIFO(self.fpga, **self._settings["parameters_Acq"])

        def connect_controls():
            # =============================================================
            # ===== LINK WIDGETS TO FUNCTIONS =============================
            # =============================================================

            # link slider to functions
            print(self.servo_polarization.get_position() * 100)
            self.sliderPosition.setValue(int(self.servo_polarization.get_position() * 100))
            self.sliderPosition.valueChanged.connect(lambda: self.set_position())

            # link buttons to functions
            self.btn_start_record.clicked.connect(lambda: self.btn_clicked())
            self.btn_stop_record.clicked.connect(lambda: self.btn_clicked())
            self.btn_clear_record.clicked.connect(lambda: self.btn_clicked())
            self.btn_start_record_fpga.clicked.connect(lambda: self.btn_clicked())
            self.btn_clear_record_fpga.clicked.connect(lambda: self.btn_clicked())
            self.btn_save_to_disk.clicked.connect(lambda: self.btn_clicked())

            self.btn_plus.clicked.connect(lambda: self.set_position())
            self.btn_minus.clicked.connect(lambda: self.set_position())
            self.btn_center.clicked.connect(lambda: self.set_position())
            self.btn_to_zero.clicked.connect(lambda: self.set_position())



            # link checkboxes to functions
            self.checkIRon.stateChanged.connect(lambda: self.control_light())
            self.checkGreenon.stateChanged.connect(lambda: self.control_light())
            self.checkWhiteLighton.stateChanged.connect(lambda: self.control_light())
            self.checkCameraon.stateChanged.connect(lambda: self.control_light())
            self.checkPIActive.stateChanged.connect(lambda: self.switch_PI_loop())

            # link combo box
            self.cmb_filterwheel.addItems(self._settings['hardware']['parameters_filterwheel']['position_list'].keys())
            self.cmb_filterwheel.currentIndexChanged.connect(lambda: self.control_light())

            print("servopos",self.servo_polarization.get_position())
            self.treeWidget.itemChanged.connect(lambda: self.update_parameters())

        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self._settings = set_settings(SETTINGS_DICT)

        self.fill_treeWidget(self.treeWidget, self._settings)

        # define some data sets
        self._recorded_data = deque() # recorded data in the live plot
        self._fifo_data = deque() # data from last FIFO read
        self.past_commands = deque() # history of executed commands
        self._time_traces  = [] # all the timetraces that have been acquired
        # also for recorded data in the live plot but can me easy extended to take more data
        self._live_data = {}
        for id in self._settings['live_data_ids']:
            self._live_data.update({id: deque()})

        connect_hardware()
        create_figures()
        connect_controls()
        create_threads()

        self.treeWidget.collapseAll()

    def __del__(self):
        '''
        Cleans up connections
        '''
        self._thread_acq.stop()

        self.fpga.stop()

    def btn_clicked(self):
        sender = self.sender()
        # self.statusBar().showMessage(sender.objectName() + ' was pressed')
        if sender.objectName() == "btn_start_record":
            # self._thread_acq.start()
            self._thread_acq_new.start()
        elif sender.objectName() == "btn_stop_record":
            # self._thread_acq.stop()
            self._thread_acq_new.stop()
        elif str(sender.objectName()) in {"btn_clear_record","btn_clear_record_fpga"}:
            self.clear_plot(sender)
        elif str(sender.objectName()) in {"btn_save_to_disk"}:
            self.save_data(sender)
        elif sender.objectName() == "btn_start_record_fpga":
            self._thread_acq_fifo.start()
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
            if parameter == 'block_size':
                self.FPGA_READ_FIFO.block_size = value_new
            elif parameter == 'sample_period_acq':
                self.FPGA_READ_FIFO.sample_period_acq = value_new
            elif parameter == 'data_length':
                self.FPGA_READ_FIFO.data_length = value_new
            elif parameter == 'integral':
                gains = self.FPGA_PI.gains
                gains.update({'integral':value_new})
                self.FPGA_PI.gains = gains
            elif parameter == 'proportional':
                gains = self.FPGA_PI.gains
                gains.update({'proportional':value_new})
                self.FPGA_PI.gains = gains
            elif parameter == 'data_path':
                if os.path.isdir(value_new):
                    self.log("path {:s} changed!!!".format(value_new))
                else:
                    self.log("warning path {:s} is not valid!!!".format(value_new))
                    updated_success = False
            elif parameter in {'detector_threshold', 'record_length'}:
                # these parameters are no settings actually just change some visualizations in the gui
                pass
            elif parameter in SETTINGS_DICT['live_data_ids'].keys():
                # these parameters are no settings actually just change some visualizations in the gui
                pass
            elif parameter in (SETTINGS_DICT['hardware'].keys()
                                   + SETTINGS_DICT['hardware']['parameters_filterwheel'].keys()
                                   + SETTINGS_DICT['hardware']['parameters_filterwheel']['position_list'].keys()):
                self.log("Harware parameter {:s} can not be changed online.".format(parameter))
                updated_success = False
            elif parameter == 'piezo':
                self.FPGA_PI.piezo = value_new
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

                    if isinstance(value_default, bool):
                        print(value)
                        value = value == 'True'
                        print(value)
                        change_success = change_parameter(parameter, value_old, value)
                    elif isinstance(value_default, int):
                        value = int(value)
                        change_success = change_parameter(parameter, value_old, value)
                    elif isinstance(value_default, float):
                        value = float(value)
                        change_success = change_parameter(parameter, value_old, value)
                    elif isinstance(value_default, str):
                        value = str(value)
                        change_success = change_parameter(parameter, value_old, value)
                    else:
                        change_success = False
                        print("WARNING, TYPE NOT RECOGNIZED!!!!")

                    if change_success:
                        dictator.update({parameter : value})
                        self.log("changed parameter {:s} from {:s} to {:s}!".format(parameter, str(value_old), str(value)))
                    else:
                        # set back to original values if value entered value is not valid
                        print(self._settings)
                        self.fill_treeWidget(self.treeWidget, self._settings)

                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise


    def save_data(self, sender):

        def save_timetrace(timetrace):

            filename = "{:s}_{:s}.dat".format(timetrace["time"], timetrace["tag"])
            filename = filename.replace(' ', '_')
            filename = filename.replace(':', '_')
            filename = "{:s}/{:s}".format(self._settings['data_path'], filename)

            save_json(timetrace['parameters'], filename.replace('.dat', '.json'))
            self.log("{:s} written to disk".format(filename.replace('.dat', '.json')), 1000)

            df = pd.DataFrame(timetrace['data'], columns = ["detector signal (bits)"])
            df.to_csv(filename, index = False, header=True)
            self.log("{:s} written to disk".format(filename), 1000)

            print(filename)

        if sender.objectName() == "btn_save_to_disk":
            selected_timetraces = [index.data().toString().split("\t")[0] for index in self.list_timetraces.selectedIndexes()]
            for timetrace in self._time_traces:
                if timetrace.get('time') in  selected_timetraces:
                    save_timetrace(timetrace)

    def update_status(self, progress):
        self.progressBar.setValue(progress)
        if progress == 100:
            parameters = deepcopy(self._settings)
            self._time_traces.append({'time': self.get_time(), 'tag': str(self.txt_tag.text()), 'data' : np.array(self._fifo_data).flatten(), 'parameters' : parameters})

            self.update_plot_fifo()
            self.log("FIFO acq. completed",1000)

    def update_plot_live(self, data_point):

        def wrap_data(data):
            if data > 2**15:
                data -= 2**16
            return data

        self._detector_signal = wrap_data(data_point)
        self._recorded_data.append(self._detector_signal)

        if len(self._recorded_data) > self._settings["record_length"]:
            self._recorded_data.popleft()
        self.axes_live.clear()
        self.axes_live.plot(list(self._recorded_data))
        detector_threshold = self._settings["detector_threshold"]
        self.axes_live.plot([0, self._settings["record_length"]], [detector_threshold, detector_threshold], 'k--')
        self.axes_live.plot([0, self._settings["record_length"]], [-detector_threshold, -detector_threshold], 'k--')

        self.canvas_live.draw()

        self.lbl_detector_signal.setText("{:d}".format(self._recorded_data[-1]))

    def update_plot_live_new(self, XX):
        '''
        when done thsis function will replace update_plot_live
        :param data_point:
        :return:
        '''

        self.axes_live.clear()
        #todo: update plot without clearing all the data, so that it doesn't "blink"
        for ID in self._settings['live_data_ids']:
            # throw out oldest data point if max queue length has been reached
            if len(self._live_data[ID]) > self._settings["record_length"]:
                self._live_data[ID].popleft()

            # plot data if set to true
            if self._settings['live_data_ids'][ID] == True:
                self.axes_live.plot(list(self._live_data[ID]))
                detector_threshold = self._settings["detector_threshold"]
                self.axes_live.plot([0, self._settings["record_length"]], [detector_threshold, detector_threshold], 'k--')
                self.axes_live.plot([0, self._settings["record_length"]], [-detector_threshold, -detector_threshold], 'k--')

            self.canvas_live.draw()

            # self.lbl_detector_signal.setText("{:d}".format(self._recorded_data[-1]))

    def update_plot_fifo(self):

        self.axes_timetrace.clear()
        self.axes_psd.clear()
        model = QtGui.QStandardItemModel(self.list_timetraces)

        for data_set in self._time_traces:
            # data = np.array(self._fifo_data).flatten()
            data = data_set['data']
            data_length = len(data)

            # time traces
            print(data_set["parameters"])
            time_step = int(data_set["parameters"]["parameters_Acq"]["sample_period_acq"]) / 40e6
            # time_step = int(self._settings["parameters_Acq"]["sample_period_acq"]) / 40e6
            times = 1e3 * np.linspace(0,time_step * data_length,data_length)
            self.axes_timetrace.plot(times, data)

            # PSD
            freq_step = 1/(time_step * data_length)
            freqs = np.linspace(0,freq_step * data_length / 2,data_length/2)
            data_PSD = np.abs(np.fft.fft(data))**2
            data_PSD = data_PSD[range(data_length/2)]
            self.axes_psd.loglog(freqs, data_PSD)

            model.appendRow(QtGui.QStandardItem("{:s}\t{:s}".format(data_set['time'], data_set['tag'])))

        self.list_timetraces.setModel(model)
        self.list_timetraces.show()

        self.axes_timetrace.set_xlabel('time (ms)')
        self.axes_psd.set_xlabel('frequency (Hz)')

        self.canvas_timetrace.draw()
        self.canvas_psd.draw()

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


    def set_position(self):

        sender = self.sender()
        if sender.objectName() == "sliderPosition":
            value = 0.01 * self.sliderPosition.value() # slider max value 600 corresponding to 6mm
            self._thread_pol.target_position = value
            self._thread_pol.start()
        elif sender.objectName() == "btn_plus":
            self.sliderPosition.setValue(self.sliderPosition.value()+10)
        elif sender.objectName() == "btn_center":
            self.sliderPosition.setValue(300)
        elif sender.objectName() == "btn_minus":
            self.sliderPosition.setValue(self.sliderPosition.value()-10)
        elif sender.objectName() == "btn_to_zero":
            self._thread_pol_stab.start()
        self.lbl_pol_position.setText("{:0.02f} mm".format(0.01 * self.sliderPosition.value()))

    def control_light(self):
        '''
        Changes script to be executed based on current text in box
        :param ApplicationWindow:
        '''

        sender = self.sender()
        if sender.objectName() == "checkIRon":
            status = self.checkIRon.isChecked()
            if status:
                self.beam_block_IR.open()
            else:
                self.beam_block_IR.block()

            self.log("IR laser {:s}".format(str(status)),1000)
        elif sender.objectName() == "checkGreenon":
            status = self.checkGreenon.isChecked()
            # the beam block is mounted in a different way that's why the calls for blocking and closing are inverted
            if status:
                self.beam_block_Green.block()
            else:
                self.beam_block_Green.open()

            self.log("Green laser {:s}".format(str(status)),1000)
        elif sender.objectName() == "checkWhiteLighton":
            status = self.checkWhiteLighton.isChecked()
            if status:
                self.whitelight.goto("on")
            else:
                self.whitelight.goto("off")
            self.log("White light {:s}".format(str(status)),1000)
        elif sender.objectName() == "checkCameraon":
            status = self.checkCameraon.isChecked()
            if status:
                self.camera.goto("on")
            else:
                self.camera.goto("off")
            self.log("Camera {:s}".format(str(status)),1000)



        elif sender.objectName() == "cmb_filterwheel":
            # cast explicitely to str because combobox element is QString, but filterwheel only understands python strings
            filter = str(self.cmb_filterwheel.currentText())
            self.log("Filter set to {:s}".format(filter),1000)
            self.filterwheel.goto(filter)

    def switch_PI_loop(self):
        '''
        Changes script to be executed based on current text in box
        :param ApplicationWindow:
        '''
        status_PI_loop =self.checkPIActive.isChecked()
        self.FPGA_PI.status_PI = status_PI_loop
        self.log("Feedback stabilization on: {:s}".format(str(status_PI_loop)),1000)

    def fill_treeWidget(self, QTreeWidget, value):

        def fill_item(item, value):
            # item.setExpanded(True)
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

            else:
                item.setText(1, unicode(value))

                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)


        QTreeWidget.clear()
        fill_item(QTreeWidget.invisibleRootItem(), value)

        QTreeWidget.setColumnWidth(0,200)



class PolarizationStabilizationThread(QtCore.QThread):

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(float) # returns the new motor position as a signal

    #You can do any extra things in this init you need
    def __init__(self, ControlMainWindow):
        """

        :param servo: Kinsesis Servo controler object that controls the polarization
        :return:
        """
        QtCore.QThread.__init__(self)
        self.ControlMainWindow = ControlMainWindow


    def run(self):


        detector_value_zero = False
        max_iter = 100
        count = 1
        detector_threshold = SETTINGS_DICT["detector_threshold"]

        while detector_value_zero == False:
            detector_value = self.ControlMainWindow._recorded_data[-1]

            if abs(detector_value > detector_threshold) > 2000:
                step_size = 40
            elif abs(detector_value > detector_threshold) > 1000:
                step_size = 20
            elif abs(detector_value > detector_threshold) > 500:
                step_size = 10
            elif abs(detector_value > detector_threshold) > 100:
                step_size = 5
            else:
                step_size = 1

            if detector_value > detector_threshold:
                # print(detector_value, "step down")
                self.ControlMainWindow.sliderPosition.setValue(self.ControlMainWindow.sliderPosition.value()-step_size)
            elif detector_value < -detector_threshold:
                # print(detector_value, "step up")
                self.ControlMainWindow.sliderPosition.setValue(self.ControlMainWindow.sliderPosition.value()+step_size)
            else:
                print(detector_value, "detector close to zero!")
                detector_value_zero = True

            count += 1
            if count >max_iter:
                detector_value_zero = True

            wait_time = self.ControlMainWindow.servo_polarization.wait_time(step_size)
            time.sleep(wait_time)

class AcquisitionThread(QtCore.QThread):

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(int)

    #You can do any extra things in this init you need
    def __init__(self, ControlMainWindow):
        """

        :param PI: lib.FPGA_PID_Loop_Simple.NI_FPGA_PI object that handles the feedback loop
        :return:
        """
        self._recording = False
        self._PI = ControlMainWindow.FPGA_PI

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

class AcquisitionThreadNew(QtCore.QThread):

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(int)

    #You can do any extra things in this init you need
    def __init__(self, ControlMainWindow):
        """

        :param PI: lib.FPGA_PID_Loop_Simple.NI_FPGA_PI object that handles the feedback loop
        :return:
        """
        self._recording = False

        self.data = ControlMainWindow._live_data
        print('============== creating threaddddd =============')
        print(self.data)
        self.data_ids =  ControlMainWindow._settings['live_data_ids']
        self._PI = ControlMainWindow.FPGA_PI
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
            data = {}
            data.update(self._PI.minmax)
            data.update(self._PI.detector)

            try:
                for ID in self.data_ids:
                    self.data[ID].append(data[ID])

            except KeyError:
                print('AcquisitionThreadNew: key {:s} not valid'.format(ID))
            except:
                # todo: this error should be caught and raise an exeption that the requested data doesn't exist
                print("Unexpected error:", sys.exc_info()[0])
                raise
            # just emit any signal to trigger an action in the gui
            self.updateProgress.emit(1)
            time.sleep(0.2)

    def stop(self):
        self._recording = False


class AcquisitionFIFOThread(QtCore.QThread):

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(int) # returns progess in %

    #You can do any extra things in this init you need
    def __init__(self, ControlMainWindow):
        """

        :param PI: lib.FPGA_PID_Loop_Simple.NI_FPGA_PI object that handles the feedback loop
        :return:
        """
        print("created AcquisitionFIFOThread")
        self._recording = False
        self._FPGA_READ_FIFO = ControlMainWindow.FPGA_READ_FIFO

        self.parameters_Acq = ControlMainWindow._settings["parameters_Acq"]
        self.data = ControlMainWindow._fifo_data

        QtCore.QThread.__init__(self)

    #A QThread is run by calling it's start() function, which calls this run()
    #function in it's own "thread".
    def run(self):

        number_of_reads = int(np.ceil(1.0 * int(self.parameters_Acq['data_length']) / int(self.parameters_Acq['block_size']) ))
        self.elements_left = np.ones(number_of_reads)
        print(number_of_reads)
        self._recording = True
        self.data.clear()
        self._FPGA_READ_FIFO.start()

        for i in range(number_of_reads):

            fifo_data =self._FPGA_READ_FIFO.data_queue.get()
            self.data.append(np.array(fifo_data[0]))
            self.elements_left[i] = int(fifo_data[2])

            progress = int(100 * (i+1)  / number_of_reads)

            self.updateProgress.emit(progress)

        self._recording = False
    def stop(self):
        self._recording = False


class PolarizationControlThread(QtCore.QThread):

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(float)

    #You can do any extra things in this init you need
    def __init__(self, ControlMainWindow):
        """

        :param servo: Kinsesis Servo controler object that controls the polarization
        :return:
        """
        self._running = False
        self._servo = ControlMainWindow.servo_polarization
        QtCore.QThread.__init__(self)

    @property
    def target_position(self):
        return self._target_position
    @target_position.setter
    def  target_position(self, target_position):
        self._target_position = target_position

    #A QThread is run by calling it's start() function, which calls this run()
    #function in it's own "thread".
    def run(self):
        self._running = True
        while self._running:

            self._servo.move_servo(self.target_position)
            time.sleep(0.1)
            actual_position = self._servo.get_position()
            #Emit the signal so it can be received on the UI side.
            self.updateProgress.emit(actual_position)
            if abs(self.target_position - actual_position)<0.01:
                self._running = False
            print(abs(self.target_position - actual_position))



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
