# This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
# PyLabControl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyLabControl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.


import traceback

from PyQt5 import QtGui, QtWidgets
from PyQt5.uic import loadUiType

from PyLabControl.src.core.read_write_functions import load_b26_file
from PyLabControl.src.core.helper_functions import get_python_package
# from PyLabControl.src.core import Parameter, Script
from PyLabControl.src.tools.export_default_v2 import find_scripts_in_python_files, python_file_to_b26
import inspect

# load the basic old_gui either from .ui file or from precompiled .py file
try:
    # import external_modules.matplotlibwidget
    Ui_Dialog, QDialog = loadUiType('import_window.ui') # with this we don't have to convert the .ui file into a python file!
except (ImportError, IOError):
    from PyLabControl.src.gui.load_dialog import Ui_Dialog
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QDialog
    print('Warning!: on the fly conversion of load_dialog.ui file failed, loaded .py file instead!!\n')


class ExportDialog(QDialog, Ui_Dialog):
    """
LoadDialog(intruments, scripts, probes)
    - type: either script, instrument or probe
    - loaded_elements: dictionary that contains the loaded elements
ControlMainWindow(settings_file)
    - settings_file is the path to a json file that contains all the settings for the old_gui
Returns:
    """

    def __init__(self):
        super(ExportDialog, self).__init__()
        self.setupUi(self)

        # create models for tree structures, the models reflect the data
        self.list_script_model = QtGui.QStandardItemModel()
        self.list_script.setModel(self.list_script_model)
        self.error_array = {}

        self.list_script.selectionModel().selectionChanged.connect(self.display_info)

        #
        # # connect the buttons
        self.btn_open_source.clicked.connect(self.open_file_dialog)
        self.btn_open_target.clicked.connect(self.open_file_dialog)
        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_select_none.clicked.connect(self.select_none)
        self.btn_export.clicked.connect(self.export)

    # def show_info(self):
    #     """
    #     displays the doc string of the selected element
    #     """
    #     sender = self.sender()
    #     tree = sender.parent()
    #     index = tree.selectedIndexes()
    #     info = ''
    #     if index != []:
    #         index = index[0]
    #         name = str(index.model().itemFromIndex(index).text())
    #         self.selected_element_name = name
    #
    #
    #
    #         if name in self.elements_old:
    #             info = self.elements_old[name].__doc__
    #
    #         #TODO: check if this is portable
    #         elif name in self.elements_from_file:
    #             class_name = self.elements_from_file[name]['class']
    #             if 'filepath' in self.elements_from_file[name]:
    #                 filepath = self.elements_from_file[name]['filepath']
    #             if 'info' in self.elements_from_file[name]:
    #                 info = self.elements_from_file[name]['info']
    #             #
    #             # path_to_src_scripts = filepath[:filepath.find('\\src\\scripts\\')]
    #             # module_name = path_to_src_scripts[path_to_src_scripts.rfind('\\')+1:]
    #             # module = __import__('{:s}.src.{:s}'.format(module_name, self.elements_type), fromlist=[class_name])
    #             # info = getattr(module, class_name).__doc__
    #
    #         if info is None:
    #             info = name
    #
    #         if tree == self.tree_infile:
    #             self.lbl_info.setText(info)
    #             self.tree_loaded.clearSelection()
    #
    #         elif tree == self.tree_loaded:
    #             self.lbl_info.setText(info)
    #             self.tree_infile.clearSelection()

    def open_file_dialog(self):
        """
        opens a file dialog to get the path to a file and
        """
        dialog = QtWidgets.QFileDialog
        sender = self.sender()
        if sender == self.btn_open_source:
            textbox = self.source_path
        elif sender == self.btn_open_target:
            textbox = self.target_path
        folder = dialog.getExistingDirectory(self, 'Select a file:', textbox.text(), options = QtWidgets.QFileDialog.ShowDirsOnly)
        if str(folder) != '':
            textbox.setText(folder)
            # load elements from file and display in tree
            if sender == self.btn_open_source:
                self.avaliable_scripts = find_scripts_in_python_files(folder)
                print(self.avaliable_scripts['SetLaser']['info'])
                self.fill_list(self.list_script, self.avaliable_scripts.keys())
                for key in self.avaliable_scripts.keys():
                    self.error_array.update({key: ''})


    def fill_list(self, list, input_list):
        """
        fills a tree with nested parameters
        Args:
            tree: QtGui.QTreeView
            parameters: dictionary or Parameter object

        Returns:

        """
        for name in input_list:
            # print(index, loaded_item, loaded_item_settings)
            item = QtGui.QStandardItem(name)
            item.setSelectable(True)
            item.setEditable(False)

            list.model().appendRow(item)

    def select_none(self):
        self.list_script.clearSelection()

    def select_all(self):
        self.list_script.selectAll()

    def export(self):
        selected_index = self.list_script.selectedIndexes()
        for index in selected_index:
            item = self.list_script.model().itemFromIndex(index)
            name = str(item.text())
            target_path = self.target_path.text()
            print(self.avaliable_scripts)
            try:
                python_file_to_b26({name: self.avaliable_scripts[name]}, target_path, raise_errors = True)
                self.error_array.update({name: 'export successful!'})
                item.setBackground(QtGui.QColor('green'))
            except Exception:
                self.error_array.update({name: str(traceback.format_exc())})
                item.setBackground(QtGui.QColor('red'))
        self.list_script.clearSelection()

    def display_info(self):
        sender = self.sender()
        somelist = sender.parent()
        index = somelist.selectedIndexes()
        if index != []:
            index = index[-1]
            name = str(index.model().itemFromIndex(index).text())
            self.text_error.setText(self.error_array[name])
            if(self.avaliable_scripts[name]['info'] == None):
                self.text_info.setText('No information avaliable')
            else:
                self.text_info.setText(self.avaliable_scripts[name]['info'])


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    # ex = LoadDialog(elements_type = 'instruments', elements_old=instuments, filename="Z:\Lab\Cantilever\Measurements\\__tmp\\test.b26")
    # ex = LoadDialog(elements_type='scripts', elements_old=instuments)
    ex = ExportDialog()

    ex.show()
    ex.raise_()

    print('asda')
    if ex.exec_():
        values = ex.get_values()
        print(values)

    sys.exit(app.exec_())

    # from PyLabControl.src.core.helper_functions import module_name_from_path
    #
    # base = '__main__'
    # fp = os.path.dirname(sys.modules[base].__file__)
    #
    # m, p = module_name_from_path(fp, verbose=True)
    # print('sys.modules[base]', m)
    # print('path', p)



