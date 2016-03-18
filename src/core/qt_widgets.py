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
        self.parameter = parameters
        # assert that parent is a layout widget


        self.visible = {}
        self.target = {}

        ## Column 0 - Text:
        self.setText(0, unicode(parameters.name))

        if isinstance(parameters.valid_values, list):
            self.combobox = QtGui.QComboBox()
            for item in parameters.valid_values:
                self.combobox.addItem(unicode(item))
            self.combobox.setCurrentIndex(self.combobox.findText(unicode(parameters.value)))
            self.treeWidget().setItemWidget( self, 1, self.combobox )
            self.combobox.currentIndexChanged.connect(lambda: self.parent().emitDataChanged())

        elif parameters.valid_values is bool:
            self.check = QtGui.QCheckBox()
            self.check.setChecked(parameters.value)
            self.treeWidget().setItemWidget( self, 1, self.check )
            self.check.stateChanged.connect(lambda: self.parent().emitDataChanged())

        elif isinstance(parameters.value, Parameter):
            QTreeParameter(self, parameters, target=target, visible=visible)

        elif isinstance(parameters.value, list):
            for item in parameters.value:
                QTreeParameter(self, item, target=target, visible=visible)
        else:
            self.setText(1, unicode(parameters.value))
            self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable)
        self.setToolTip(1, unicode(parameters.info))

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
            self.combobox.currentIndexChanged.connect(lambda: self.parent().emitDataChanged())

        elif self.valid_values is bool:
            self.check = QtGui.QCheckBox()
            self.check.setChecked(self.value)
            self.treeWidget().setItemWidget( self, 1, self.check )
            self.check.stateChanged.connect(lambda: self.parent().emitDataChanged())

        elif isinstance(self.value, Parameter):
            B26QTreeItem(self, self, target=self.target, visible=self.visible)

        # elif isinstance(self.value, list):
        #     for item in self.value:
        #         B26QTreeItem(self, item, target=target, visible=visible)
        else:
            self.setText(1, unicode(self.value))
            self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable)
        self.setToolTip(1, unicode(self.info))

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



if __name__ == '__main__':

    import sys


    class UI(QtGui.QMainWindow):

        def __init__( self, parent=None ):

            ## Init:
            super(UI, self).__init__( parent )

            # ----------------
            # Create Simple UI with QTreeWidget
            # ----------------
            self.centralwidget = QtGui.QWidget(self)
            self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
            self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
            self.verticalLayout.addWidget(self.treeWidget)
            self.setCentralWidget(self.centralwidget)

            # ----------------
            # Set TreeWidget Headers
            # ----------------
            HEADERS = ( "parameter", "value" )
            self.treeWidget.setColumnCount( len(HEADERS) )
            self.treeWidget.setHeaderLabels( HEADERS )

            # ----------------
            # Add Custom QTreeWidgetItem
            # ----------------


            # my_instruments = [
            #     # Instrument_Dummy('inst dummy 1'),
            #     # Maestro_Controller('maestro 6 channels'),
            #     ZIHF2('Zurich instrument')
            # ]
            #
            # for elem in my_instruments:
            #     item = QTreeInstrument( self.treeWidget, elem )
            #
            # my_scripts = [
            #     Script_Dummy('script dummy 1')
            # ]
            #
            # for elem in my_scripts:
            #     item = QTreeScript( self.treeWidget, elem )
            #
            # ## Set Columns Width to match content:
            # for column in range( self.treeWidget.columnCount() ):
            #     self.treeWidget.resizeColumnToContents( column )

    app = QtGui.QApplication(sys.argv)
    ex = UI()
    ex.show()
    sys.exit(app.exec_())