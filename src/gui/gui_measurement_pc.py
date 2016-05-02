# this is the gui for the measurment pc
# this gui only loads dummy scripts and instruments

import sys

from src.core import qt_b26_gui

from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)

ex = qt_b26_gui.ControlMainWindow()


ex.show()
ex.raise_()
sys.exit(app.exec_())
