"""
Basic gui class designed with QT designer
"""
import sip
sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
from src.core import Parameter, Instrument, B26QTreeItem, ReadProbes, QThreadWrapper
import os.path
import numpy as np
import json as json
import yaml # we use this to load json files, yaml doesn't cast everything to unicode
from PySide.QtCore import QThread

# from src.instruments import DummyInstrument
# from src.scripts import ScriptDummy, ScriptDummyWithQtSignal

import datetime
from collections import deque

from src.core import load_probes, load_scripts, load_instruments

from src.scripts import ZISweeper, ZISweeperHighResolution, KeysightGetSpectrum, KeysightSpectrumVsPower, GalvoScan
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
            print('loading from file {:s}'.format(args[0]))
            instruments, scripts, probes = self.load_settings(args[0])
        elif len(args) == 3:
            instruments, scripts, probes = args
        else:
            raise TypeError("called ControlMainWindow with wrong arguments")

        instruments = load_instruments(instruments)
        scripts = load_scripts(scripts, instruments, log_function= lambda x: self.log(x, target = 'script'))
        probes = load_probes(probes, instruments)

        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        self.instruments = instruments
        self.scripts = scripts
        self.probes = probes

        self.read_probes = ReadProbes(self.probes)
        # self.read_probes.updateProgress.connect(self.update_probes)

        # define data container
        self.history = deque(maxlen=500)  # history of executed commands
        self.history_model = QtGui.QStandardItemModel(self.list_history)
        self.list_history.setModel(self.history_model)
        self.list_history.show()

        self.script_model = QtGui.QStandardItemModel(self.list_scripts)
        self.list_scripts.setModel(self.script_model)
        self.list_scripts.show()


        # fill the trees
        self.fill_tree(self.tree_settings, self.instruments)
        self.tree_settings.setColumnWidth(0, 300)

        self.fill_tree(self.tree_scripts, self.scripts)
        self.tree_scripts.setColumnWidth(0, 300)



        # self.fill_tree(self.tree_monitor, self.probes)
        self.tree_monitor.setColumnWidth(0, 300)
        self.tree_monitor.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        # self.tree_monitor.setDisabled(True)


        self.current_script = None
        self.probe_to_plot = None

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
            self.btn_plot_script.clicked.connect(lambda: self.btn_clicked())
            self.btn_plot_probe.clicked.connect(lambda: self.btn_clicked())

            self.btn_save_gui.clicked.connect(lambda: self.btn_clicked())
            self.btn_load_gui.clicked.connect(lambda: self.btn_clicked())

            # tree structures
            self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts))
            self.tree_settings.itemChanged.connect(lambda: self.update_parameters(self.tree_settings))
            self.tabWidget.currentChanged.connect(lambda : self.switch_tab())

            self.tree_settings.itemExpanded.connect(lambda: self.refresh_instruments())

            # plots
            self.matplotlibwidget.mpl_connect('button_press_event',  self.plot_clicked)
            self.matplotlibwidget_2.mpl_connect('button_press_event',  self.plot_clicked)

        connect_controls()

    def switch_tab(self):
        current_tab = str(self.tabWidget.tabText(self.tabWidget.currentIndex()))
        if current_tab == 'Monitor':
            self.read_probes.start()
            self.read_probes.updateProgress.connect(self.update_probes)
        else:
            try:
                self.read_probes.updateProgress.disconnect()
                self.read_probes.stop()
            except RuntimeError:
                pass
        if current_tab == 'Scripts':
            # rebuild script- tree because intruments might have changed
            self.tree_scripts.itemChanged.disconnect()
            self.fill_tree(self.tree_scripts, self.scripts)
            self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts))

    def refresh_instruments(self):
        """
        if self.tree_settings has been expanded, ask instruments for their actual values
        """
        def update(item):
            if item.isExpanded():
                for index in range(item.childCount()):
                    child = item.child(index)

                    if child.childCount() == 0:
                        instrument, path_to_instrument = child.get_instrument()
                        path_to_instrument.reverse()
                        value = instrument.settings
                        for elem in path_to_instrument:
                            value = value[elem]
                        print('{:s}:\t {:s} |\t {:s}'.format(child.name, str(child.value), str(value)))
                    else:
                        update(child)


        print('---- updating instruments (compare values from instr to values in tree) ----')
        for index in range(self.tree_settings.topLevelItemCount()):
            instrument = self.tree_settings.topLevelItem(index)
            update(instrument)
    def plot_clicked(self, mouse_event):
        item = self.tree_scripts.currentItem()

        if item is not None:

            if item.is_point():
                item_x = item.child(1)
                if mouse_event.xdata is not None:
                    self.tree_scripts.setCurrentItem(item_x)
                    item_x.value = float(mouse_event.xdata)
                    item_x.setText(1, '{:0.3f}'.format(float(mouse_event.xdata)))
                item_y = item.child(0)
                if mouse_event.ydata is not None:
                    self.tree_scripts.setCurrentItem(item_y)
                    item_y.value = float(mouse_event.ydata)
                    item_y.setText(1, '{:0.3f}'.format(float(mouse_event.ydata)))

                # focus back on item
                self.tree_scripts.setCurrentItem(item)
            else:
                if item.parent() is not None:
                    if item.parent().is_point():
                        if item == item.parent().child(1):
                            if mouse_event.xdata is not None:
                                item.setData(1, 2, float(mouse_event.xdata))
                        if item == item.parent().child(0):
                            if mouse_event.ydata is not None:
                                item.setData(1, 2, float(mouse_event.ydata))

    def get_time(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    def log(self, msg, target = 'hist'):

        time = self.get_time()

        msg = "{:s}\t {:s}".format(time, msg)

        if target == 'script':
            self.script_model.insertRow(0,QtGui.QStandardItem(msg))

        self.history.append(msg)
        self.history_model.insertRow(0,QtGui.QStandardItem(msg))


    def btn_clicked(self):
        sender = self.sender()
        self.probe_to_plot = None

        if sender is self.btn_start_script:
            item = self.tree_scripts.currentItem()

            if item is not None:
                script, path_to_script = item.get_script()
                # # is the script is a QThread object we connect its signals to the update_status function
                # if isinstance(script, QThread):
                #     script.updateProgress.connect(self.update_status)
                #     self.current_script = script
                #     script.start()
                # else:
                #     # non QThread script don't have a start function so we call .run() directly
                #     script.run()

                self.log('start {:s}'.format(script.name))
                # is the script is not a QThread object we use the wrapper QtSCript
                # to but it on a separate thread such that the gui remains responsive
                if not isinstance(script, QThread):
                    script = QThreadWrapper(script)

                script.updateProgress.connect(self.update_status)
                self.current_script = script
                script.start()


            else:
                self.log('No script selected. Select script and try again!')
        elif sender is self.btn_plot_script:
            item = self.tree_scripts.currentItem()

            if item is not None:
                script, path_to_script = item.get_script()
                # is the script is a QThread object we connect its signals to the update_status function
                script.plot(self.matplotlibwidget.axes)
                self.matplotlibwidget.draw()
        elif sender is self.btn_plot_probe:
            item = self.tree_monitor.currentItem()

            if item is not None:
                self.probe_to_plot = self.probes[item.name]
            else:
                self.log('Can\'t plot, No probe selected. Select probe and try again!')

        elif sender is self.btn_save_gui:

            # get filename
            fname = QtGui.QFileDialog.getSaveFileName(self, 'Save gui settings to file', 'Z:\\Lab\\Cantilever\\Measurements')# filter = '.b26gui'
            self.save_settings(fname)
        elif sender is self.btn_load_gui:

            # get filename
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Load gui settings from file', 'Z:\\Lab\\Cantilever\\Measurements')
            self.load_settings(fname)

    def load_settings(self, in_file_name):
        """
        loads a old_gui settings file (a json dictionary)
        - path_to_file: path to file that contains the dictionary

        Returns:
            - instruments: depth 1 dictionary where keys are instrument names and values are instances of instruments
            - scripts:  depth 1 dictionary where keys are script names and values are instances of scripts
            - probes: depth 1 dictionary where to be decided....?
        """

        assert os.path.isfile(in_file_name)

        with open(in_file_name, 'r') as infile:
            in_data = yaml.safe_load(infile)

        instruments = in_data['instruments']
        scripts = in_data['scripts']
        probes = in_data['probes']

        return instruments, scripts, probes

    def save_settings(self, out_file_name):
        """
        saves a old_gui settings file (to a json dictionary)
        - path_to_file: path to file that will contain the dictionary
        """


        print('saving', out_file_name)

        out_data = {'instruments':{}, 'scripts':{}, 'probes':{}}

        for instrument in self.instruments.itervalues():

            out_data['instruments'].update(instrument.to_dict())

        for script in self.scripts.itervalues():
            out_data['scripts'].update(script.to_dict())

        for probe in self.probes.itervalues():
            out_data['probes'].update(probe.to_dict())

        with open(out_file_name, 'w') as outfile:
            tmp = json.dump(out_data, outfile, indent=4)

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
                msg = "changed parameter {:s} from {:s} to {:s} on {:s}".format(item.name, str(old_value),
                                                                                str(new_value), instrument.name)
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
                msg = "changed parameter {:s} from {:s} to {:s} on {:s}".format(item.name, str(old_value),
                                                                                str(new_value),
                                                                                script.name)
            else:
                msg = "did not change parameter {:s} on {:s}".format(item.name, script.name)

            self.log(msg)

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

        if isinstance(script, (ZISweeper, ZISweeperHighResolution, KeysightGetSpectrum, KeysightSpectrumVsPower, GalvoScan)):
            if script.data:
                script.plot(self.matplotlibwidget.axes)
                self.matplotlibwidget.draw()

    def update_probes(self, progress):
        """
        update the probe monitor tree
        """

        new_values = self.read_probes.probes_values
        probe_count = len(self.read_probes.probes)

        if probe_count > self.tree_monitor.topLevelItemCount():
            # when run for the first time, there are no probes in the tree, so we have to fill it first
            self.fill_tree(self.tree_monitor, self.read_probes.probes_values)
        else:
            for x in range(0 , probe_count):
                topLvlItem = self.tree_monitor.topLevelItem(x)
                topLvlItem.value = new_values[topLvlItem.name]
                topLvlItem.setText(1, unicode(topLvlItem.value))
        if self.probe_to_plot is not None:
            self.probe_to_plot.plot(self.matplotlibwidget.axes)
            self.matplotlibwidget.draw()


        if self.chk_probe_log.isChecked():
            file_name  = str(self.txt_probe_log_path.text())
            if os.path.isfile(file_name) == False:
                outfile = open(file_name, 'w')
                outfile.write("{:s}\n".format(",".join(new_values.keys())))
            else:
                outfile = open(file_name, 'a')
            outfile.write("{:s}\n".format(",".join(map(str, new_values.values()))))




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

