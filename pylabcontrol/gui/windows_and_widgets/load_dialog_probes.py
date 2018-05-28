
# This file is part of pylabcontrol, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
# pylabcontrol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pylabcontrol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pylabcontrol.  If not, see <http://www.gnu.org/licenses/>.

"""
Basic gui class designed with QT designer
"""
# import sip
# sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
import os

from PyQt5 import QtGui
from PyQt5.uic import loadUiType

from pylabcontrol.core.read_write_functions import load_b26_file

# load the basic old_gui either from .ui file or from precompiled .py file
try:
    # import external_modules.matplotlibwidget
    Ui_Dialog, QDialog = loadUiType('load_dialog.ui') # with this we don't have to convert the .ui file into a python file!
except (ImportError, IOError):
    # load precompiled old_gui, to complite run pyqt_uic basic_application_window.ui -o basic_application_window.py
    from pylabcontrol.gui.compiled_ui_files.load_dialog import Ui_Dialog
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QDialog
    # print('Warning!: on the fly conversion of load_dialog.ui file failed, loaded .py file instead!!')



class LoadDialogProbes(QDialog, Ui_Dialog):
    """
LoadDialog(intruments, scripts, probes)
    - type: either script, instrument or probe
    - loaded_elements: dictionary that contains the loaded elements
MainWindow(settings_file)
    - settings_file is the path to a json file that contains all the settings for the old_gui
Returns:
    """

    def __init__(self, probes_old={}, filename=None):
        super(LoadDialogProbes, self).__init__()
        self.setupUi(self)

        if filename is None:
            filename = ''
        self.txt_probe_log_path.setText(filename)

        # create models for tree structures, the models reflect the data
        self.tree_infile_model = QtGui.QStandardItemModel()
        self.tree_infile.setModel(self.tree_infile_model)
        QtGui.QStandardItemModel().reset()

        self.tree_infile_model.setHorizontalHeaderLabels(['Instrument', 'Probe'])
        self.tree_loaded_model = QtGui.QStandardItemModel()
        self.tree_loaded.setModel(self.tree_loaded_model)
        self.tree_loaded_model.setHorizontalHeaderLabels(['Instrument', 'Probe'])
        # connect the buttons
        self.btn_open.clicked.connect(self.open_file_dialog)

        # create the dictionaries that hold the data
        #   - elements_old: the old elements (scripts, instruments) that have been passed to the dialog
        #   - elements_from_file: the elements from the file that had been opened
        print(('adsada', probes_old))
        self.elements_selected = {}
        for instrument_name, p in probes_old.items():
            self.elements_selected.update( {instrument_name: ','.join(list(p.keys()))})
        if os.path.isfile(filename):
            self.elements_from_file = self.load_elements(filename)
        else:
            self.elements_from_file = {}

        # fill trees with the data
        self.fill_tree(self.tree_loaded, self.elements_selected)
        self.fill_tree(self.tree_infile, self.elements_from_file)

        self.tree_infile.selectionModel().selectionChanged.connect(self.show_info)
        self.tree_loaded.selectionModel().selectionChanged.connect(self.show_info)

        self.tree_infile_model.itemChanged.connect(self.item_dragged_and_dropped)
        self.tree_loaded_model.itemChanged.connect(self.item_dragged_and_dropped)


    def item_dragged_and_dropped(self):
        """

        adds and removes probes from the trees when they are dragged and dropped

        """

        index = None
        self.tree_infile_model.itemChanged.disconnect()
        self.tree_loaded_model.itemChanged.disconnect()

        index_infile = self.tree_infile.selectedIndexes()
        index_loaded = self.tree_loaded.selectedIndexes()
        if index_infile != []:
            index = index_infile[0]
            dict_target = self.elements_selected
            dict_source = self.elements_from_file
        elif index_loaded != []:
            index = index_loaded[0]
            dict_source = self.elements_selected
            dict_target= self.elements_from_file

        if index is not None:

            parent = index.model().itemFromIndex(index).parent()
            if parent is None:
                instrument_name = str(index.model().itemFromIndex(index).text())
                probe_names = [str(index.model().itemFromIndex(index).child(i).text()) for i in range(index.model().itemFromIndex(index).rowCount())]
            else:
                instrument_name = str(parent.text())
                probe_names = [str(index.model().itemFromIndex(index).text())]

            if not instrument_name in list(dict_target.keys()):
                dict_target.update({instrument_name: ','.join(probe_names)})
                dict_source[instrument_name] = ','.join(set(dict_source[instrument_name].split(',')) - set(probe_names))
            else:
                dict_target[instrument_name] = ','.join(set(dict_target[instrument_name].split(',') + probe_names))
                dict_source[instrument_name] = ','.join(set(dict_source[instrument_name].split(',')) - set(probe_names))

            if instrument_name in dict_source and  dict_source[instrument_name] == '':
                del dict_source[instrument_name]
            if instrument_name in dict_target and dict_target[instrument_name] == '':
                del dict_target[instrument_name]

        else:
            # this case should never happen but if it does raise an error
            raise TypeError

        self.fill_tree(self.tree_loaded, self.elements_selected)
        self.fill_tree(self.tree_infile, self.elements_from_file)
        self.tree_infile_model.itemChanged.connect(self.item_dragged_and_dropped)
        self.tree_loaded_model.itemChanged.connect(self.item_dragged_and_dropped)

    def show_info(self):
        """
        displays the doc string of the selected element
        """

        sender = self.sender()
        tree = sender.parent()
        index = tree.selectedIndexes()
        info = ''
        if index != []:
            index = index[0]
            name = str(index.model().itemFromIndex(index).text())

            if name in set(list(self.elements_from_file.keys()) + list(self.elements_selected.keys())):
                probe_name = None
                instrument_name = name
            else:
                instrument_name = str(index.model().itemFromIndex(index).parent().text())
                probe_name = name



            module = __import__('pylabcontrol.instruments', fromlist=[instrument_name])
            if probe_name is None:
                info = getattr(module, instrument_name).__doc__
            else:
                if probe_name in list(getattr(module, instrument_name)._PROBES.keys()):
                    info = getattr(module, instrument_name)._PROBES[probe_name]

        if info is not None:
            self.lbl_info.setText(info)

    def open_file_dialog(self):
        """
        opens a file dialog to get the path to a file and
        """
        dialog = QtGui.QFileDialog
        filename = dialog.getOpenFileName(self, 'Select a file:', self.txt_probe_log_path.text())
        if str(filename)!='':
            self.txt_probe_log_path.setText(filename)
            # load elements from file and display in tree
            elements_from_file = self.load_elements(filename)
            self.fill_tree(self.tree_infile, elements_from_file)
            # append new elements to internal dictionary
            self.elements_from_file.update(elements_from_file)
    def load_elements(self, filename):
        """
        loads the elements from file filename
        """
        input_data = load_b26_file(filename)
        if isinstance(input_data, dict) and 'probes' in input_data:
            return input_data['probes']
        else:
            return {}

    def fill_tree(self, tree, input_dict):
        """
        fills a tree with nested parameters
        Args:
            tree: QtGui.QTreeView
            parameters: dictionary or Parameter object

        Returns:

        """


        def removeAll(tree):

            if tree.model().rowCount() > 0:
                for i in range(0, tree.model().rowCount()):
                    item = tree.model().item(i)
                    del item
                    tree.model().removeRows(0, tree.model().rowCount())
                    tree.model().reset()

        def add_probe(tree, instrument, probes):
            item = QtGui.QStandardItem(instrument)
            item.setEditable(False)

            for probe in probes.split(','):
                child_name = QtGui.QStandardItem(probe)
                child_name.setDragEnabled(True)
                child_name.setSelectable(True)
                child_name.setEditable(False)
                item.appendRow(child_name)
            tree.model().appendRow(item)

        removeAll(tree)

        for index, (instrument, probes) in enumerate(input_dict.items()):
            add_probe(tree, instrument, probes)
            # tree.setFirstColumnSpanned(index, self.tree_infile.rootIndex(), True)
        tree.expandAll()

    def getValues(self):
        """
        Returns: the selected elements
        """
        print(('self.elements_selected', self.elements_selected))
        return self.elements_selected

if __name__ == '__main__':
    import sys
    from pylabcontrol.core import Probe
    app = QtGui.QApplication(sys.argv)
    folder = "C:/Users/Experiment/PycharmProjects/PythonLab/b26_files/probes_auto_generated/"
    dialog = LoadDialogProbes(probes_old={}, filename=folder)
    dialog.show()
    dialog.raise_()
    if dialog.exec_():
        probes = dialog.getValues()

        print(probes)

        probes_obj, failed, instruments = Probe.load_and_append(
            probe_dict=probes,
            probes={},
            instruments={})
        print((probes_obj, failed, instruments))
    sys.exit(app.exec_())


