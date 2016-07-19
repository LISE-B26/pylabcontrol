#Qvariant only need for gui

# try:
#     import sip
#     sip.setapi('QVariant', 2)# set to version to so that the old_gui returns QString objects and not generic QVariants
# except ValueError:
#     pass
    
from PyQt4 import QtCore, QtGui
from src.core import Parameter, Instrument, Script


# ======== B26QTreeItem ==========
class B26QTreeItem(QtGui.QTreeWidgetItem):
    '''
    Custom QTreeWidgetItem with Widgets
    '''

    def __init__(self, parent, name, value, valid_values, info, visible = None):
        """
        Args:
            parent:
            name:
            value:
            valid_values:
            info:
            visible (optional):

        Returns:

        """

        super(B26QTreeItem, self ).__init__( parent )

        self.name = name
        self.valid_values = valid_values
        self.value = value
        self.info = info
        self._visible = visible

        # font = QtGui.QFont()
        # font.setBold(True)
        # font.setPointSize(20)
        # font.setWeight(75)
        # print("SET FONT!!", self.name)
        # self.setFont(0, font)
        self.setTextColor(1, QtGui.QColor(255,0,0))


        # self.setData(0, 0, unicode(self.name))
        self.setData(0, 0, self.name)
        self.setForeground(0, QtGui.QColor(255, 0, 0))

        if isinstance(self.valid_values, list):
            self.combobox = QtGui.QComboBox()
            for item in self.valid_values:
                self.combobox.addItem(unicode(item))
            self.combobox.setCurrentIndex(self.combobox.findText(unicode(self.value)))
            self.treeWidget().setItemWidget( self, 1, self.combobox)
            self.combobox.currentIndexChanged.connect(lambda: self.setData(1, 2, self.combobox))
            self._visible = False

        elif self.valid_values is bool:
            self.check = QtGui.QCheckBox()
            self.check.setChecked(self.value)
            self.treeWidget().setItemWidget( self, 1, self.check )
            self.check.stateChanged.connect(lambda: self.setData(1, 2, self.check))
            self._visible = False

        elif isinstance(self.value, Parameter):
            for key, value in self.value.iteritems():
                B26QTreeItem(self, key, value, self.value.valid_values[key], self.value.info[key])
                # B26QTreeItem(self, key, value, self.value.valid_values[key], self.value.info[key])
        elif isinstance(self.value, dict):
            for key, value in self.value.iteritems():

                if self.valid_values == dict:
                    B26QTreeItem(self, key, value, type(value), '')
                    # B26QTreeItem(self, key, value, type(value), '')
                else:
                    B26QTreeItem(self, key, value, self.valid_values[key], self.info[key])
                    # B26QTreeItem(self, key, value, self.valid_values[key], self.info[key])

        elif isinstance(self.value, Instrument):
            index_top_level_item = self.treeWidget().indexOfTopLevelItem(self)
            top_level_item = self.treeWidget().topLevelItem(index_top_level_item)
            if top_level_item == self:
                # instrument is on top level, thus we are in the instrument tab
                for key, value in self.value.settings.iteritems():
                    B26QTreeItem(self, key, value, self.value.settings.valid_values[key], self.value.settings.info[key])
                    # B26QTreeItem(self, key, value, self.value.settings.valid_values[key], self.value.settings.info[key])
            else:
                self.valid_values = [self.value.name]
                self.value = self.value.name
                self.combobox = QtGui.QComboBox()
                for item in self.valid_values:
                    self.combobox.addItem(unicode(item))
                self.combobox.setCurrentIndex(self.combobox.findText(unicode(self.value)))
                self.treeWidget().setItemWidget(self, 1, self.combobox)
                self.combobox.currentIndexChanged.connect(lambda: self.setData(1, 2, self.combobox))
                # todo: change so that all the instruments of the same type can be selected in the gui
                # B26QTreeItem(self, 'instance', self.value.name, self.value, 'instrument '.format(self.value.name),visible=self.visible)


        elif isinstance(self.value, Script):
            for key, value in self.value.settings.iteritems():
                B26QTreeItem(self, key, value, self.value.settings.valid_values[key], self.value.settings.info[key])
                # B26QTreeItem(self, key, value, self.value.settings.valid_values[key], self.value.settings.info[key])

            for key, value in self.value.instruments.iteritems():
                item = B26QTreeItem(self, key, self.value.instruments[key],  type(self.value.instruments[key]), '')
                # item = B26QTreeItem(self, key, self.value.instruments[key], type(self.value.instruments[key]), '')
                # item.setDisabled(True)

            for key, value in self.value.scripts.iteritems():
                item = B26QTreeItem(self, key, self.value.scripts[key],  type(self.value.scripts[key]), '')
                # item = B26QTreeItem(self, key, self.value.scripts[key], type(self.value.scripts[key]), '')
                # item.setDisabled(True)

            # #todo: set the font to bold
            #
            # print(self.font(0))
            # font = QtGui.QFont()
            # font.setBold(True)
            # font.setPointSize(20)
            # font.setWeight(75)
            # print("SET FONT!!", self.name)
            # self.setFont(0, font)
            #
            # self.setForeground(0, QtGui.QBrush(QtGui.QColor("#003366")))

        else:
            self.setData(1, 0, self.value)
            # self.setFself.setTextColor(0, QtGui.QColor(255, 0, 0))lags(self.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable)
            self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            self._visible = False
        self.setToolTip(1, unicode(self.info if isinstance(self.info, str) else ''))

        # self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        # self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        if self._visible is not None:
            self.check_show = QtGui.QCheckBox()
            self.check_show.setChecked(self.visible)
            self.treeWidget().setItemWidget( self, 2, self.check_show )


    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if Parameter.is_valid(value, self.valid_values):
            self._value = value
        else:
            if value is not None:
                raise TypeError("wrong type {:s}, expected {:s}".format(str(value), str(self.valid_values)))

    @property
    def visible(self):
        if self._visible is not None:
            return self.check_show.isChecked()

        elif isinstance(self.value, (Parameter, dict)):
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


    # @property
    # def show_all(self):
    #     return self._show_all
    # @show_all.setter
    # def show_all(self, value):
    #     if value:
    #         self.chk_visible = QtGui.QCheckBox()
    #         self.chk_visible.setChecked(self.visible)
    #         self.treeWidget().setItemWidget(self, 2, self.chk_visible)
    #     else:
    #         QtGui.QTreeWidget.removeItemWidget(self, 2, self.chk_visible)
    #     self._show_all = value

    def setData(self, column, role, value):
        assert isinstance(column, int)
        assert isinstance(role, int)

        msg = None

        # make sure that the right row is selected, this is not always the case for checkboxes and
        # comboboxes because they are items on top of the tree structure
        if isinstance(value, (QtGui.QComboBox, QtGui.QCheckBox)):
            self.treeWidget().setCurrentItem(self)

        # if role = 2 (editrole, value has been entered)
        if role == 2 and column == 1:

            if isinstance(value, QtCore.QString):

                value = self.cast_type(value) # cast into same type as valid values
            elif isinstance(value, QtCore.QVariant):

                value = self.cast_type(value.toString())  # cast into same type as valid values
            elif isinstance(value, QtGui.QComboBox):
                value = self.cast_type(value.currentText())
            elif isinstance(value, QtGui.QCheckBox):
                value = int(value.checkState()) # this gives 2 (True) and 0 (False)
                value = value == 2


            # save value in internal variable
            self.value = value

        elif column == 0:
            # labels should not be changed so we set it back
            value = self.name
            msg = 'labels can not be changed, label {:s} reset'.format(str(value))

        if value == None:
            value = self.value
            msg = 'value not valid, reset to {:s}'.format(str(value))

        if not isinstance(value, bool):
            super(B26QTreeItem, self).setData(column, role, value)
        else:
            self.emitDataChanged()


    def cast_type(self, var, typ = None):
        """
        cast the value into the type typ
        if typ is not provided it is set to self.valid_values
        Args:
            var: variable to be cast
            typ: target type

        Returns: the variable var csat into type typ

        """

        if typ is None:
            typ = self.valid_values

        try:
            if typ == int:
                var = int(var)
            elif typ == float:
                var = float(var)
            elif typ == str:
                var = str(var)
            elif isinstance(typ, list):
                # get index of element that corresponds to Qstring value
                index = [str(element) for element in typ].index(str(var))
                var = typ[index]
            else:
                var = None
        except ValueError:
            var = None
        return var

    def get_instrument(self):
        """

        Returns: the instrument and the path to the instrument to which this item belongs

        """
        parent = self.parent()

        if isinstance(self.value, Instrument):
            instrument = self.value
            path_to_instrument = []
        else:
            instrument = None
            path_to_instrument = [self.name]
            while parent is not None:
                if isinstance(parent.value, Instrument):
                    instrument = parent.value
                    parent = None
                else:
                    path_to_instrument.append(parent.name)
                    parent = parent.parent()

        # path_to_instrument.reverse()
        return instrument, path_to_instrument

    def get_script(self):
        """

        Returns: the script and the path to the script to which this item belongs

        """
        parent = self.parent()

        if isinstance(self.value, Script):
            script = self.value
            path_to_script = []
            script_item = self
        else:
            script = None
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
            raise ValueError, 'several elements with name ' + sub_script_name


        return subscript_item

    # @staticmethod
    def is_point(self):
        """
        figures out if item is a point, that is if it has two subelements of type float
        Args:
            self:

        Returns: if item is a point (True) or not (False)

        """

        is_point = True
        if self.childCount() == 2:
            for i in range(self.childCount()):
                if self.child(i).valid_values != float:
                    is_point = False
        else:
            is_point = False
        return is_point

    def to_dict(self):
        """

        Returns: the tree item as a dictionary

        """
        if self.childCount()>0:
            value = {}
            for index in range(self.childCount()):
                value.update(self.child(index).to_dict())
        else:
            value = self.value

        return  {self.name: value}



if __name__ == '__main__':

    # from src.core import Instrument
    # from src.core.read_write_functions import load_b26_file
    #
    #
    # # from file
    # file = 'C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\instruments\\MaestroLightControl.b26'
    #
    # input = load_b26_file(file)['instruments']
    #
    # instruments = {}
    # instruments, failed = Instrument.load_and_append(input, instruments)
    # print(instruments)
    #
    #
    # sett = instruments['MaestroLightControl'].settings
    # print('======')
    # print(sett['filter wheel'], type(sett['filter wheel']))
    # print(sett.valid_values['filter wheel'])
    #
    # p = instruments['MaestroLightControl'].settings['filter wheel']
    # print('======')
    # print(p, type(p))
    # print(p.valid_values)
    #


    print('- ---------- NEW -----------------')
    # new
    from src.instruments import MaestroLightControl

    instruments = {'MaestroLightControl':MaestroLightControl()}

    sett = instruments['MaestroLightControl'].settings
    print('======')
    print(sett['filter wheel'], type(sett['filter wheel']))
    print(sett.valid_values['filter wheel'])

    p = instruments['MaestroLightControl'].settings['filter wheel']
    print('======')
    print(p, type(p))
    # print(p.valid_values)



