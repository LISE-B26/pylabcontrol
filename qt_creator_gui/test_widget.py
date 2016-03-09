
from PyQt4.uic import loadUiType
# Ui_MainWindow, QMainWindow = loadUiType('zi_control.ui') # with this we don't have to convert the .ui file into a python file!

from qt_creator_gui.zi_control import Ui_MainWindow

from qt_gui_widgets import *
from PySide import QtCore, QtGui

class ControlMainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(ControlMainWindow, self).__init__()
        self.setupUi(self)



        my_instruments = [
            inst.Instrument_Dummy('inst dummy 1'),
            inst.ZI_Sweeper('sweeper')
        ]

        for elem in my_instruments:
            item = QTreeInstrument( self.tree_scripts, elem )



if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    ex = ControlMainWindow()
    ex.show()
    sys.exit(app.exec_())