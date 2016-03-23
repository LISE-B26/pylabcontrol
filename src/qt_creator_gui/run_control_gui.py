"""
New gui with new parameter and instrument class and GUI designed with QT designer
"""
import sip
sip.setapi('QVariant', 2)# set to version to so that the gui returns QString objects and not generic QVariants
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
from src.core import Parameter, Instrument
from src.core.qt_widgets import fill_tree


from src.instruments import MaestroBeamBlock, MaestroController, ZIHF2

# from src.core.scripts import *

INSTRUMENTS = []



import datetime
from collections import deque
# from src.qt_creator_gui import QTreeInstrument, QTreeScript, QTreeParameter


# todo: try to complie .ui file if if doesn't exist or can't be compliled load precompiled .py file
try:
    Ui_MainWindow, QMainWindow = loadUiType('zi_control.ui') # with this we don't have to convert the .ui file into a python file!
except:
    raise
# from src.qt_creator_gui.zi_control import Ui_MainWindow



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

            #
            # for script in self.scripts:
            #     if isinstance(script, QtScript):
            #         print(script.name)
            #         script.updateProgress.connect(self.update_progress)

        # define data container
        self.past_commands = deque() # history of executed commands

        # ============ define instruments ==========================
        # maestro = MaestroController('maestro 6 channels')
        self.instruments = [
            ZIHF2('ZiHF2'),
            # MaestroBeamBlock(maestro,'IR beam block')
        ]


        self.instruments = {instrument.name: instrument  for instrument in self.instruments}
        fill_tree(self.tree_settings, self.instruments)
        self.tree_settings.setColumnWidth(0,300)

        self.tree_settings.itemChanged.connect(lambda: self.update_parameters(self.tree_settings))
        # ============ define probes / monitor ========================

        # ============ define scripts =================================


        #
        # # define parameters to monitor
        # zi_inst = get_elemet('ZiHF2', self.instrument_tests)
        # self.monitor_parameters = [
        #     {'target' : zi_inst, 'parameter' : get_elemet('freq', zi_inst.parameters)}
        # ]

        # define scripts
        # self.scripts = [
        #     Script_Dummy('script dummy 1'),
        #     QtScript('threaded script')
        # ]

        # # fill the trees
        # self.fill_treewidget(self.tree_scripts)
        # self.tree_scripts.setColumnWidth(0,200)
        #
        # self.fill_treewidget(self.tree_settings)
        # self.tree_settings.setColumnWidth(0,200)

        # self.fill_treewidget(self.tree_monitor)
        # self.tree_monitor.setColumnWidth(0,200)

        # connect_controls()

    def update_parameters(self, treeWidget):

        if treeWidget == self.tree_settings:

            item = treeWidget.currentItem()

            current_item = item
            xx = []
            while not isinstance(current_item.value, Instrument):
                print(xx)
                xx.append(current_item.name)
                current_item = current_item.parent()
            print('ZZ', xx)

            old_value = ''
            new_value = item.value
            if new_value is not old_value:
                msg = "changed parameter {:s} from {:s} to {:s} on {:s}".format(item.name, str(old_value), str(new_value), item.target)
            else:
                msg = "did not change parameter {:s} on {:s}".format(item.name, item.target)

            self.log(msg)
            # print(treeWidget.currentItem(), treeWidget.currentItem().target)

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


    def update_progress_old(self, current_progress):
        self.progressBar.setValue(current_progress)
        if current_progress == 100:
            self.log('finished!!!')


    def btn_clicked_old(self):
        sender = self.sender()

        script = self.tree_scripts.currentItem()

        if script is not None:
            while isinstance(script, QTreeScript) == False:
                script = script.parent()
            script = script.script
            # self.statusBar().showMessage(sender.objectName() + ' was pressed')
            if sender.objectName() == "btn_start_script":
                # self._thread_acq.start()
                self.log('start {:s}'.format(script.name))
                script.run()
                if isinstance(script, Script):
                    self.log('finished')
            elif sender.objectName() == "btn_stop_script":
                self.log('stop {:s}'.format(script.name))
                script.stop()
            else:
                print('unknown sender: ', sender.objectName())
        else:
            self.log('No script selected. Select script and try again!')




        # self.log("parameter {:s} changed from {:s} to {:s}!".format(parameter.name, str(old_value), str(new_value)), 1000)
    def update_parameters_old(self, treeWidget):

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
                    # print('target',treeWidget.currentItem().target)
                    # print('parameter', treeWidget.currentItem().parameter)


                    # old_value = deepcopy(parameter.value)
                    old_value = parameter.value

                    # todo = this asignment doesn't work yet!!!
                    # parameter.value = new_value
                    # instead we have to use the following syntax
                    # if parameter belongs to an instrument, we update it
                    if isinstance(treeWidget.currentItem().target, Instrument):
                        # treeWidget.currentItem().target.update_parameters(Parameter(parameter.name, new_value))
                        print('xxxxx')
                        print(parameter.valid_values)
                        print(parameter.value)
                        print({parameter.name: new_value})
                        treeWidget.currentItem().target.update({parameter.name: new_value})
                        print( 'parameter ins' , parameter)
                    elif isinstance(treeWidget.currentItem().target, Script):
                        print( 'parameter script' , parameter)

                        print('xxxxx')
                        print(parameter.valid_values)
                        print(parameter.value)
                        print({parameter.name: new_value})

                        p = Parameter(parameter.name, new_value)
                        print(p)

                        treeWidget.currentItem().target.update(Parameter(parameter.name, new_value))

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

    def fill_treewidget_old(self, treeWidget):
        if treeWidget == self.tree_scripts:
            for elem in self.scripts:
                QTreeScript( self.tree_scripts, elem )

        elif treeWidget == self.tree_settings:
            for elem in self.instruments:
                QTreeInstrument( self.tree_settings, elem )
        elif treeWidget == self.tree_monitor:
            for elem in self.monitor_parameters:
                QTreeParameter( self.tree_monitor, elem['parameter'],  elem['target'])

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    ex = ControlMainWindow()
    ex.show()
    sys.exit(app.exec_())