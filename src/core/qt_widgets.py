from PyQt4 import QtCore, QtGui
from src.core import Parameter


class B26QTreeWidget(QtGui.QTreeWidget):
    def __init__(self, parent, parameters, target = None, visible = True):
        """

        Args:
            parent:
            parameters:
            target:
            visible:

        Returns:

        """

        ## Init super class ( QtGui.QTreeWidgetItem )
        super( B26QTreeWidget, self ).__init__( parent )

        assert isinstance(parameters, Parameter)
        self.parameters = parameters
        # assert that parent is a layout widget

        for key, value in parameters.iteritems():
            print(key, value, parameters.valid_values[key], parameters.info[key])
            B26QTreeItem(self, key, value, parameters.valid_values[key], parameters.info[key])


class B26QTreeItem(QtGui.QTreeWidgetItem):
    '''
    Custom QTreeWidgetItem with Widgets
    '''

    def __init__(self, parent, name, value, valid_values, info, target = None, visible = True):
        """
        Args:
            parent:
            name:
            value:
            valid_values:
            info:
            target (optional):
            visible (optional):

        Returns:

        """

        ## Init super class ( QtGui.QTreeWidgetItem )
        print(parent)
        super( B26QTreeItem, self ).__init__( parent )

        self.name = name
        self.valid_values = valid_values
        self.value = value
        self.info = info
        self.target = target
        self.visible = visible

        self.setText(0, unicode(self.name))

        if isinstance(self.valid_values, list):
            self.combobox = QtGui.QComboBox()
            for item in self.valid_values:
                self.combobox.addItem(unicode(item))
            self.combobox.setCurrentIndex(self.combobox.findText(unicode(self.value)))
            self.treeWidget().setItemWidget( self, 1, self.combobox )
            if self.parent() is not None:
                self.combobox.currentIndexChanged.connect(lambda: self.parent().emitDataChanged())
            else:
                self.combobox.currentIndexChanged.connect(lambda: self.emitDataChanged())
            # self.combobox.currentIndexChanged.connect(lambda: self.emitDataChanged(self.combobox))

        elif self.valid_values is bool:
            self.check = QtGui.QCheckBox()
            self.check.setChecked(self.value)
            self.treeWidget().setItemWidget( self, 1, self.check )
            if self.parent() is not None:
                self.check.stateChanged.connect(lambda: self.parent().emitDataChanged())
            else:
                self.check.stateChanged.connect(lambda: self.emitDataChanged())
            # self.check.stateChanged.connect(lambda: self.emitDataChanged(self.check))

        elif isinstance(self.value, Parameter):
            for key, value in self.value.iteritems():
                print('key: ', key,)
                print('value: ', value)
                print('self.valid_values[key]: ',self.valid_values[key])
                print('self.info: ',  self.info)
                print('self.info[key]: ',  self.info[key])
                print('========')
                B26QTreeItem(self, key, value, self.valid_values[key], self.info[key], target=self.target, visible=self.visible)

        # elif isinstance(self.value, list):
        #     for item in self.value:
        #         B26QTreeItem(self, item, target=target, visible=visible)
        else:
            self.setText(1, unicode(self.value))
            self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable)
        self.setToolTip(1, unicode(self.info  if isinstance(self.info, str) else ''))

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if Parameter.is_valid(value, self.valid_values):
            self._value = value
        else:
            raise TypeError("wrong type {:s}, expected {:s}".format(str(value), str(self.valid_values)))

    @property
    def visible(self):
        return self._visible
    @visible.setter
    def visible(self, value):
        assert isinstance(value, bool)
        self._visible = value

