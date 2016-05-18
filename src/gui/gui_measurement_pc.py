# this is the gui for the measurment pc
# this gui only loads dummy scripts and instruments

import sys

from src.core import qt_b26_gui
from PyQt4 import QtGui
import ctypes

myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = QtGui.QApplication(sys.argv)
fname = 'c:\\b26_tmp\\gui_settings.b26'
ex = qt_b26_gui.ControlMainWindow(fname)

app.setWindowIcon(QtGui.QIcon('magnet_and_nv.ico'))

ex.show()
ex.raise_()
sys.exit(app.exec_())
