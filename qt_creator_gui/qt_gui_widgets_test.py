
from PyQt4.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('zi_control.ui') # with this we don't have to convert the .ui file into a python file!
# from qt_creator_gui.zi_control import Ui_MainWindow

from hardware_modules.instruments import Instrument_Dummy, Maestro_Controller, ZIHF2, Maestro_BeamBlock
from scripts.scripts import Script_Dummy

from PyQt4 import QtCore, QtGui
import datetime
from collections import deque
from qt_creator_gui.qt_gui_widgets import QTreeInstrument, QTreeScript, QTreeParameter
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from copy import deepcopy
class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        def connect_controls():
            # =============================================================
            # ===== LINK WIDGETS TO FUNCTIONS =============================
            # =============================================================

            # link slider to functions
            #
            # self.sliderPosition.setValue(int(self.servo_polarization.get_position() * 100))
            # self.sliderPosition.valueChanged.connect(lambda: self.set_position())

            # link buttons to functions
            self.btn_start_script.clicked.connect(lambda: self.btn_clicked())
            self.btn_stop_script.clicked.connect(lambda: self.btn_clicked())
            # self.btn_clear_record.clicked.connect(lambda: self.btn_clicked())
            # self.btn_start_record_fpga.clicked.connect(lambda: self.btn_clicked())
            # self.btn_clear_record_fpga.clicked.connect(lambda: self.btn_clicked())
            # self.btn_save_to_disk.clicked.connect(lambda: self.btn_clicked())
            #
            # self.btn_plus.clicked.connect(lambda: self.set_position())
            # self.btn_minus.clicked.connect(lambda: self.set_position())
            # self.btn_center.clicked.connect(lambda: self.set_position())
            # self.btn_to_zero.clicked.connect(lambda: self.set_position())



            # link checkboxes to functions
            # self.checkIRon.stateChanged.connect(lambda: self.control_light())
            # self.checkGreenon.stateChanged.connect(lambda: self.control_light())
            # self.checkWhiteLighton.stateChanged.connect(lambda: self.control_light())
            # self.checkCameraon.stateChanged.connect(lambda: self.control_light())
            # self.checkPIActive.stateChanged.connect(lambda: self.switch_PI_loop())

            # link combo box
            # self.cmb_filterwheel.addItems(self._settings['hardware']['parameters_filterwheel']['position_list'].keys())
            # self.cmb_filterwheel.currentIndexChanged.connect(lambda: self.control_light())

            self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts))
            self.tree_settings.itemChanged.connect(lambda: self.update_parameters(self.tree_settings))

        # define data container
        self.past_commands = deque() # history of executed commands

        # define instruments
        maestro = Maestro_Controller('maestro 6 channels')
        self.instruments = [
            ZIHF2('ZiHF2',{'freq': 10.0}),
            Maestro_BeamBlock(maestro,'IR beam block')
        ]

        # define scripts
        self.scripts = [
            Script_Dummy('script dummy 1')
        ]

        # fill the trees

        self.fill_treewidget(self.tree_scripts)
        self.tree_scripts.setColumnWidth(0,200)

        self.fill_treewidget(self.tree_settings)
        self.tree_settings.setColumnWidth(0,200)

        self.fill_treewidget(self.tree_monitor)
        self.tree_monitor.setColumnWidth(0,200)

        connect_controls()
    def get_time(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    def log(self, msg, wait_time = 5000):

        self.statusbar.showMessage(msg, wait_time)
        time = self.get_time()
        self.past_commands.append("{:s}\t {:s}".format(time, msg))
        if len(self.past_commands) > 10:
            self.past_commands.popleft()

        model = QtGui.QStandardItemModel(self.list_history)
        for item in self.past_commands:
            model.insertRow(0,QtGui.QStandardItem(item))

        self.list_history.setModel(model)
        self.list_history.show()

    def btn_clicked(self):
        sender = self.sender()

        script = self.tree_scripts.currentItem()
        x = 0
        while isinstance(script, QTreeScript) == False:
            print(script)
            x +=1
            script = script.parent()
            if x>5:
                exit


        # self.statusBar().showMessage(sender.objectName() + ' was pressed')
        if sender.objectName() == "btn_start_script":
            # self._thread_acq.start()
            self.log('start {:s}'.format(script))
        elif sender.objectName() == "btn_stop_script":
            self.log('stop {:s}'.format(script))
        else:
            print('unknown sender: ', sender.objectName())


    def update_parameters(self, treeWidget):

        # todo: catch changes from checkboxes and combos
        if not treeWidget.currentItem() == None:
            if treeWidget.currentColumn() == 0:
                self.log("Tried to edit parameter name. This is not allowed!!", 1000)
                # todo: following line is wrong: fix!
                self.fill_treeWidget(treeWidget, parameter_dict) # set tree back to status before it was edited by user
            else:
                if isinstance(treeWidget.currentItem(), QTreeParameter):
                    parameter = treeWidget.currentItem().parameter

                    if isinstance(parameter.valid_values, list):
                        new_value = treeWidget.currentItem().combobox.currentText()
                    elif parameter.valid_values is bool:
                        new_value = treeWidget.currentItem().check.checkState()
                        if new_value == int(2):
                            new_value = True
                        elif new_value == int(0):
                            new_value = False
                    elif isinstance(parameter.value, list):

                        print('list')
                    else:
                        new_value = treeWidget.currentItem().text(1)
                    print(treeWidget.currentItem())


                    # old_value = deepcopy(parameter.value)
                    old_value = parameter.value
                    parameter.value = new_value
                    # read the new value back from the actual parameter
                    new_value = parameter.value

                    # new_value = str(treeWidget.currentItem().text(1))

                    # self.log("Updated {:s} from {:s} to {:s}!!".format(element, str(value_old), str(value)), 1000)
                    self.log("parameter {:s} changed from {:s} to {:s}!".format(parameter.name, str(old_value), str(new_value)), 1000)
                # elif isinstance(treeWidget.currentItem(), QTreeScript):
                #     self.log("script .. changed!", 1000)
                # elif isinstance(treeWidget.currentItem(), QTreeInstrument):
                #     self.log("instrument .. changed!", 1000)
                # else:
                #     raise TypeError('Unknown item!!')

    def fill_treewidget(self, treeWidget):
        if treeWidget == self.tree_scripts:
            for elem in self.scripts:
                QTreeScript( self.tree_scripts, elem )

        elif treeWidget == self.tree_settings:
            for elem in self.instruments:
                QTreeInstrument( self.tree_settings, elem )
        elif treeWidget == self.tree_monitor:
             print('nothing to do....')

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    ex = ControlMainWindow()
    ex.show()
    sys.exit(app.exec_())