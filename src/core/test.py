from unittest import TestCase

import sip
sip.setapi('QVariant', 2)
from PyQt4 import QtCore, QtGui
import sys
from src.core.qt_b26_widgets import B26QTreeItem, fill_tree
from src.core import Parameter

class UI(QtGui.QMainWindow):

    def __init__(self, parameters,parent=None ):

        ## Init:
        super(UI, self).__init__( parent )

        # ----------------
        # Create Simple UI with QTreeWidget
        # ----------------
        self.centralwidget = QtGui.QWidget(self)
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)



        self.parameters = parameters
        self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        fill_tree(self.treeWidget, self.parameters)

        # self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        self.verticalLayout.addWidget(self.treeWidget)

        self.setCentralWidget(self.centralwidget)

        self.button = QtGui.QPushButton(self.centralwidget)
        self.button.setText("press")
        self.button.clicked.connect(lambda: self.clicked())
        self.verticalLayout.addWidget(self.button)

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

    def clicked(self):
        print(self.treeWidget.currentItem().name)
        print(self.treeWidget.currentItem().get_instrument())

    # def update_parameters(self, tree, parameters):
    #
    #     new_value
    #     print('sss', tree.currentItem().text(0), tree.currentItem().valid_values)
    #
    #
    def update_parameters(self, treeWidget, parameters):

        if treeWidget == self.treeWidget:

            item = treeWidget.currentItem()

            current_item = item
            instrument, path_to_instrument = item.get_instrument()




            old_value = instrument.parameters
            for level in path_to_instrument:
                old_value = old_value[level]

            path_to_instrument.reverse()
            new_value = item.value
            new_value_dict = new_value
            for level in path_to_instrument:
                new_value_dict = {level: new_value_dict}
            print(new_value_dict)



            instrument.parameters.update(new_value_dict)
            # todo: update .parameters



            if new_value is not old_value:
                msg = "changed parameter {:s} from {:s} to {:s} on {:s}".format(item.name, str(old_value), str(new_value), 'target')
            else:
                msg = "did not change parameter {:s} on {:s}".format(item.name, item.target)

            print(msg)




            # print(treeWidget.currentItem(), treeWidget.currentItem().target)
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


    #======= test with parameter objects ===========
    parameters = Parameter([
        Parameter('test1', 0, int, 'test parameter (int)'),
        Parameter('test2' ,
                  [Parameter('test2_1', 'string', str, 'test parameter (str)'),
                   Parameter('test2_2', 0.0, float, 'test parameter (float)'),
                   Parameter('test2_3', 'a', ['a', 'b', 'c'], 'test parameter (list)'),
                   Parameter('test2_4', False, bool, 'test parameter (bool)')
                   ]),
        Parameter('test3', 'aa', ['aa', 'bb', 'cc'], 'test parameter (list)'),
        Parameter('test4', False, bool, 'test parameter (bool)')
    ])
    #======= test with dict ========================
    parameters = {
        'test1':1,
        'test2':{'test2_1':'ss', 'test3':4},
        'test4':2
    }

    #======= test with instrument objects ===========
    from src.instruments import ZIHF2, MaestroController, MaestroBeamBlock
    # maestro = MaestroController('maestro 6 channels')
    instruments = [
        ZIHF2('ZiHF2')
        # MaestroBeamBlock(maestro,'IR beam block')
    ]
    parameters = {instrument.name: instrument  for instrument in instruments}


    app = QtGui.QApplication(sys.argv)
    ex = UI(parameters)
    ex.show()
    ex.raise_()
    sys.exit(app.exec_())
