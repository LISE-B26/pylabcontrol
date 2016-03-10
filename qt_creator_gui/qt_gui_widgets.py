
from PyQt4 import QtCore, QtGui

from hardware_modules.instruments import Parameter

from hardware_modules.instruments import Instrument_Dummy, Maestro_Controller


class QTreeParameter(QtGui.QTreeWidgetItem, Parameter):
    '''
    Custom QTreeWidgetItem with Widgets
    '''

    def __init__(self, parent, name, value = None, valid_values = None, info = None, visible = True, target = None):
        '''
        parent (QTreeWidget) : Item's QTreeWidget parent.
        name   (str)         : Item's name. just an example.
        '''
        if valid_values == None:
            valid_values = type(value)


        self._data = {
            'name' : name,
            'value': value,
            'valid_values': valid_values,
            'info':info,
            'visible' : visible,
            'target' : target
            }
        ## Init super class ( QtGui.QTreeWidgetItem )
        super( QTreeParameter, self ).__init__( parent )

        ## Column 0 - Text:
        self.setText( 0, unicode(name) )

        if isinstance(self._data['valid_values'], list):
            self.combobox = QtGui.QComboBox()
            for item in self._data['valid_values']:
                self.combobox.addItem(unicode(item))
            # self.combobox.setItemText(value)
            self.combobox.setCurrentIndex(self.combobox.findText(unicode(value)))
            self.treeWidget().setItemWidget( self, 1, self.combobox )
        elif self._data['valid_values'] is bool:
            self.check = QtGui.QCheckBox()
            self.check.setChecked(value)
            self.treeWidget().setItemWidget( self, 1, self.check )
        else:
            self.setText(1, unicode(value))
            self.setFlags(self.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable)
        self.setToolTip(1, unicode(info) )

class QTreeInstrument(QtGui.QTreeWidgetItem):

    def __init__(self, parent, instrument):
        self.instrument = instrument

        print(type(parent))
        super( QTreeInstrument, self ).__init__( parent )
        self.setText(0, unicode(instrument.name))

        for parameter in self.instrument.parameters:
            print(parameter.dict)
            parameter_dict = {
                'name' : parameter.name,
                'value' : parameter.value,
                'info' : parameter.info,
                'valid_values' : parameter.valid_values,
                'target' : self.instrument.name,
                'visible' : True
                }

            print(parameter_dict)
            QTreeParameter( self, **parameter_dict )


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


        my_instruments = [
            Instrument_Dummy('inst dummy 1'),
            Maestro_Controller('maestro 6 channels')
        ]

        for elem in my_instruments:
            item = QTreeInstrument( self.treeWidget, elem )

        # for d in SWEEP_SETTINGS:
        #     print(d)
        #     item = ScriptParameter( self.treeWidget, **d )

        ## Set Columns Width to match content:
        for column in range( self.treeWidget.columnCount() ):
            self.treeWidget.resizeColumnToContents( column )



if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    ex = UI()
    ex.show()
    sys.exit(app.exec_())