"""
Basic gui class designed with QT designer
"""
import sip
sip.setapi('QVariant', 2)# set to version to so that the gui returns QString objects and not generic QVariants
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
from src.core import Parameter, Instrument, B26QTreeItem
import os.path

from src.instruments import DummyInstrument
from src.scripts import ScriptDummy

import datetime
from collections import deque

from src.core import load_probes, load_scripts, load_instruments

# load the basic gui either from .ui file or from precompiled .py file
try:
    # import external_modules.matplotlibwidget
    Ui_MainWindow, QMainWindow = loadUiType('basic_application_window.ui') # with this we don't have to convert the .ui file into a python file!
except (ImportError, IOError):
    # load precompiled gui, to complite run pyqt_uic basic_application_window.ui -o basic_application_window.py
    from src.core.basic_application_window import Ui_MainWindow
    from PyQt4.QtGui import QMainWindow
    print('Warning: on the fly conversion of .ui file failed, loaded .py file instead!!')



class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args):
        """

        ControlMainWindow(intruments, scripts, probes)
            - intruments: depth 1 dictionary where keys are instrument names and keys are instrument classes
            - scripts: depth 1 dictionary where keys are script names and keys are script classes
            - probes: depth 1 dictionary where to be decided....?

        ControlMainWindow(settings_file)
            - settings_file is the path to a json file that contains all the settings for the gui

        Returns:

        """

        print(args)
        if len(args) == 1:
            instruments, scripts, probes = self.load_settings(args[0])
        elif len(args) == 3:
            instruments, scripts, probes = args

            instruments = load_instruments(instruments)
            print('created instruments')
            print(instruments)
            scripts = load_scripts(scripts, instruments)
            print('created scripts')
            print(scripts)
            probes = load_probes(probes, instruments)
            print('created probes')
            print(probes)
        else:
            raise TypeError("called ControlMainWindow with wrong arguments")

        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self.instruments = instruments
        self.scripts = scripts
        self.probes = probes


        # define data container
        self.history = deque()  # history of executed commands


        # fill the trees
        self.fill_tree(self.tree_settings, self.instruments)
        self.tree_settings.setColumnWidth(0, 300)

        print('self.scripts', self.scripts)

        self.fill_tree(self.tree_scripts, self.scripts)
        self.tree_scripts.setColumnWidth(0, 300)

        # ========= old stuff =========

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
            # for script in self.scripts_old:
            #     if isinstance(script, QtScript):
            #         print(script.name)
            #         script.updateProgress.connect(self.update_progress)


        # self.instruments = {instrument.name: instrument  for instrument in self.instruments}
        # fill_tree(self.tree_settings, self.instruments)
        # self.tree_settings.setColumnWidth(0,300)
        #
        # self.tree_settings.itemChanged.connect(lambda: self.update_parameters(self.tree_settings))
        # ============ define probes / monitor ========================

        # ============ define scripts_old =================================


        #
        # # define parameters to monitor
        # zi_inst = get_elemet('ZiHF2', self.instrument_tests)
        # self.monitor_parameters = [
        #     {'target' : zi_inst, 'parameter' : get_elemet('freq', zi_inst.parameters)}
        # ]

        # define scripts_old
        # self.scripts_old = [
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


    def load_settings(self, path_to_file):
        """
        loads a gui settings file (a json dictionary)
        - path_to_file: path to file that contains the dictionary

        Returns:
            - instruments: depth 1 dictionary where keys are instrument names and values are instances of instruments
            - scripts:  depth 1 dictionary where keys are script names and values are instances of scripts
            - probes: depth 1 dictionary where to be decided....?
        """
        instruments = None
        scripts = None
        probes = None
        # todo: implement load settings from json file
        assert isinstance(path_to_file, str)

        assert os.path.isfile(path_to_file)
        print('loading from json file not supported yet!')
        raise TypeError

        return instruments, scripts, probes

    def save_settings(self, path_to_file):
        """
        saves a gui settings file (to a json dictionary)
        - path_to_file: path to file that will contain the dictionary
        """

        # todo: implement

    def fill_tree(self, tree, parameters):
        """
        fills a tree with nested parameters
        Args:
            tree: QtGui.QTreeWidget
            parameters: dictionary or Parameter object

        Returns:

        """
        assert isinstance(parameters, (dict, Parameter))

        for key, value in parameters.iteritems():
            if isinstance(value, Parameter):
                B26QTreeItem(tree, key, value, parameters.valid_values[key], parameters.info[key])
            else:
                B26QTreeItem(tree, key, value, type(value), '')

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)



    instruments = {'inst_dummy': 'DummyInstrument'}

    scripts= {


        'counter': 'ScriptDummy',


        'dummy script with inst': {
            'script_class': 'ScriptDummyWithInstrument',
            'instruments': {'dummy_instrument': 'inst_dummy'}
        }

        # 'new_script': 'NewScript',

        # 'new_script_with_inst': {
        #     "script_class" :'NewScriptWithInst',
        #     # "instruments": {"inst1": "Inst1", ..}
        # }



    }

    # {"zihf2": "ZIHF2", "inst": 'INST'} => param = {"zihf2": &ZIHF2, 'inst': &sacbs;}

    # Zi_Sweeper(*param)

    probes = {'probe 1', 'something', 'probe 2', 'something else'}

    # ex = ControlMainWindow('path....')
    ex = ControlMainWindow(instruments, scripts, probes)
    ex.show()
    ex.raise_()
    sys.exit(app.exec_())

    # instruments = load_instruments(instruments)
    # print('created instruments')
    # print(instruments)
    # scripts = load_scripts(scripts, instruments)
    # print('created scripts')
    # print(scripts['counter'].settings)
