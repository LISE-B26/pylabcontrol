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


import hardware_modules.maestro as maestro

import hardware_modules.DCServo_Kinesis_dll as DCServo_Kinesis

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

settings_dict = {
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
    "detector_threshold" : 50,
    "data_path" : "Z:/Lab/Cantilever/Measurements/20160209_InterferometerStabilization",
    "hardware" : {
        "serial_port_maestro" : "COM5",
        "channel_beam_block_IR" : 4,
        "channel_beam_block_Green" : 5,
        "parameters_filterwheel" : {
            "channel" : 1,
            "position_list" : {'ND1.0': 4*600, 'LP':4*1550, 'ND2.0':4*2500}
        },
    "kinesis_serial_number" : 83832028,
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
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self._settings = settings_dict

        self.fill_treeWidget(self.treeWidget, self._settings)

        self._recorded_data = deque()
        self._fifo_data = deque()
        self.past_commands = deque()

        self.connect_hardware()
        self.create_figures()
        self.connect_controls()
        self.create_threads()

        self.treeWidget.collapseAll()

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

    def create_threads(self):

        # ============= threading ====================================
        self._thread_acq = AcquisitionThread(self)
        self._thread_acq.updateProgress.connect(self.update_plot_live)

        self._thread_acq_fifo = AcquisitionFIFOThread(self)
        self._thread_acq_fifo.updateProgress.connect(self.update_status)

        self._thread_pol = PolarizationControlThread(self)

        self._thread_pol_stab = PolarizationStabilizationThread(self)

    def connect_hardware(self):
        # create connections to hardware
        hardware_settings = self._settings['hardware']
        self._servo = maestro.Controller(hardware_settings['serial_port_maestro'])
        self.beam_block_IR = maestro.BeamBlock(self._servo, hardware_settings['channel_beam_block_IR'])
        self.beam_block_Green = maestro.BeamBlock(self._servo, hardware_settings['channel_beam_block_Green'])
        self.filterwheel = maestro.FilterWheel(self._servo, **hardware_settings['parameters_filterwheel'])

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

    def connect_controls(self):
        # =============================================================
        # ===== LINK WIDGETS TO FUNCTIONS =============================
        # =============================================================

        # link slider to functions
        print(self.servo_polarization.get_position() * 100)
        self.sliderPosition.setValue(int(self.servo_polarization.get_position() * 100))
        self.sliderPosition.valueChanged.connect(lambda: self.set_position())

        # link buttons to functions
        self.btn_start_record.clicked.connect(lambda: self.record())
        self.btn_stop_record.clicked.connect(lambda: self.record())
        self.btn_clear_record.clicked.connect(lambda: self.record())
        self.btn_start_record_fpga.clicked.connect(lambda: self.record())

        self.btn_plus.clicked.connect(lambda: self.set_position())
        self.btn_minus.clicked.connect(lambda: self.set_position())
        self.btn_center.clicked.connect(lambda: self.set_position())
        self.btn_to_zero.clicked.connect(lambda: self.set_position())


        self.btn_apply_settings.clicked.connect(lambda: self.apply_settings())
        # link checkboxes to functions
        self.checkIRon.stateChanged.connect(lambda: self.control_light())
        self.checkGreenon.stateChanged.connect(lambda: self.control_light())
        self.checkPIActive.stateChanged.connect(lambda: self.switch_PI_loop())

        # link combo box
        self.cmb_filterwheel.addItems(self._settings['hardware']['parameters_filterwheel']['position_list'].keys())
        self.cmb_filterwheel.currentIndexChanged.connect(lambda: self.control_light())


        self.treeWidget.itemChanged.connect(lambda: self.update_parameters())

    def __del__(self):
        '''
        Cleans up connections
        '''
        self._thread_acq.stop()

        self.fpga.stop()

    def apply_settings(self):

        parameters_Acq = self._settings["parameters_PI"]
        gains = parameters_Acq['gains']
        print(gains)
        # assert self._gains['proportional'].isnumeric(), "proportional gain not a valid number"
        # assert self._gains['integral'].isnumeric(), "integral gain not a valid number"

        # self.FPGA_PI.gains = self._gains

        self.log("applied new gains {:0.3f}, {:0.3f}" .format(gains['proportional'],gains['integral']),1000)

    def update_parameters(self):
        '''
        is called when a parameter in the tree is changed
        this function updates the dictionary that holds all the parameter
        :return:
        '''
        print(self.treeWidget.currentItem())
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
                print(parents)
                dictator = self._settings
                for i in parents:
                    print i
                    dictator = dictator[i]
                value_old = dictator[parameter]

                dictator = settings_dict
                for i in parents:
                    print i
                    dictator = dictator[i]
                value_default = dictator[parameter]
                print("parameter_type", type(value_default))

                if isinstance(value_default, int):
                    value = int(value)
                elif isinstance(value_default, float):
                    value = float(value)
                else:
                    print("WARNING, TYPE NOT RECOGNIZED!!!!")
                dictator.update({parameter : value})

                # self._settings.update({parameter : float(value)})
                self.log("changed {:s} from {:s} to {:s}".format(parameter, str(value_old), str(value)))
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise


    def assert_parameters(self, parameter, value):
        '''
        asserts if the parameter has a the right value type and range
        :param parameter: name of parameter
        :param value: value of parameter
        :return: True or False
        '''
        # if parameter in {"channel_beam_block_IR", "channel_beam_block_Green", "channel", 'ND1.0', 'LP', 'ND2.0', "detector_threshold" }:
#
#
# "channel_beam_block_IR", "channel_beam_block_Green", "channel"
# range 0-5
#
# 'ND1.0',
# 'LP'
# 'ND2.0'
# 64-3232
#
# "record_length"
#
# "sample_period_PI"
# 'proportional'
# 'integral'
#
# "sample_period_acq"
# "data_length"
#
# "block_size"
#
# "setpoint", "piezo"
#
# "detector_threshold"



    def update_status(self, progress):
        self.progressBar.setValue(progress)
        if progress == 100:
            self.update_plot_fifo()

    def update_plot_live(self, data_point):
        if data_point > 2**15:
            self._recorded_data.append(data_point-2**16)
        else:
            self._recorded_data.append(data_point)
        if len(self._recorded_data) > self._settings["record_length"]:
            self._recorded_data.popleft()
        self.axes_live.clear()
        self.axes_live.plot(list(self._recorded_data))
        detector_threshold = self._settings["detector_threshold"]
        self.axes_live.plot([0, self._settings["record_length"]], [detector_threshold, detector_threshold], 'k--')
        self.axes_live.plot([0, self._settings["record_length"]], [-detector_threshold, -detector_threshold], 'k--')

        self.canvas_live.draw()

        self.lbl_detector_signal.setText("{:d}".format(self._recorded_data[-1]))

    def update_plot_fifo(self):


        data_length = len(np.array(self._fifo_data).flatten())
        print("===>> len data", data_length)
        time_step = int(self._settings["parameters_Acq"]["sample_period_acq"]) / 40e6
        freq_step = 1/(time_step * data_length)

        self.axes_timetrace.clear()
        times = 1e3 * np.linspace(0,time_step,data_length)
        self.axes_timetrace.plot(times, np.array(self._fifo_data).flatten())

        self.canvas_timetrace.draw()
        self.log("FIFO acq. completed",1000)

        # calculate PSD and plot


        freqs = np.linspace(0,freq_step * data_length / 2,data_length/2)

        self.data_PSD = np.abs(np.fft.fft(np.array(self._fifo_data).flatten()))**2
        self.data_PSD = self.data_PSD[range(data_length/2)]

        self.axes_psd.clear()
        self.axes_psd.loglog(freqs, self.data_PSD)
        self.axes_psd.set_xlabel('frequency (Hz)')
        self.canvas_psd.draw()

    def log(self, msg, wait_time = 1000):
        self.statusbar.showMessage(msg, wait_time)
        time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        self.past_commands.append("{:s}\t {:s}".format(time, msg))
        if len(self.past_commands) > 10:
            self.past_commands.popleft()


        print time
        model = QtGui.QStandardItemModel(self.listView)
        for item in self.past_commands:
            model.appendRow(QtGui.QStandardItem(item))
        self.listView.setModel(model)
        self.listView.show()

    def clear_plot(self):
        self._recorded_data.clear()
        self.axes_live.clear()
        self.canvas_live.draw()
        self.log("Cleared Data",1000)


    def record(self):
        sender = self.sender()
        # self.statusBar().showMessage(sender.objectName() + ' was pressed')
        if sender.objectName() == "btn_start_record":
            self._thread_acq.start()
        elif sender.objectName() == "btn_stop_record":
            self._thread_acq.stop()
        elif sender.objectName() == "btn_clear_record":
            self.clear_plot()
        elif sender.objectName() == "btn_start_record_fpga":
            # define variables and datasets
            # parameters_Acq = self._settings["parameters_Acq"]
            # number_of_reads = np.ceil(1.0 * int(parameters_Acq['data_length']) / int(parameters_Acq['block_size']))
            # block_size = parameters_Acq['block_size']
            # self.elements_left = np.ones(number_of_reads)

            # self.FPGA_READ_FIFO.data_length = int(self._settings['parameters_Acq']['block_size'])
            # self.FPGA_READ_FIFO.data_length = int(self._settings['parameters_Acq']['data_length'])
            self._thread_acq_fifo.start()
        else:
            print('unknown sender: ', sender.objectName())


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
                child.setFlags(child.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)


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
        detector_threshold = settings_dict["detector_threshold"]

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
            self.updateProgress.emit(data_point)
            time.sleep(0.1)
            # exept:

        print("acquisition ended")
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
            print(i)
            fifo_data =self._FPGA_READ_FIFO.data_queue.get()
            self.data.append(np.array(fifo_data[0]))
            self.elements_left[i] = int(fifo_data[2])
            print(fifo_data[2])
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



# class SettingsTree(QtGui.QTreeWidget):
#
#     def __init__(self, parent = None):
#         super(SettingsTree, self).__init__(parent)
#         self.setColumnCount(1)
#         self.setHeaderLabel("Settings")
#         self.settings = settings_dict
#         self.style()
#         self.fill_widget(self.settings)
#
#     def fill_widget(self, value):
#
#         def fill_item(item, value):
#             item.setExpanded(True)
#             if type(value) is dict:
#                 for key, val in sorted(value.iteritems()):
#                     child = QTreeWidgetItem()
#                     child.setText(0, unicode(key))
#                     item.addChild(child)
#                     fill_item(child, val)
#             elif type(value) is list:
#                 for val in value:
#                     child = QTreeWidgetItem()
#                     item.addChild(child)
#                 if type(val) is dict:
#                     child.setText(0, '[dict]')
#                     fill_item(child, val)
#                 elif type(val) is list:
#                     child.setText(0, '[list]')
#                     fill_item(child, val)
#                 else:
#                     child.setText(0, unicode(val))
#                 child.setExpanded(True)
#
#                 child.setFlags(Qt.ItemIsSelectable |Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)
#
#             else:
#                 child = QTreeWidgetItem()
#                 child.setText(0, unicode(value))
#                 item.addChild(child)
#                 child.setFlags(Qt.ItemIsSelectable |Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable)
#
#         self.clear()
#         fill_item(self.invisibleRootItem(), value)



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
