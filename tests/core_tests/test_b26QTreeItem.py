from unittest import TestCase
from PyQt4 import QtCore, QtGui
import sys


class UI(QtGui.QMainWindow):

        def __init__(self, parent=None ):

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

class TestB26QTreeItem(TestCase):


    app = QtGui.QApplication(sys.argv)
    ex = UI()
    ex.show()
    sys.exit(app.exec_())
