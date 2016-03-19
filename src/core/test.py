from unittest import TestCase
from PyQt4 import QtCore, QtGui
import sys
from src.core.qt_widgets import B26QTreeItem,B26QTreeWidget
from src.core import Parameter

class UI(QtGui.QMainWindow):

    def __init__(self, parent=None ):

        ## Init:
        super(UI, self).__init__( parent )

        # ----------------
        # Create Simple UI with QTreeWidget
        # ----------------
        self.centralwidget = QtGui.QWidget(self)
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)

        self.parameters = Parameter([
            Parameter('test1', 0, int, 'test parameter (int)'),
            Parameter('test2' ,
                      [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                       Parameter('test2_2', 0.0, float, 'test parameter (float)'),
                       Parameter('test2_3', 'a', ['a', 'b', 'c'], 'test parameter (list)'),
                       Parameter('test2_4', False, bool, 'test parameter (bool)')
                       ]),
            Parameter('test3', 'a', ['a', 'b', 'c'], 'test parameter (list)'),
            Parameter('test4', False, bool, 'test parameter (bool)')
        ])

        self.treeWidget = B26QTreeWidget(self.centralwidget, self.parameters)

        # self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
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
        self.treeWidget.itemChanged.connect(lambda: self.update_parameters(self.treeWidget, self.parameters))



    def update_parameters(self, tree, parameters):

        print('sss', tree.currentItem().text(0))

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

if __name__ == '__main__':


    app = QtGui.QApplication(sys.argv)
    ex = UI()
    ex.show()
    ex.raise_()
    sys.exit(app.exec_())
