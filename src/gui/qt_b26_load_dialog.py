"""
Basic gui class designed with QT designer
"""
# import sip
# sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
import os

from PyQt4 import QtGui
from PyQt4.uic import loadUiType

from src.core.read_write_functions import load_b26_file
from src.core import Parameter
import src.scripts
from src.core import Script

# load the basic old_gui either from .ui file or from precompiled .py file
try:
    # import external_modules.matplotlibwidget
    Ui_Dialog, QDialog = loadUiType('load_dialog.ui') # with this we don't have to convert the .ui file into a python file!
except (ImportError, IOError):
    # load precompiled old_gui, to complite run pyqt_uic basic_application_window.ui -o basic_application_window.py
    from src.gui.load_dialog import Ui_Dialog
    from PyQt4.QtGui import QMainWindow
    from PyQt4.QtGui import QDialog
    print('Warning!: on the fly conversion of load_dialog.ui file failed, loaded .py file instead!!')



class LoadDialog(QDialog, Ui_Dialog):
    """
LoadDialog(intruments, scripts, probes)
    - type: either script, instrument or probe
    - loaded_elements: dictionary that contains the loaded elements
ControlMainWindow(settings_file)
    - settings_file is the path to a json file that contains all the settings for the old_gui
Returns:
    """

    def __init__(self, elements_type, elements_old = {}, filename = ''):
        super(LoadDialog, self).__init__()
        self.setupUi(self)

        self.elements_type = elements_type
        self.txt_probe_log_path.setText(filename)

        # create models for tree structures, the models reflect the data
        self.tree_infile_model = QtGui.QStandardItemModel()
        self.tree_infile.setModel(self.tree_infile_model)
        self.tree_infile_model.setHorizontalHeaderLabels([self.elements_type, 'Value'])

        self.tree_loaded_model = QtGui.QStandardItemModel()
        self.tree_loaded.setModel(self.tree_loaded_model)
        self.tree_loaded_model.setHorizontalHeaderLabels([self.elements_type, 'Value'])

        self.tree_script_sequence_model = QtGui.QStandardItemModel()
        self.tree_script_sequence.setModel(self.tree_script_sequence_model)
        self.tree_script_sequence_model.setHorizontalHeaderLabels([self.elements_type, 'Value'])

        # connect the buttons
        self.btn_open.clicked.connect(self.open_file_dialog)
        self.btn_script_sequence.clicked.connect(self.add_script_sequence)

        # create the dictionaries that hold the data
        #   - elements_old: the old elements (scripts, instruments) that have been passed to the dialog
        #   - elements_from_file: the elements from the file that had been opened
        self.elements_old = elements_old
        self.elements_selected = {}
        for element_name, element in self.elements_old.iteritems():
            self.elements_selected.update( {element_name: {'class': element.__class__.__name__ , 'settings':element.settings}})
        if os.path.isfile(filename):
            self.elements_from_file = self.load_elements(filename)
        else:
            self.elements_from_file = {}

        # fill trees with the data
        self.fill_tree(self.tree_loaded, self.elements_selected)
        self.fill_tree(self.tree_infile, self.elements_from_file)

        self.tree_infile.selectionModel().selectionChanged.connect(self.show_info)
        self.tree_loaded.selectionModel().selectionChanged.connect(self.show_info)
        self.tree_script_sequence.selectionModel().selectionChanged.connect(self.show_info)

        self.tree_infile.selectionModel().selectionChanged.connect(self.show_info)

        self.tree_infile_model.itemChanged.connect(self.name_changed)
        self.tree_loaded_model.itemChanged.connect(self.name_changed)

        self.cmb_looping_variable.addItems(['Loop', 'Parameter Sweep'])

    def test(item):
        print(item)

    def name_changed(self, changed_item):
        #COMMENT_ME
        name = str(changed_item.text())

        # if the item has been moved we ignore this because the item only went from one tree to the other without changing names
        if name != '':
            print('new:',name,'old:', self.selected_element_name)
            if name != self.selected_element_name:
                self.elements_from_file[name] = self.elements_from_file[self.selected_element_name]
                del self.elements_from_file[self.selected_element_name]
                self.selected_element_name = name


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
            self.selected_element_name = name



            if name in self.elements_old:
                info = self.elements_old[name].__class__.__doc__

            elif name in self.elements_from_file:
                class_name = self.elements_from_file[name]['class']
                module = __import__('src.{:s}'.format(self.elements_type), fromlist=[class_name])
                print(module, class_name)
                info = getattr(module, class_name).__doc__

            if info is None:
                info = name

            if tree == self.tree_infile:
                self.lbl_info.setText(info)
                self.tree_loaded.clearSelection()

            elif tree == self.tree_loaded:
                self.lbl_info.setText(info)
                self.tree_infile.clearSelection()


    # def accept(self):


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
        if isinstance(input_data, dict) and self.elements_type in input_data:
            print('input_data', input_data)
            print('input_data[elements_type]', input_data[self.elements_type])
            return input_data[self.elements_type]
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

        def add_elemet(item, key, value):
            child_name = QtGui.QStandardItem(key)
            child_name.setDragEnabled(False)
            child_name.setSelectable(False)
            child_name.setEditable(False)

            if isinstance(value, dict):
                for ket_child, value_child in value.iteritems():
                    add_elemet(child_name, ket_child, value_child)
                item.appendRow(child_name)
            else:
                child_value = QtGui.QStandardItem(unicode(value))
                child_value.setDragEnabled(False)
                child_value.setSelectable(False)
                child_value.setEditable(False)

                item.appendRow([child_name, child_value])

        for index, (instrument, instrument_settings) in enumerate(input_dict.iteritems()):
            item = QtGui.QStandardItem(instrument)

            for key, value in instrument_settings['settings'].iteritems():
                add_elemet(item, key, value)

            tree.model().appendRow(item)
            if tree == self.tree_loaded:
                item.setEditable(False)
            tree.setFirstColumnSpanned(index, self.tree_infile.rootIndex(), True)

    def getValues(self):
        """
        Returns: the selected instruments
        """
        elements_selected = {}
        for index in range(self.tree_loaded_model.rowCount()):
            element_name = str(self.tree_loaded_model.item(index).text())
            if element_name in self.elements_old:
                elements_selected.update({element_name: self.elements_old[element_name]})
            elif element_name in self.elements_from_file:
                elements_selected.update({element_name: self.elements_from_file[element_name]})

        return elements_selected

    def add_script_sequence(self):
        #COMMENT_ME

        def empty_tree(tree_model):
            # COMMENT_ME
            def add_children_to_list(item, somelist):
                if item.hasChildren():
                    for rownum in range(0, item.rowCount()):
                        somelist.append(str(item.child(rownum, 0).text()))

            output_list = []
            root = tree_model.invisibleRootItem()
            add_children_to_list(root, output_list)
            tree_model.clear()
            return output_list

        name = str(self.txt_script_sequence_name.text())
        new_script_list = empty_tree(self.tree_script_sequence_model)
        new_script_dict = {}
        for script in new_script_list:
            if script in self.elements_old:
                new_script_dict.update({script: self.elements_old[script]})
            elif script in self.elements_from_file:
                new_script_dict.update({script: self.elements_from_file[script]})
        # factory_scripts = dict()
        # for script in new_script_dict.keys():
        #     if isinstance(new_script_dict[script], dict):
        #         factory_scripts.update({script: eval('src.scripts.' + new_script_dict[script]['class'])})
        #     else: #if an object (already loaded) rather than a dict
        #         factory_scripts.update({script: new_script_dict[script].__class__})
        new_script_parameter_dict = {}
        for index, script in enumerate(new_script_list):
            new_script_parameter_dict.update({script: index})

        # class_name = Script.set_up_dynamic_script(factory_scripts, new_script_parameter_list, self.cmb_looping_variable.currentText() == 'Parameter Sweep')
        new_script_dict = {name: {'class': 'ScriptIterator', 'scripts': new_script_dict,
                                  'settings': {'script_order': new_script_parameter_dict,
                                               'iterator_type': str(self.cmb_looping_variable.currentText())}}}
        self.selected_element_name = name
        print('NSDxxxx', new_script_dict)
        self.fill_tree(self.tree_loaded, new_script_dict)
        self.elements_from_file.update(new_script_dict)



if __name__ == '__main__':
    import sys
    from src.core.loading import instantiate_instruments
    instuments = instantiate_instruments({'inst_dummy': 'DummyInstrument'})
    print(instuments)
    app = QtGui.QApplication(sys.argv)
    # ex = LoadDialog(elements_type = 'instruments', elements_old=instuments, filename="Z:\Lab\Cantilever\Measurements\\__tmp\\test.b26")
    # ex = LoadDialog(elements_type='scripts', elements_old=instuments)
    ex = LoadDialog(elements_type='scripts')

    ex.show()
    ex.raise_()

    print('asda')
    if ex.exec_():
        values = ex.getValues()
        print(values)

    sys.exit(app.exec_())


