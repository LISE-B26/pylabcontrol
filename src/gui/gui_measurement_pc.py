# this is the gui for the measurment pc
# this gui only loads dummy scripts and instruments

import sys

from src.core import qt_b26_gui
from PyQt4 import QtGui
import ctypes

#work around to change taskbar icon
myappid = 'lukinlab.b26.pythonlab' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = QtGui.QApplication(sys.argv)
fname = 'c:\\b26_tmp\\pythonlab_config.b26'
fname = "C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\pythonlab_config.b26"

ex = qt_b26_gui.ControlMainWindow(fname)

app.setWindowIcon(QtGui.QIcon('magnet_and_nv.ico'))

ex.show()
ex.raise_()
sys.exit(app.exec_())
 
