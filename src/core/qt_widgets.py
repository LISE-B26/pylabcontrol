
import sip
sip.setapi('QVariant', 2)# set to version to so that the gui returns QString objects and not generic QVariants
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

        assert isinstance(parameters, (dict, Parameter))
        self.parameters = parameters

        for key, value in parameters.iteritems():
            if isinstance(parameters, Parameter):
                B26QTreeItem(self, key, value, parameters.valid_values[key], parameters.info[key])
            else:
                B26QTreeItem(self, key, value, type(value), '')


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
        super(B26QTreeItem, self ).__init__( parent )

        self.name = name
        self.valid_values = valid_values
        self.value = value
        self.info = info
        self.target = target
        self.visible = visible

        self.setData(0, 0, unicode(self.name))
        # self.setText(0, unicode(self.name))


        if isinstance(self.valid_values, list):
            self.combobox = QtGui.QComboBox()
            for item in self.valid_values:
                self.combobox.addItem(unicode(item))
            self.combobox.setCurrentIndex(self.combobox.findText(unicode(self.value)))
            self.treeWidget().setItemWidget( self, 1, self.combobox )
            # if self.parent() is not None:
            #     self.combobox.currentIndexChanged.connect(lambda: self.parent().emitDataChanged())
            # else:
            #     self.combobox.currentIndexChanged.connect(lambda: self.emitDataChanged())


            self.combobox.currentIndexChanged.connect(lambda: self.setData(1, 2, self.combobox))
            # self.combobox.currentIndexChanged.connect(lambda: self.emitDataChanged(self.combobox))

        elif self.valid_values is bool:
            self.check = QtGui.QCheckBox()
            self.check.setChecked(self.value)
            self.treeWidget().setItemWidget( self, 1, self.check )
            self.check.stateChanged.connect(lambda: self.setData(1, 2, self.check))

            # if self.parent() is not None:
            #     self.check.stateChanged.connect(lambda: self.parent().emitDataChanged())
            # else:
            #     self.check.stateChanged.connect(lambda: self.emitDataChanged())
            # self.check.stateChanged.connect(lambda: self.emitDataChanged(self.check))

        elif isinstance(self.value, Parameter):
            for key, value in self.value.iteritems():
                B26QTreeItem(self, key, value, self.valid_values[key], self.info[key], target=self.target, visible=self.visible)

        elif isinstance(self.value, dict):
            for key, value in self.value.iteritems():
                B26QTreeItem(self, key, value, type(value), '', target=self.target, visible=self.visible)

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

    def setData(self, column, role, value):
        assert isinstance(column, int)
        assert isinstance(role, int)
        # assert isinstance(value, QtCore.QString)

        def cast_type(var, typ):
            """
            Args:
                var:
                typ:

            Returns:

            """
            try:
                if typ == int:
                    var = int(var)
                elif typ == float:
                    var = float(var)
                elif typ  == str:
                    var = str(var)
                else:
                    var = None
            except ValueError:
                var = None
            return var
        # if role = 2 (editrole, value has been entered)
        if role == 2 and column == 1:
            if isinstance(value, QtCore.QString):
                if not isinstance(self.valid_values, list):
                    value = cast_type(value, self.valid_values) # cast into same type as valid values
            elif isinstance(value, QtGui.QComboBox):
                value =  value.currentText()

                print('clombo', value)
            elif isinstance(value, QtGui.QCheckBox):
                value =  value.checkState()
                print('check', value)

        elif column == 0:
            # labels should not be changed so we set it back
            value = self.name



        super(B26QTreeItem, self).setData(column, role, value )



