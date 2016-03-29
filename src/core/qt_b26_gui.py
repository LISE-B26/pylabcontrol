"""
Basic gui class designed with QT designer
"""
import sip
sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
from src.core import Parameter, Instrument, B26QTreeItem, ReadProbes
import os.path
import numpy as np

from PySide.QtCore import QThread

from src.instruments import DummyInstrument
from src.scripts import ScriptDummy, ScriptDummyWithQtSignal

import datetime
from collections import deque

from src.core import load_probes, load_scripts, load_instruments

from src.scripts import ZISweeper, ZISweeperHighResolution
from src.core.plotting import plot_psd


# load the basic old_gui either from .ui file or from precompiled .py file
try:
    # import external_modules.matplotlibwidget
    Ui_MainWindow, QMainWindow = loadUiType('basic_application_window.ui') # with this we don't have to convert the .ui file into a python file!
except (ImportError, IOError):
    # load precompiled old_gui, to complite run pyqt_uic basic_application_window.ui -o basic_application_window.py
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
            - settings_file is the path to a json file that contains all the settings for the old_gui

        Returns:

        """
        if len(args) == 1:
            instruments, scripts, probes = self.load_settings(args[0])
        elif len(args) == 3:
            instruments, scripts, probes = args

            instruments = load_instruments(instruments)
            scripts = load_scripts(scripts, instruments)
            probes = load_probes(probes, instruments)
        else:
            raise TypeError("called ControlMainWindow with wrong arguments")

        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self.instruments = instruments
        self.scripts = scripts
        self.probes = probes

        self.read_probes = ReadProbes(self.probes)
        self.read_probes.updateProgress.connect(self.update_probes)

        # define data container
        self.history = deque()  # history of executed commands


        # fill the trees
        self.fill_tree(self.tree_settings, self.instruments)
        self.tree_settings.setColumnWidth(0, 300)

        self.fill_tree(self.tree_scripts, self.scripts)
        self.tree_scripts.setColumnWidth(0, 300)



        # self.fill_tree(self.tree_monitor, self.probes)
        self.tree_monitor.setColumnWidth(0, 300)
        self.tree_monitor.setDisabled(True)


        self.current_script = None

        def connect_controls():
            # =============================================================
            # ===== LINK WIDGETS TO FUNCTIONS =============================
            # =============================================================

            # link slider to old_functions
            #
            # self.sliderPosition.setValue(int(self.servo_polarization.get_position() * 100))
            # self.sliderPosition.valueChanged.connect(lambda: self.set_position())




            # link buttons to old_functions
            self.btn_start_script.clicked.connect(lambda: self.btn_clicked())
            self.btn_stop_script.clicked.connect(lambda: self.btn_clicked())

            self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts))
            self.tree_settings.itemChanged.connect(lambda: self.update_parameters(self.tree_settings))
            self.tabWidget.currentChanged.connect(lambda : self.switch_tab())

        connect_controls()

    def switch_tab(self):
        current_tab = str(self.tabWidget.tabText(self.tabWidget.currentIndex()))
        if current_tab == 'Monitor':
            self.read_probes.start()
        else:
            self.read_probes.stop()

        if current_tab == 'Scripts':
            # rebuild script- tree because intruments might have changed
            self.tree_scripts.itemChanged.disconnect()
            self.fill_tree(self.tree_scripts, self.scripts)
            self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts))




    def update_parameters(self, treeWidget):

        if treeWidget == self.tree_settings:

            item = treeWidget.currentItem()

            instrument, path_to_instrument = item.get_instrument()

            # build nested dictionary to update instrument
            dictator = item.value
            for element in path_to_instrument:
                dictator = {element: dictator}

            # get old value from instrument
            old_value = instrument.settings
            path_to_instrument.reverse()
            for element in path_to_instrument:
                old_value = old_value[element]

            # send new value from tree to instrument
            instrument.update(dictator)


            new_value = item.value
            if new_value is not old_value:
                msg = "changed parameter {:s} from {:s} to {:s} on {:s}".format(item.name, str(old_value), str(new_value), instrument.name)
            else:
                msg = "did not change parameter {:s} on {:s}".format(item.name, instrument.name)

            self.log(msg)
        elif treeWidget == self.tree_scripts:

            item = treeWidget.currentItem()

            script, path_to_script = item.get_script()

            # build nested dictionary to update instrument
            dictator = item.value
            for element in path_to_script:
                dictator = {element: dictator}

            # get old value from instrument
            old_value = script.settings
            path_to_script.reverse()
            for element in path_to_script:
                old_value = old_value[element]

            # send new value from tree to script
            script.update(dictator)

            new_value = item.value
            if new_value is not old_value:
                msg = "changed parameter {:s} from {:s} to {:s} on {:s}".format(item.name, str(old_value), str(new_value),
                                                                                script.name)
            else:
                msg = "did not change parameter {:s} on {:s}".format(item.name, script.name)

            self.log(msg)

    def get_time(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    def log(self, msg, wait_time = 5000):

        self.statusbar.showMessage(msg, wait_time)
        time = self.get_time()
        self.history.append("{:s}\t {:s}".format(time, msg))
        if len(self.history) > 10:
            self.history.popleft()

        model = QtGui.QStandardItemModel(self.list_history)
        for item in self.history:
            model.insertRow(0,QtGui.QStandardItem(item))

        self.list_history.setModel(model)
        self.list_history.show()


    def btn_clicked(self):
        sender = self.sender()


        if sender is self.btn_start_script:
            item = self.tree_scripts.currentItem()

            if item is not None:
                script, path_to_script = item.get_script()
                # is the script is a QThread object we connect its signals to the update_status function
                if isinstance(script, QThread):
                    script.updateProgress.connect(self.update_status)
                    self.current_script = script
                    script.start()
                else:
                    # non QThread script don't have a start function so we call .run() directly
                    script.run()
                self.log('start {:s}'.format(script.name))


            else:
                self.log('No script selected. Select script and try again!')

    def load_settings(self, path_to_file):
        """
        loads a old_gui settings file (a json dictionary)
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
        raise NotImplementedError

        return instruments, scripts, probes

    def save_settings(self, path_to_file):
        """
        saves a old_gui settings file (to a json dictionary)
        - path_to_file: path to file that will contain the dictionary
        """
        # todo: implement
        raise NotImplementedError


    def update_status(self, progress):
        """
        waits for a signal emitted from a thread and updates the gui
        Args:
            progress:

        Returns:

        """
        self.progressBar.setValue(progress)
        if progress == 100:
            pass
        script = self.current_script

        if isinstance(script, (ZISweeper, ZISweeperHighResolution)):
            if script.data:
                script.plot(self.matplotlibwidget.axes)
                self.matplotlibwidget.draw()

    def update_probes(self, progress):
        self.fill_tree(self.tree_monitor, self.read_probes.probes_values)


    def fill_tree(self, tree, parameters):
        """
        fills a tree with nested parameters
        Args:
            tree: QtGui.QTreeWidget
            parameters: dictionary or Parameter object

        Returns:

        """

        tree.clear()
        assert isinstance(parameters, (dict, Parameter))

        for key, value in parameters.iteritems():
            if isinstance(value, Parameter):
                B26QTreeItem(tree, key, value, parameters.valid_values[key], parameters.info[key])
            else:
                B26QTreeItem(tree, key, value, type(value), '')


