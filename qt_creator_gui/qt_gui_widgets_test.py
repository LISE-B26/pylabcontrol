
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
            # self.btn_start_record.clicked.connect(lambda: self.btn_clicked())
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
    def log(self, msg, wait_time = 1000):

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

    def update_parameters_old(self, treeWidget, parameter_dict):
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

    def update_parameters(self, treeWidget):

        # todo: catch changes from checkboxes and combos
        if not treeWidget.currentItem() == None:
            if treeWidget.currentColumn() == 0:
                self.log("Tried to edit parameter name. This is not allowed!!", 1000)
                # todo: following line is wrong: fix!
                self.fill_treeWidget(treeWidget, parameter_dict) # set tree back to status before it was edited by user
            else:
                if isinstance(treeWidget.currentItem(), QTreeParameter):
                    new_value = treeWidget.currentItem().text(1)
                    parameter = treeWidget.currentItem().parameter
                    # old_value = deepcopy(parameter.value)
                    old_value = parameter.value
                    parameter.value = new_value
                    # read the new value back from the actual parameter
                    new_value = parameter.value

                    new_value = str(treeWidget.currentItem().text(1))

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