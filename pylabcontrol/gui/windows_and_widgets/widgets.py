
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

#Qvariant only need for gui


# try:
#     import sip
#     sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
# except ValueError:
#     pass

from PyQt5 import QtCore, QtWidgets
from pylabcontrol.core import Parameter, Instrument, Script
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure


# ======== B26QTreeItem ==========
class B26QTreeItem(QtWidgets.QTreeWidgetItem):
    """
    Custom QTreeWidgetItem with Widgets
    """

    def __init__(self, parent, name, value, valid_values, info, visible=None):
        """
        Args:
            name:
            value:
            valid_values:
            info:
            visible (optional):

        Returns:

        """

        super(B26QTreeItem, self ).__init__(parent)


        self.ui_type = None
        self.name = name
        self.valid_values = valid_values
        self._value = value
        self.info = info
        self._visible = visible

        self.setData(0, 0, self.name)

        if isinstance(self.valid_values, list):
            self.ui_type = 'combo_box'
            self.combo_box = QtWidgets.QComboBox()
            for item in self.valid_values:
                self.combo_box.addItem(str(item))
            self.combo_box.setCurrentIndex(self.combo_box.findText(str(self.value)))
            self.treeWidget().setItemWidget(self, 1, self.combo_box)
            self.combo_box.currentIndexChanged.connect(lambda: self.setData(1, 2, self.combo_box))
            self.combo_box.setFocusPolicy(QtCore.Qt.StrongFocus)
            self._visible = False

        elif self.valid_values is bool:
            self.ui_type = 'checkbox'
            self.checkbox = QtWidgets.QCheckBox()
            self.checkbox.setChecked(self.value)
            self.treeWidget().setItemWidget( self, 1, self.checkbox )
            self.checkbox.stateChanged.connect(lambda: self.setData(1, 2, self.checkbox))
            self._visible = False

        elif isinstance(self.value, Parameter):
            for key, value in self.value.items():
                B26QTreeItem(self, key, value, self.value.valid_values[key], self.value.info[key])

        elif isinstance(self.value, dict):
            for key, value in self.value.items():
                if self.valid_values == dict:
                    B26QTreeItem(self, key, value, type(value), '')
                else:
                    B26QTreeItem(self, key, value, self.valid_values[key], self.info[key])

        elif isinstance(self.value, Instrument):
            index_top_level_item = self.treeWidget().indexOfTopLevelItem(self)
            top_level_item = self.treeWidget().topLevelItem(index_top_level_item)
            if top_level_item == self:
                # instrument is on top level, thus we are in the instrument tab
                for key, value in self.value.settings.items():
                    B26QTreeItem(self, key, value, self.value.settings.valid_values[key], self.value.settings.info[key])
            else:
                self.valid_values = [self.value.name]
                self.value = self.value.name
                self.combo_box = QtWidgets.QComboBox()
                for item in self.valid_values:
                    self.combo_box.addItem(item)
                self.combo_box.setCurrentIndex(self.combo_box.findText(str(self.value)))
                self.treeWidget().setItemWidget(self, 1, self.combo_box)
                self.combo_box.currentIndexChanged.connect(lambda: self.setData(1, 2, self.combo_box))
                self.combo_box.setFocusPolicy(QtCore.Qt.StrongFocus)

        elif isinstance(self.value, Script):
            for key, value in self.value.settings.items():
                B26QTreeItem(self, key, value, self.value.settings.valid_values[key], self.value.settings.info[key])

            for key, value in self.value.instruments.items():
                B26QTreeItem(self, key, self.value.instruments[key],  type(self.value.instruments[key]), '')

            for key, value in self.value.scripts.items():
                B26QTreeItem(self, key, self.value.scripts[key],  type(self.value.scripts[key]), '')

            self.info = self.value.__doc__

        else:
            self.setData(1, 0, self.value)
            self._visible = False

        self.setToolTip(1, str(self.info if isinstance(self.info, str) else ''))

        if self._visible is not None:
            self.check_show = QtWidgets.QCheckBox()
            self.check_show.setChecked(self.visible)
            self.treeWidget().setItemWidget(self, 2, self.check_show)

        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

    @property
    def value(self):
        """
        item value
        """
        return self._value

    @value.setter
    def value(self, value):
        if Parameter.is_valid(value, self.valid_values):
            self._value = value
            # check if there is a special case for setting such as a checkbox or combobox
            if self.ui_type == 'checkbox':
                self.checkbox.setChecked(value)
            elif self.ui_type == 'combo_box':
                self.combo_box.setCurrentIndex(self.combo_box.findText(str(self.value)))
            else:  # for standard values
                self.setData(1, 0, value)
        else:
            if value is not None:
                raise TypeError("wrong type {:s}, expected {:s}".format(str(type(value)), str(self.valid_values)))

    @property
    def visible(self):
        """

        Returns: boolean (True: item is visible) (False: item is hidden)

        """
        if self._visible is not None:
            return self.check_show.isChecked()

        elif isinstance(self._value, (Parameter, dict)):
            # check if any of the children is visible
            for i in range(self.childCount()):
                if self.child(i).visible:
                    return True
            # if none of the children is visible hide this parameter
            return False
        else:
            return True

    @visible.setter
    def visible(self, value):
        if self._visible is not None:
            self._visible = value
            self.check_show.setChecked(self._visible)

    def setData(self, column, role, value):
        """
        if value is valid sets the data to value
        Args:
            column: column of item
            role: role of item (see Qt doc)
            value: value to be set
        """
        assert isinstance(column, int)
        assert isinstance(role, int)

        # make sure that the right row is selected, this is not always the case for checkboxes and
        # combo boxes because they are items on top of the tree structure
        if isinstance(value, (QtWidgets.QComboBox, QtWidgets.QCheckBox)):
            self.treeWidget().setCurrentItem(self)

        # if row 2 (editrole, value has been entered)
        if role == 2 and column == 1:

            if isinstance(value, str):
                value = self.cast_type(value) # cast into same type as valid values

            if isinstance(value, QtCore.QVariant):
                value = self.cast_type(value.toString())  # cast into same type as valid values

            if isinstance(value, QtWidgets.QComboBox):
                value = self.cast_type(value.currentText())

            if isinstance(value, QtWidgets.QCheckBox):
                value = bool(int(value.checkState()))  # checkState() gives 2 (True) and 0 (False)

            # save value in internal variable
            self.value = value

        elif column == 0:
            # labels should not be changed so we set it back
            value = self.name

        if value is None:
            value = self.value

        # 180327(asafira) --- why do we need to do the following lines? Why not just always call super or always
        # emitDataChanged()?
        if not isinstance(value, bool):
            super(B26QTreeItem, self).setData(column, role, value)

        else:
            self.emitDataChanged()

    def cast_type(self, var, cast_type=None):
        """
        cast the value into the type typ
        if type is not provided it is set to self.valid_values
        Args:
            var: variable to be cast
            type: target type

        Returns: the variable var csat into type typ

        """

        if cast_type is None:
            cast_type = self.valid_values

        try:
            if cast_type == int:
                return int(var)
            elif cast_type == float:
                return float(var)
            elif cast_type == str:
                return str(var)
            elif isinstance(cast_type, list):
                # cast var to be of the same type as those in the list
                return type(cast_type[0])(var)
            else:
                return None
        except ValueError:
            return None

        return var

    def get_instrument(self):
        """
        Returns: the instrument and the path to the instrument to which this item belongs
        """

        if isinstance(self.value, Instrument):
            instrument = self.value
            path_to_instrument = []
        else:
            instrument = None
            parent = self.parent()
            path_to_instrument = [self.name]
            while parent is not None:
                if isinstance(parent.value, Instrument):
                    instrument = parent.value
                    parent = None
                else:
                    path_to_instrument.append(parent.name)
                    parent = parent.parent()

        return instrument, path_to_instrument

    def get_script(self):
        """

        Returns: the script and the path to the script to which this item belongs

        """

        if isinstance(self.value, Script):
            script = self.value
            path_to_script = []
            script_item = self

        else:
            script = None
            parent = self.parent()
            path_to_script = [self.name]
            while parent is not None:
                if isinstance(parent.value, Script):
                    script = parent.value
                    script_item = parent
                    parent = None
                else:
                    path_to_script.append(parent.name)
                    parent = parent.parent()

        return script, path_to_script, script_item

    def get_subscript(self, sub_script_name):
        """
        finds the item that contains the sub_script with name sub_script_name
        Args:
            sub_script_name: name of subscript
        Returns: B26QTreeItem in QTreeWidget which is a script

        """

        # get tree of item
        tree = self.treeWidget()

        items = tree.findItems(sub_script_name, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)

        if len(items) >= 1:
            # identify correct script by checking that it is a sub_element of the current script
            subscript_item = [sub_item for sub_item in items if isinstance(sub_item.value, Script)
                               and sub_item.parent() is self]

            subscript_item = subscript_item[0]
        else:
            raise ValueError('several elements with name ' + sub_script_name)


        return subscript_item

    def is_point(self):
        """
        figures out if item is a point, that is if it has two subelements of type float
        Args:
            self:

        Returns: if item is a point (True) or not (False)

        """

        if self.childCount() == 2:
                if self.child(0).valid_values == float and self.child(1).valid_values == float:
                    return True
        else:
            return False

    def to_dict(self):
        """

        Returns: the tree item as a dictionary

        """
        if self.childCount() > 0:
            value = {}
            for index in range(self.childCount()):
                value.update(self.child(index).to_dict())
        else:
            value = self.value

        return {self.name: value}

class MatplotlibWidget(Canvas):
    """
    MatplotlibWidget inherits PyQt5.QtWidgets.QWidget
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

        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

    def sizeHint(self):
        """
        gives qt a starting point for widget size during window resizing
        """
        w, h = self.get_width_height()
        return QtCore.QSize(w, h)

    def minimumSizeHint(self):
        """
        minimum widget size during window resizing
        Returns: QSize object that specifies the size of widget
        """
        return QtCore.QSize(10, 10)



