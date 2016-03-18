from PyQt4 import QtCore, QtGui
from src.core import Parameter


class B26QTreeWidget(QtGui.QTreeWidget):
    def __init__(self, parent, parameter, target = None, visible = True):
        '''
        parent (QTreeWidget) : Item's QTreeWidget parent.
        name   (str)         : Item's name. just an example.
        '''

        ## Init super class ( QtGui.QTreeWidgetItem )
        super( B26QTreeWidget, self ).__init__( parent )

        assert isinstance(parameter, Parameter)
        self.parameter = parameter
        # assert that parent is a layout widget


        self.visible = {}
        self.target = {}

        ## Column 0 - Text:
        self.setText(0, unicode(parameter.name))

        if isinstance(parameter.valid_values, list):
            self.combobox = QtGui.QComboBox()
            for item in parameter.valid_values:
                self.combobox.addItem(unicode(item))
            self.combobox.setCurrentIndex(self.combobox.findText(unicode(parameter.value)))
            self.treeWidget().setItemWidget( self, 1, self.combobox )
            self.combobox.currentIndexChanged.connect(lambda: self.parent().emitDataChanged())

        elif parameter.valid_values is bool:
            self.check = QtGui.QCheckBox()
            self.check.setChecked(parameter.value)
            self.treeWidget().setItemWidget( self, 1, self.check )
            self.check.stateChanged.connect(lambda: self.parent().emitDataChanged())

        elif isinstance(parameter.value, Parameter):
            QTreeParameter(self, parameter, target=target, visible=visible)

        elif isinstance(parameter.value, list):
            for item in parameter.value:
                QTreeParameter(self, item, target=target, visible=visible)
        else:
            self.setText(1, unicode(parameter.value))
            self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable)
        self.setToolTip(1, unicode(parameter.info))

class B26QTreeItem(QtGui.QTreeWidgetItem):
    '''
    Custom QTreeWidgetItem with Widgets
    '''

    def __init__(self, parent, parameter, target = None, visible = True):
        '''
        parent (QTreeWidget) : Item's QTreeWidget parent.
        name   (str)         : Item's name. just an example.
        '''

        ## Init super class ( QtGui.QTreeWidgetItem )
        super( B26QTreeItem, self ).__init__( parent )

        assert isinstance(parameter, Parameter)
        # assert isinstance(target, (Script, Instrument))

        self.visible = visible
        self.target = target
        self.parameter = parameter

        ## Column 0 - Text:
        self.setText(0, unicode(parameter.name))

        if isinstance(parameter.valid_values, list):
            self.combobox = QtGui.QComboBox()
            for item in parameter.valid_values:
                self.combobox.addItem(unicode(item))
            self.combobox.setCurrentIndex(self.combobox.findText(unicode(parameter.value)))
            self.treeWidget().setItemWidget( self, 1, self.combobox )
            self.combobox.currentIndexChanged.connect(lambda: self.parent().emitDataChanged())

        elif parameter.valid_values is bool:
            self.check = QtGui.QCheckBox()
            self.check.setChecked(parameter.value)
            self.treeWidget().setItemWidget( self, 1, self.check )
            self.check.stateChanged.connect(lambda: self.parent().emitDataChanged())

        elif isinstance(parameter.value, Parameter):
            B26QTreeItem(self, parameter, target=target, visible=visible)

        elif isinstance(parameter.value, list):
            for item in parameter.value:
                B26QTreeItem(self, item, target=target, visible=visible)
        else:
            self.setText(1, unicode(parameter.value))
            self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable)
        self.setToolTip(1, unicode(parameter.info))

    # @property
    # def parameter(self):
    #     return self._parameter
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