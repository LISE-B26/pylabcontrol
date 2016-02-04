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

Ui_MainWindow, QMainWindow = loadUiType('mainwindow.ui') # with this we don't have to convert the .ui file into a python file!


from collections import deque
import numpy as np
import lib.FPGA_PID_Loop_Simple as NI
import time
import threading
import Queue as queue

# ============= GENERAL SETTING ====================================
# ==================================================================
settings = {
    "serial_port_maestro" : "COM5",
    "channel_beam_block_IR" : 4,
    "record_length" : 10,
    "parameters_PI" : {
        "sample_period_PI" :4e5,
        "gains" : {'proportional': 1.0, 'integral':0.1},
        "setpoint" : 0,
        "piezo" : 0
    },
    "kinesis_serial_number" : 83832028
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


class AcquisitionThread(QtCore.QThread):

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(int)

    #You can do any extra things in this init you need
    def __init__(self, PI):
        """

        :param PI: lib.FPGA_PID_Loop_Simple.NI_FPGA_PI object that handles the feedback loop
        :return:
        """
        self._recording = False
        self._PI = PI
        QtCore.QThread.__init__(self)

    #A QThread is run by calling it's start() function, which calls this run()
    #function in it's own "thread".
    def run(self):
        self._recording = True

        while self._recording:
            #Emit the signal so it can be received on the UI side.
            # data_point = np.random.randint(-32000, 32000)
            data_point = self._PI.detector
            self.updateProgress.emit(data_point)
            time.sleep(0.1)

        print("acquisition ended")
    def stop(self):
        self._recording = False

class PolarizationControlThread(QtCore.QThread):

    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = QtCore.Signal(float)

    #You can do any extra things in this init you need
    def __init__(self, servo):
        """

        :param servo: Kinsesis Servo controler object that controls the polarization
        :return:
        """
        self._running = False
        self._servo = servo
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
            #Emit the signal so it can be received on the UI side.
            self._servo.move_servo(self.target_position)
            time.sleep(0.1)
            actual_position = self._servo.get_position()
            self.updateProgress.emit(actual_position)
            if abs(self.target_position - actual_position)<0.01:
                self._running = False
            print(abs(self.target_position - actual_position))


        print("position reached")



class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self._recorded_data = deque()


        # =============================================================
        # ===== NI FPGA ===============================================
        # =============================================================
        # connect to FPGA and start it
        fpga = NI.NI7845R()
        fpga.start()

        # create PI (proportional integral) controler object
        PI = NI.NI_FPGA_PI(fpga, **settings["parameters_PI"])

        # fill the empty widget with a figure
        fig = Figure()
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.axes = fig.add_subplot(111)


        # ============================================================
        # ====== POLARIZATION CONTROL ================================

        servo_polarization = DCServo_Kinesis.TDC001(settings["kinesis_serial_number"])



        # ============= threading ====================================
        # create thread instance
        self._thread_acq = AcquisitionThread(PI)
        # connect emitted signal from the thread to update_plot function
        self._thread_acq.updateProgress.connect(self.update_plot)
        # self._acquisition.updateProgress.connect(lambda: self.update_plot())
        self._thread_pol = PolarizationControlThread(servo_polarization)
        # connect emitted signal from the thread to update_plot function
        self._thread_pol.updateProgress.connect(self.update_position)


        # =============================================================
        # ===== LINK WIDGETS TO FUNCTIONS =============================
        # =============================================================

        # link slider to functions
        print(servo_polarization.get_position() * 100)
        self.sliderPosition.setValue(int(servo_polarization.get_position() * 100))
        self.sliderPosition.valueChanged.connect(lambda: self.set_position(servo_polarization))

        # link buttons to functions
        self.btn_start_record.clicked.connect(lambda: self.record())
        self.btn_stop_record.clicked.connect(lambda: self.record())
        self.btn_clear_record.clicked.connect(lambda: self.record())

        # link checkboxes to functions
        self.checkIRon.stateChanged.connect(lambda: self.switch_IR())
        self.checkPIActive.stateChanged.connect(lambda: self.switch_PI_loop())

        # create connections to hardware
        self.settings = settings
        self._servo = maestro.Controller(self.settings['serial_port_maestro'])
        self.beam_block_IR = maestro.BeamBlock(self._servo, self.settings['channel_beam_block_IR'])

        # model = QtGui.QStandardItemModel(self.listView)
        # # self.listView.isWrapping = True
        # item = QtGui.QStandardItem()
        # item.setText('Item text')
        # model.appendRow(item)
        #
        # item2 = QtGui.QStandardItem()
        # item2.setText('Item text 2')
        # model.appendRow(item2)
        #
        # self.listView.setModel(model)
        # self.listView.show()

    def update_plot(self, data_point):
        if data_point > 2**15:
            self._recorded_data.append(data_point-2**16)
        else:
            self._recorded_data.append(data_point)
        if len(self._recorded_data) > settings["record_length"]:
            self._recorded_data.popleft()
        self.axes.clear()
        self.axes.plot(list(self._recorded_data))
        self.canvas.draw()
        self.statusbar.showMessage("Recording Data",1000)
        # print(data_point, data_point-2**16)

    def clear_plot(self):
        self._recorded_data.clear()
        self.axes.clear()
        self.canvas.draw()
        self.statusbar.showMessage("Cleared Data",1000)
    # def setProgress(self, progress):
    #     self.progressBar.setValue(progress)


    def record(self):
        sender = self.sender()
        # self.statusBar().showMessage(sender.objectName() + ' was pressed')
        if sender.objectName() == "btn_start_record":
            self._thread_acq.start()
        elif sender.objectName() == "btn_stop_record":
            self._thread_acq.stop()
        elif sender.objectName() == "btn_clear_record":
            self.clear_plot()


    def set_position(self, servo_polarization):
        value = 0.01 * self.sliderPosition.value() # slider max value 600 corresponding to 6mm
        self._thread_pol.target_position = value
        self._thread_pol.start()

    def update_position(self, value):
        print("position {:0.02f}".format(value))
        self.statusbar.showMessage("position {:0.02f}".format(value),1000)
        # servo_polarization.move_servo(value)
        # print(servo_polarization.get_position())

    #
    # def record_data(self, axes):
    #     print("called record")
    #     while self._recording:
    #         self._recorded_data.append(np.random.random())
    #         if len(self._recorded_data) > settings["record_length"]:
    #             self._recorded_data.popleft()
    #
    #         axes.clear()
    #         axes.plot(list(self._recorded_data))
    #         self.canvas.draw()
    #         # self.statusbar.showMessage("Recording Data",1000)
    #         print('ad')
    #         time.sleep(0.5)

    #
    # def addBatch2(self,text="test",iters=6,delay=0.3):
    #     for i in range(iters):
    #         time.sleep(delay) # artificial time delay
    #         self.emit( QtCore.SIGNAL('add(QString)'), text+" "+str(i) )

    # def start_record_data(self, axes):
    #     '''
    #     Changes script to be executed based on current text in box
    #     :param ApplicationWindow:
    #     '''
    #
    #     self.threadPool.append( GenericThread(self.addBatch2,"from generic thread using signal ",delay=0.3) )
    #     self.disconnect( self, QtCore.SIGNAL("add(QString)"), self.add )
    #     self.connect( self, QtCore.SIGNAL("add(QString)"), self.add )
    #     self.threadPool[len(self.threadPool)-1].start()

        # =============================================

        # print("start called record")
        # if self._recording  == False:
        #     self._recording = True
        #     self.thread = threading.Thread(target=self.record_data(axes))
        #     self.thread.start()
        # else:
        #     self.statusbar.showMessage("Data already recording",1000)

        # =============================
        # while self._recording:
            # self._recorded_data.append(np.random.random())
            # if len(self._recorded_data) > settings["record_length"]:
            #     self._recorded_data.popleft()
            #
            # axes.clear()
            # axes.plot(list(self._recorded_data))
            # self.canvas.draw()
            # self.statusbar.showMessage("Recording Data",1000)

            # time.sleep(0.5)
            # QtGui.QApplication.processEvents()

    # def stop_record_data(self, axes):
    #     '''
    #     Changes script to be executed based on current text in box
    #     :param ApplicationWindow:
    #     '''
    #
    #     # x = np.random.random(100)
    #     # axes.clear()
    #     # axes.plot(np.random.rand(5))
    #     # self.canvas.draw()
    #
    #     self._recording = False
    #     self.statusbar.showMessage("Stopped recording data",1000)
    # def clear_record_data(self, axes):
    #     self._recorded_data.clear()
    #     axes.clear()
    #     self.canvas.draw()
    #     self.statusbar.showMessage("Cleared Data",1000)

    def switch_IR(self):
        '''
        Changes script to be executed based on current text in box
        :param ApplicationWindow:
        '''


        status_IR = self.checkIRon.isChecked()

        if status_IR:
            self.beam_block_IR.open()
        else:
            self.beam_block_IR.block()

        self.statusbar.showMessage("IR laser {:s}".format(str(status_IR)),1000)

    def switch_PI_loop(self):
        '''
        Changes script to be executed based on current text in box
        :param ApplicationWindow:
        '''

        status_PI_loop =self.checkPIActive.isChecked()
        print(status_PI_loop)
        self.statusbar.showMessage("IR laser  {:s}".format(str(status_PI_loop)),1000)

    # def plot(self, canvas, axes):
    #     canvas.draw()
    #     axes.plot(np.random.rand(5))


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
