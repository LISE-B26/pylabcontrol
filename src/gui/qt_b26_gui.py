"""
Basic gui class designed with QT designer
"""
# import sip
# try:
#     import sip
#     sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
# except ValueError:
#     pass
from PyQt4 import QtGui, QtCore
from PyQt4.uic import loadUiType
from src.core import Parameter, Instrument, Script, ReadProbes, QThreadWrapper
from src.gui import B26QTreeItem
import os.path
import numpy as np
import json as json
from PySide.QtCore import QThread
from src.gui import LoadDialog
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as Canvas,
                                                NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import sys

import datetime
from collections import deque
# from src.core import instantiate_probes

#from src.scripts import KeysightGetSpectrum, KeysightSpectrumVsPower, GalvoScan, MWSpectraVsPower, AutoFocus, StanfordResearch_ESR, Find_Points, Select_NVs, ESR_Selected_NVs

###AARON_PC REMOVE
from src.scripts.Select_NVs import Select_NVs, Select_NVs_Simple

from src.core.read_write_functions import load_b26_file
# load the basic old_gui either from .ui file or from precompiled .py file
try:
    # import external_modules.matplotlibwidget
    Ui_MainWindow, QMainWindow = loadUiType('basic_application_window.ui') # with this we don't have to convert the .ui file into a python file!
except (ImportError, IOError):
    # load precompiled old_gui, to complite run pyqt_uic basic_application_window.ui -o basic_application_window.py
    from src.gui.basic_application_window import Ui_MainWindow
    from PyQt4.QtGui import QMainWindow
    print('Warning: on-the-fly conversion of basic_application_window.ui file failed, loaded .py file instead.')



class ControlMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, filename = None):
        """
        ControlMainWindow(intruments, scripts, probes)
            - intruments: depth 1 dictionary where keys are instrument names and keys are instrument classes
            - scripts: depth 1 dictionary where keys are script names and keys are script classes
            - probes: depth 1 dictionary where to be decided....?

        ControlMainWindow(settings_file)
            - settings_file is the path to a json file that contains all the settings for the old_gui

        Returns:

        """

        super(ControlMainWindow, self).__init__()
        self.setupUi(self)

        def setup_trees():

            # define data container
            self.history = deque(maxlen=500)  # history of executed commands
            self.history_model = QtGui.QStandardItemModel(self.list_history)
            self.list_history.setModel(self.history_model)
            self.list_history.show()

            # self.tree_settings.setColumnWidth(0, 400)
            #
            # self.tree_scripts.setColumnWidth(0, 300)
            self.tree_scripts.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

            # self.tree_monitor.setColumnWidth(0, 300)
            self.tree_monitor.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

            # self.tree_dataset.setColumnWidth(0, 100)
            # self.tree_dataset.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

            # self.tree_gui_settings.setColumnWidth(0, 500)
            self.tree_gui_settings.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            self.tree_gui_settings.doubleClicked.connect(self.edit_tree_item)

            self.current_script = None
            self.probe_to_plot = None

            # create models for tree structures, the models reflect the data
            self.tree_dataset_model = QtGui.QStandardItemModel()
            self.tree_dataset.setModel(self.tree_dataset_model)
            self.tree_dataset_model.setHorizontalHeaderLabels(['time', 'name (tag)', 'type (script)'])

            # create models for tree structures, the models reflect the data
            self.tree_gui_settings_model = QtGui.QStandardItemModel()
            self.tree_gui_settings.setModel(self.tree_gui_settings_model)
            self.tree_gui_settings_model.setHorizontalHeaderLabels(['parameter', 'value'])



        def connect_controls():
            # =============================================================
            # ===== LINK WIDGETS TO FUNCTIONS =============================
            # =============================================================

            # link slider to old_functions
            #
            # self.sliderPosition.setValue(int(self.servo_polarization.get_position() * 100))
            # self.sliderPosition.valueChanged.connect(lambda: self.set_position())

            # link buttons to old_functions
            self.btn_start_script.clicked.connect(self.btn_clicked)
            self.btn_stop_script.clicked.connect(self.btn_clicked)
            self.btn_plot_script.clicked.connect(self.btn_clicked)
            self.btn_plot_probe.clicked.connect(self.btn_clicked)
            self.btn_store_script_data.clicked.connect(self.btn_clicked)
            self.btn_plot_data.clicked.connect(self.btn_clicked)
            self.btn_save_data.clicked.connect(self.btn_clicked)
            self.btn_delete_data.clicked.connect(self.btn_clicked)


            self.btn_save_gui.triggered.connect(self.btn_clicked)
            self.btn_load_gui.triggered.connect(self.btn_clicked)
            self.btn_about.triggered.connect(self.btn_clicked)
            self.btn_exit.triggered.connect(self.close)

            self.btn_test_2.triggered.connect(self.test)


            self.btn_load_instruments.clicked.connect(self.btn_clicked)
            self.btn_load_scripts.clicked.connect(self.btn_clicked)

            # Helper function to make only column 1 editable
            def onScriptParamClick(item, column):
                if column == 1:
                    self.tree_scripts.editItem(item, column)

            # tree structures
            self.tree_scripts.itemClicked.connect(lambda: onScriptParamClick(self.tree_scripts.currentItem(),
                                                                             self.tree_scripts.currentColumn()))
            self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts))
            self.tree_settings.itemChanged.connect(lambda: self.update_parameters(self.tree_settings))
            self.tabWidget.currentChanged.connect(lambda : self.switch_tab())
            self.tree_dataset.clicked.connect(lambda: self.btn_clicked())

            self.tree_settings.itemExpanded.connect(lambda: self.refresh_instruments())

            # plots
            self.matplotlibwidget_1.mpl_connect('button_press_event', self.plot_1_clicked)
            self.matplotlibwidget_2.mpl_connect('button_press_event',  self.plot_2_clicked)

        self.create_figures()
        self.tree_scripts.setColumnWidth(0, 250)

        # create a "delegate" --- an editor that uses our new Editor Factory when creating editors,
        # and use that for tree_scripts
        delegate = QtGui.QStyledItemDelegate()
        new_factory = CustomEditorFactory()
        delegate.setItemEditorFactory(new_factory)
        self.tree_scripts.setItemDelegate(delegate)

        setup_trees()

        connect_controls()

        if filename is not None and os.path.exists(filename):
            try:
                self.config_filename = filename
                self.load_config(self.config_filename)
                self.load_settings(os.path.join(self.gui_settings['tmp_folder'],'gui_settings.b26'))
            except KeyError:
                print('Did not pre-load scripts! Issue: {:s}'.format(str(sys.exc_info())))
            except AssertionError:
                print('Did not pre-load scripts! Issue: {:s}'.format(str(sys.exc_info())))

        else:
            self.instruments = {}
            self.scripts = {}
            self.probes = {}
            self.gui_settings = {'scripts_folder': '', 'data_folder': ''}

        self.data_sets = {} # todo: load datasets from tmp folder
        self.read_probes = ReadProbes(self.probes)

    def closeEvent(self, event):

        fname =  os.path.join(self.gui_settings['tmp_folder'],'gui_settings.b26')
        print('save settings to {:s}'.format(fname))
        self.save_settings(fname)

        fname =  self.config_filename
        print('save config to {:s}'.format(fname))
        self.save_config(fname)



        event.accept()

    def test(self):
        """
        just for testing
        Returns:

        """
        fname = self.gui_settings['tmp_folder']
        print('save datasets to {:s}'.format(fname))
        self.save_dataset(fname)

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

        # following is outdated: now we want to have independent instrument settings in the scripts
        # if current_tab == 'Scripts':
        #     # rebuild script- tree because intruments might have changed
        #     self.tree_scripts.itemChanged.disconnect()
        #     self.fill_tree(self.tree_scripts, self.scripts)
        #     self.tree_scripts.itemChanged.connect(lambda: self.update_parameters(self.tree_scripts))

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

    def plot_1_clicked(self, mouse_event):
        key_press_handler(mouse_event, self.matplotlibwidget_1.canvas, self.matplotlibwidget_1)
        self.plot_clicked(mouse_event)

    def plot_2_clicked(self, mouse_event):
        key_press_handler(mouse_event, self.matplotlibwidget_1.canvas, self.matplotlibwidget_1)
        self.plot_clicked(mouse_event)

    def plot_clicked(self, mouse_event):
        if isinstance(self.current_script, (Select_NVs, Select_NVs_Simple)) and self.current_script.isRunning:
            if (not (mouse_event.xdata == None)):
                if (mouse_event.button == 1):
                    pt = np.array([mouse_event.xdata, mouse_event.ydata])
                    self.current_script.toggle_NV(pt, self.matplotlibwidget_1.figure)
                    self.matplotlibwidget_1.draw()

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
    def log(self, msg):

        time = self.get_time()

        msg = "{:s}\t {:s}".format(time, msg)

        self.history.append(msg)
        self.history_model.insertRow(0,QtGui.QStandardItem(msg))

    def create_figures(self):
        try:
            self.horizontalLayout_15.removeWidget(self.matplotlibwidget_2)
            self.horizontalLayout_14.removeWidget(self.matplotlibwidget_1)
            self.matplotlibwidget_1.close()
            self.matplotlibwidget_2.close()
        except AttributeError:
            pass
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(QtCore.QString.fromUtf8("centralwidget"))
        self.matplotlibwidget_2 = MatplotlibWidget(self.plot_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.matplotlibwidget_2.sizePolicy().hasHeightForWidth())
        self.matplotlibwidget_2.setSizePolicy(sizePolicy)
        self.matplotlibwidget_2.setMinimumSize(QtCore.QSize(200, 200))
        self.matplotlibwidget_2.setObjectName(QtCore.QString.fromUtf8("matplotlibwidget_2"))
        self.horizontalLayout_16.addWidget(self.matplotlibwidget_2)
        self.matplotlibwidget_1 = MatplotlibWidget(self.plot_1)
        self.matplotlibwidget_1.setMinimumSize(QtCore.QSize(200, 200))
        self.matplotlibwidget_1.setObjectName(QtCore.QString.fromUtf8("matplotlibwidget_1"))
        self.horizontalLayout_15.addWidget(self.matplotlibwidget_1)
        self.matplotlibwidget_1.mpl_connect('button_press_event', self.plot_1_clicked)
        self.matplotlibwidget_2.mpl_connect('button_press_event', self.plot_2_clicked)

        # adds a toolbar to the plots
        self.mpl_toolbar_1 = NavigationToolbar(self.matplotlibwidget_1.canvas, self.toolbar_space_1)
        self.mpl_toolbar_2 = NavigationToolbar(self.matplotlibwidget_2.canvas, self.toolbar_space_2)
        self.horizontalLayout_9.addWidget(self.mpl_toolbar_2)
        self.horizontalLayout_14.addWidget(self.mpl_toolbar_1)


        self.matplotlibwidget_1.figure.tight_layout()
        self.matplotlibwidget_2.figure.tight_layout()

    def btn_clicked(self):
        sender = self.sender()
        self.probe_to_plot = None

        # the following function takes the current figures and makes a new widget in place of them.
        # This work-around is necessary because figures have a nasty 'feature' of remembering axes
        # characteristics of previous plots, and this is the only way I (Arthur) could figure out how to do it.


        def start_button():

            item = self.tree_scripts.currentItem()
            self.script_start_time = datetime.datetime.now()


            if item is not None:
                script, path_to_script, script_item = item.get_script()

                self.update_script_from_item(script_item)
                script.data_path = self.gui_settings['data_folder']
                self.log('starting {:s}'.format(script.name))
                # is the script is not a QThread object we use the wrapper QtSCript
                # to but it on a separate thread such that the gui remains responsive
                if not isinstance(script, QThread):
                    script = QThreadWrapper(script)

                script.updateProgress.connect(self.update_status)

                self.current_script = script
                self.btn_start_script.setEnabled(False)

                # if not isinstance(script, Select_NVs_Simple):
                #     self.create_figures()

                script.start()
            else:
                self.log('User stupidly tried to run a script without one selected.')
        def stop_button():
            if self.current_script is not None and self.current_script.isRunning():
                self.current_script.stop()
            else:
                self.log('User clicked stop, but there isn\'t anything running...this is awkward. Re-enabling start button anyway.')
            self.btn_start_script.setEnabled(True)
        def store_script_data():
            """
            send selected script to dataset tab
            Returns:

            """
            item = self.tree_scripts.currentItem()
            if item is not None:
                script, path_to_script, _ = item.get_script()
                # self.data_sets.append({}
                #     'data' : script.data,
                # })

                script_copy = script.duplicate()
                time_tag = script.start_time.strftime('%y%m%d-%H_%M_%S')

                self.data_sets.update({time_tag : script_copy})

                self.fill_dataset_tree(self.tree_dataset, self.data_sets)
        def save_data():
            indecies = self.tree_dataset.selectedIndexes()
            model = indecies[0].model()
            rows = list(set([index.row()for index in indecies]))

            for row in rows:
                time_tag = str(model.itemFromIndex(model.index(row, 0)).text())
                name_tag = str(model.itemFromIndex(model.index(row, 1)).text())
                path = self.gui_settings['data_folder']
                script = self.data_sets[time_tag]
                script.update({'tag' : name_tag, 'path': path})
                script.save_data()
                script.save_b26()
                script.save_log()
        def delete_data():
            indecies = self.tree_dataset.selectedIndexes()
            model = indecies[0].model()
            rows = list(set([index.row()for index in indecies]))

            for row in rows:
                time_tag = str(model.itemFromIndex(model.index(row, 0)).text())
                print(self.data_sets.keys())
                del self.data_sets[time_tag]

                model.removeRows(row,1)

        def plot_data(sender):
            print(sender)
            if sender in (self.btn_plot_data, self.tree_dataset):
                index = self.tree_dataset.selectedIndexes()[0]
                model = index.model()
                time_tag = str(model.itemFromIndex(model.index(index.row(), 0)).text())
                script = self.data_sets[time_tag]
            elif sender == self.btn_plot_script:
                item = self.tree_scripts.currentItem()
                if item is not None:
                    script, path_to_script, _ = item.get_script()
            # self.update_script_from_selected_item(script, self.tree_scripts)# jan: not sure why this is needed here....
            self.plot_script(script)

        if sender is self.btn_start_script:
            start_button()
        elif sender is self.btn_stop_script:
            stop_button()
        # elif sender is self.btn_plot_data or sender is self.btn_plot_script or sender is self.tree_dataset:
        elif sender in (self.btn_plot_data, self.btn_plot_script, self.tree_dataset):
            plot_data(sender)
        elif sender is self.btn_store_script_data:
            store_script_data()
        elif sender is self.btn_save_data:
            save_data()
        elif sender is self.btn_delete_data:
            delete_data()
        elif sender is self.btn_plot_probe:
            item = self.tree_monitor.currentItem()
            if item is not None:
                self.probe_to_plot = self.probes[item.name]
            else:
                self.log('Can\'t plot, No probe selected. Select probe and try again!')
        elif sender is self.btn_save_gui:
            # get filename
            fname = QtGui.QFileDialog.getSaveFileName(self, 'Save gui settings to file', self.gui_settings['data_folder']) # filter = '.b26gui'
            self.save_settings(fname)
        elif sender is self.btn_load_gui:
            # get filename
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Load gui settings from file',  self.gui_settings['data_folder'])
            self.load_settings(fname)
        elif sender is self.btn_about:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText("Lukin Lab B26 Gui")
            msg.setInformativeText("Check out: https://github.com/LISE-B26/PythonLab")
            msg.setWindowTitle("About")
            # msg.setDetailedText("some stuff")
            msg.setStandardButtons(QtGui.QMessageBox.Ok)
            # msg.buttonClicked.connect(msgbtn)
            retval = msg.exec_()
        elif (sender is self.btn_load_instruments) or (sender is self.btn_load_scripts):

            if sender is self.btn_load_instruments:

                if 'instrument_folder' in self.gui_settings:
                    dialog = LoadDialog(elements_type="instruments", elements_old=self.instruments,
                                        filename=self.gui_settings['instrument_folder'])

                else:
                    dialog = LoadDialog(elements_type="instruments", elements_old=self.instruments)


                if dialog.exec_():
                    self.gui_settings['instrument_folder'] = str(dialog.txt_probe_log_path.text())
                    instruments = dialog.getValues()
                    added_instruments = set(instruments.keys())-set(self.instruments.keys())
                    removed_instruments = set(self.instruments.keys()) - set(instruments.keys())
                    print('added_instruments', {name: instruments[name] for name in added_instruments})

                    # create instances of new instruments
                    self.instruments, loaded_failed = Instrument.load_and_append(
                        {name: instruments[name] for name in added_instruments}, self.instruments)
                    if loaded_failed != []:
                        print('WARNING following instrument could not be loaded', loaded_failed)
                    # delete instances of new instruments/scripts that have been deselected
                    for name in removed_instruments:
                        del self.instruments[name]

            elif sender is self.btn_load_scripts:

                dialog = LoadDialog(elements_type="scripts", elements_old=self.scripts, filename=self.gui_settings['scripts_folder'])
                if dialog.exec_():
                    self.gui_settings['scripts_folder'] = str(dialog.txt_probe_log_path.text())
                    scripts = dialog.getValues()
                    added_scripts = set(scripts.keys())-set(self.scripts.keys())
                    removed_scripts = set(self.scripts.keys()) - set(scripts.keys())


                    if 'data_folder' in self.gui_settings.keys() and os.path.exists(self.gui_settings['data_folder']):
                        data_folder_name = self.gui_settings['data_folder']
                    else:
                        data_folder_name = None

                    # create instances of new instruments/scripts
                    self.scripts, loaded_failed, self.instruments = Script.load_and_append(script_dict = {name: scripts[name] for name in added_scripts},
                                                                                           scripts = self.scripts,
                                                                                           instruments = self.instruments,
                                                                                           log_function = self.log,
                                                                                           data_path = data_folder_name)
                    # delete instances of new instruments/scripts that have been deselected
                    for name in removed_scripts:
                        del self.scripts[name]
            # refresh trees
            self.refresh_tree(self.tree_scripts, self.scripts)
            self.refresh_tree(self.tree_settings, self.instruments)

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
            script, path_to_script, _ = item.get_script()

            # check if changes value is from an instrument
            instrument, path_to_instrument = item.get_instrument()
            if instrument is not None:
                print('INSTUMENT PARAMETER CHANGED in', script.instruments[instrument.name])

                # just check if value is valid without actually sending a command to the instrument

                # # get old value from script.instrument
                # old_value = script.instruments[instrument.name].settings
                # path_to_instrument.reverse()
                # for element in path_to_instrument:
                #     old_value = old_value[element]

                new_value = item.value


                msg = "changed parameter {:s} to {:s} on {:s}".format(item.name,
                                                                                str(new_value),
                                                                                script.name)
                print(msg)
            else:
                new_value = item.value
                msg = "changed parameter {:s} to {:s} on {:s}".format(item.name,
                                                                            str(new_value),
                                                                            script.name)
            self.log(msg)

    def plot_script(self, script):
        """
        checks the plottype of the script and plots it accordingly
        Args:
            script: script to be plotted

        """
        if script.plot_type == 'main':
            script.plot(self.matplotlibwidget_1.figure)
            self.matplotlibwidget_1.draw()
        elif script.plot_type == 'aux':
            script.plot(self.matplotlibwidget_2.figure)
            self.matplotlibwidget_2.draw()
        elif script.plot_type == 'two':
            script.plot(self.matplotlibwidget_1.figure, self.matplotlibwidget_2.figure)
            self.matplotlibwidget_1.draw()
            self.matplotlibwidget_2.draw()
        elif script.plot_type == 'none':
            pass
        else:
            message = 'property plot_type = {:s} not correct for this script ({:s})!'.format(str(script.plot_type), script.name)
            raise AttributeError(message)

    def update_status(self, progress):
        """
        waits for a signal emitted from a thread and updates the gui
        Args:
            progress:

        Returns:

        """
        # print('SIGNAL')
        self.progressBar.setValue(progress)

        # Estimate remaining time if progress has been made
        if progress:

            def _translate(context, text, disambig):
                _encoding = QtGui.QApplication.UnicodeUTF8
                return QtGui.QApplication.translate(context, text, disambig, _encoding)

            script_run_time = datetime.datetime.now() - self.script_start_time
            remaining_time_seconds = (100.0-progress)*script_run_time.total_seconds()/float(progress)
            remaining_time_minutes = int(remaining_time_seconds/60.0)
            leftover_seconds = int(remaining_time_seconds - remaining_time_minutes*60)

            self.lbl_time_estimate.setText(_translate("MainWindow",
                                                      "time remaining: {0} min, {1} sec".format(remaining_time_minutes,
                                                                                                leftover_seconds), None))

        script = self.current_script
        if isinstance(script, QThreadWrapper):
            script = script.script
        self.plot_script(script)


        if progress == 100:
            # self.refresh_tree(self.tree_scripts, self.scripts)
            self.btn_start_script.setEnabled(True)
            self.current_script.updateProgress.disconnect(self.update_status)

    def update_probes(self, progress):
        """
        update the probe monitor tree
        """

        new_values = self.read_probes.probes_values
        probe_count = len(self.read_probes.probes)

        if probe_count > self.tree_monitor.topLevelItemCount():
            # when run for the first time, there are no probes in the tree, so we have to fill it first
            self.fill_treewidget(self.tree_monitor, self.read_probes.probes_values)
        else:
            for x in range(0 , probe_count):
                topLvlItem = self.tree_monitor.topLevelItem(x)
                topLvlItem.value = new_values[topLvlItem.name]
                topLvlItem.setText(1, unicode(topLvlItem.value))
        if self.probe_to_plot is not None:
            self.probe_to_plot.plot(self.matplotlibwidget_1.axes)
            self.matplotlibwidget_1.draw()


        if self.chk_probe_log.isChecked():
            file_name  = str(self.txt_probe_log_path.text())
            if os.path.isfile(file_name) == False:
                outfile = open(file_name, 'w')
                outfile.write("{:s}\n".format(",".join(new_values.keys())))
            else:
                outfile = open(file_name, 'a')
            outfile.write("{:s}\n".format(",".join(map(str, new_values.values()))))

    def update_script_from_item(self, item):
        """
        updates the script based on the information provided in item

        Args:
            script: script to be updated
            item: B26QTreeItem that contains the new settings of the script

        """

        script, path_to_script, script_item = item.get_script()

        # build dictionary
        # get full information from script
        dictator = script_item.to_dict().values()[0]  # there is only one item in the dictionary
        for instrument in script.instruments.keys():
            # update instrument
            script.instruments[instrument]['settings'] = dictator[instrument]['settings']
            # remove instrument
            del dictator[instrument]


        for sub_script_name in script.scripts.keys():
            sub_script_item = script_item.get_subscript(sub_script_name)
            self.update_script_from_item(sub_script_item)
            del dictator[sub_script_name]

        script.update(dictator)

    def fill_treewidget(self, tree, parameters):
        """
        fills a QTreeWidget with nested parameters, in future replace QTreeWidget with QTreeView and call fill_treeview
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

    def fill_treeview(self, tree, input_dict):
        """
        fills a treeview with nested parameters
        Args:
            tree: QtGui.QTreeView
            parameters: dictionary or Parameter object

        Returns:

        """
        # tree.model().clear()
        tree.model().removeRows(0, tree.model().rowCount())
        def add_elemet(item, key, value):
            child_name = QtGui.QStandardItem(key)
            # child_name.setDragEnabled(False)
            # child_name.setSelectable(False)
            # child_name.setEditable(False)

            if isinstance(value, dict):
                for key_child, value_child in value.iteritems():
                    add_elemet(child_name, key_child, value_child)
                item.appendRow(child_name)
            else:
                child_value = QtGui.QStandardItem(unicode(value))
                # child_value.setDragEnabled(False)
                # child_value.setSelectable(False)
                # child_value.setEditable(False)

                item.appendRow([child_name, child_value])

        for index, (key, value) in enumerate(input_dict.iteritems()):

            if isinstance(value, dict):
                item = QtGui.QStandardItem(key)
                for sub_key, sub_value in value.iteritems():
                    add_elemet(item, sub_key, sub_value)
                tree.model().appendRow(item)
            elif isinstance(value, str):
                item = QtGui.QStandardItem(key)
                item_value = QtGui.QStandardItem(value)
                item_value.setEditable(True)
                item_value.setSelectable(True)
                tree.model().appendRow([item, item_value])


            # if tree == self.tree_loaded:
            #     item.setEditable(False)
            # tree.setFirstColumnSpanned(index, tree.rootIndex(), True)

    def edit_tree_item(self):

        def open_path_dialog(path):
            """
            opens a file dialog to get the path to a file and
            """
            dialog = QtGui.QFileDialog()
            dialog.setFileMode(QtGui.QFileDialog.Directory)
            dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
            path = dialog.getExistingDirectory(self, 'Select a folder:', path)

            return path

        tree = self.sender()

        if tree == self.tree_gui_settings:

            index = tree.selectedIndexes()[0]
            model = index.model()

            if index.column() == 1:
                path = model.itemFromIndex(index).text()
                path = str(open_path_dialog(path))

                key = str(model.itemFromIndex(model.index(index.row(), 0)).text())

                if path != "":
                    self.gui_settings.update({key:path})
                    self.fill_treeview(tree, self.gui_settings)


    def refresh_tree(self, tree, items):
        """
        refresh trees with current settings
        Args:
            tree: a QtGui.QTreeWidget object or a QtGui.QTreeView object

        Returns:

        """


        if tree == self.tree_scripts or tree == self.tree_settings:
            tree.itemChanged.disconnect()
            self.fill_treewidget(tree, items)
            tree.itemChanged.connect(lambda: self.update_parameters(tree))
        # elif tree == self.tree_dataset:
        #     self.fill_dataset(tree, self.data_sets)
        elif tree == self.tree_gui_settings:
            self.fill_treeview(tree, items)

    def fill_dataset_tree(self, tree, data_sets):

        tree.model().removeRows(0, tree.model().rowCount())
        for index, (time, script) in enumerate(data_sets.iteritems()):
            name = script.settings['tag']
            type = script.name

            item_time = QtGui.QStandardItem(unicode(time))
            item_name = QtGui.QStandardItem(unicode(name))
            item_type = QtGui.QStandardItem(unicode(type))

            item_time.setSelectable(False)
            item_time.setEditable(False)
            item_type.setSelectable(False)
            item_type.setEditable(False)

            tree.model().appendRow([item_time, item_name, item_type])


    def load_config(self, file_name):
        assert os.path.isfile(file_name), file_name

        in_data = load_b26_file(file_name)
        assert "gui_settings" in in_data
        self.gui_settings = in_data['gui_settings']

        self.refresh_tree(self.tree_gui_settings, self.gui_settings)

    def load_settings(self, in_file_name):
        """
        loads a old_gui settings file (a json dictionary)
        - path_to_file: path to file that contains the dictionary

        Returns:
            - instruments: depth 1 dictionary where keys are instrument names and values are instances of instruments
            - scripts:  depth 1 dictionary where keys are script names and values are instances of scripts
            - probes: depth 1 dictionary where to be decided....?
        """

        self.instruments = {}
        self.probes = {}
        self.scripts = {}
        print('loading config file: ', in_file_name)

        # assert os.path.isfile(in_file_name), in_file_name



        if os.path.isfile(in_file_name):
            in_data = load_b26_file(in_file_name)

            instruments = in_data['instruments']
            scripts = in_data['scripts']
            probes = in_data['probes']
            # print('============ loading instruments ================')
            self.instruments, failed = Instrument.load_and_append(instruments)
            if failed != {}:
                print('WARNING! Following instruments could not be loaded: ', failed)
            print('============ loading scripts ================')
            self.scripts, failed, self.instruments = Script.load_and_append(
                script_dict=scripts,
                instruments=self.instruments,
                log_function=self.log,
                data_path=self.gui_settings['data_folder'])
            if failed != {}:
                print('WARNING! Following scripts could not be loaded: ', failed)
            print('INFO: ==== loading probes not implmented yet================')
            # probes = instantiate_probes(probes, instruments)
            # todo: implement probes
            self.probes = {}
            # refresh trees
            self.refresh_tree(self.tree_scripts, self.scripts)


            self.refresh_tree(self.tree_settings, self.instruments)
        else:
            self.instruments = {}
            self.scripts = {}
            self.probes = {}

    def save_settings(self, out_file_name):
        """
        saves a old_gui settings file (to a json dictionary)
        - path_to_file: path to file that will contain the dictionary
        """
        out_file_name = str(out_file_name)

        print('saving', out_file_name)

        # update the internal dictionaries from the trees in the gui
        for index in range(self.tree_scripts.topLevelItemCount()):
            script_item = self.tree_scripts.topLevelItem(index)
            self.update_script_from_item(script_item)

        out_data = {'instruments': {}, 'scripts': {}, 'probes': {}}

        for instrument in self.instruments.itervalues():
            out_data['instruments'].update(instrument.to_dict())

        for script in self.scripts.itervalues():
            out_data['scripts'].update(script.to_dict())

        for probe in self.probes.itervalues():
            out_data['probes'].update(probe.to_dict())

        if not os.path.exists(os.path.dirname(out_file_name)):
            print('creating: ', out_file_name)
            os.makedirs(os.path.dirname(out_file_name))

        with open(out_file_name, 'w') as outfile:
            tmp = json.dump(out_data, outfile, indent=4)

    def save_config(self, out_file_name):
        """
        saves gui configuration to out_file_name
        Args:
            out_file_name: name of file
        """
        if not os.path.exists(os.path.dirname(out_file_name)):
            os.makedirs(os.path.dirname(out_file_name))

        with open(out_file_name, 'w') as outfile:
            tmp = json.dump({"gui_settings":self.gui_settings}, outfile, indent=4)

    def save_dataset(self, out_file_name):
        """
        saves current dataset to out_file_name
        Args:
            out_file_name: name of file
        """

        for time_tag, script in self.data_sets.iteritems():
            print(time_tag, script)
            script.save(os.path.join(out_file_name, '{:s}.b26s'.format(time_tag)))


# In order to set the precision when editing floats, we need to override the default Editor widget that
# pops up over the text when you click. To do that, we create a custom Editor Factory so that the QTreeWidget
# uses the custom spinbox when editing floats
class CustomEditorFactory(QtGui.QItemEditorFactory):
    def createEditor(self, type, QWidget):
        if type == QtCore.QVariant.Double or type == QtCore.QVariant.Int:
            spin_box = QtGui.QLineEdit(QWidget)
            return spin_box
        else:
            return super(CustomEditorFactory, self).createEditor(type, QWidget)



class MatplotlibWidget(Canvas):
    """
    MatplotlibWidget inherits PyQt4.QtGui.QWidget
    and matplotlib.backend_bases.FigureCanvasBase

    Options: option_name (default_value)
    -------
    parent (None): parent widget
    title (''): figure title
    xlabel (''): X-axis label
    ylabel (''): Y-axis label
    xlim (None): X-axis limits ([min, max])
    ylim (None): Y-axis limits ([min, max])
    xscale ('linear'): X-axis scale
    yscale ('linear'): Y-axis scale
    width (4): width in inches
    height (3): height in inches
    dpi (100): resolution in dpi
    hold (False): if False, figure will be cleared each time plot is called

    Widget attributes:
    -----------------
    figure: instance of matplotlib.figure.Figure
    axes: figure axes

    Example:
    -------
    self.widget = MatplotlibWidget(self, yscale='log', hold=True)
    from numpy import linspace
    x = linspace(-10, 10)
    self.widget.axes.plot(x, x**2)
    self.wdiget.axes.plot(x, x**3)
    """
    def __init__(self, parent=None):
        self.figure = Figure(dpi=100)
        Canvas.__init__(self, self.figure)
        self.axes = self.figure.add_subplot(111)

        self.canvas = self.figure.canvas
        self.setParent(parent)

        Canvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

    def sizeHint(self):
        w, h = self.get_width_height()
        return QtCore.QSize(w, h)

    def minimumSizeHint(self):
        return QtCore.QSize(10, 10)