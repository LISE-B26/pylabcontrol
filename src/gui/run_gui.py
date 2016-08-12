"""
    This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
    Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell

    PyLabControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyLabControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.
"""
# this is the gui for the measurment pc

import ctypes
import sys

from PyQt4 import QtGui

from PyLabControl.src.gui import qt_b26_gui

#work around to change taskbar icon
#myappid = 'lukinlab.b26.pythonlab' # arbitrary string
#ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
fname = 'C:\Users\Experiment\PycharmProjects\user_data\pythonlab_config.b26'
def run_gui(fname = ''):
    app = QtGui.QApplication(sys.argv)
    # fname = 'c:\\b26_tmp\\pythonlab_config_dummy.b26'
    # fname = 'c:\\b26_tmp\\pythonlab_config3a.b26'


    # fname = 'c:\\b26_tmp\\pythonlab_config_safsafaf1.b26'

    # fname = "C:\\Users\\Experiment\\PycharmProjects\\PythonLab\\b26_files\\pythonlab_config.b26"
    try:
        print("PyLabControl  Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell \n\n \
PyLabControl is free software: you can redistribute it and/or modify \n \
it under the terms of the GNU General Public License as published by \n \
the Free Software Foundation, either version 3 of the License, or \n \
(at your option) any later version. \n\n \
PyLabControl is distributed in the hope that it will be useful, \n \
but WITHOUT ANY WARRANTY; without even the implied warranty of \n \
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the \n \
GNU General Public License for more details. \n\n \
You should have received a copy of the GNU General Public License \n \
along with PyLabControl.  If not, see <http://www.gnu.org/licenses/>.")

        ex = qt_b26_gui.ControlMainWindow(fname)

        app.setWindowIcon(QtGui.QIcon('magnet_and_nv.ico'))

        ex.show()
        ex.raise_()
        sys.exit(app.exec_())

    except ValueError, e:

        if not e.message in['No config file was provided. abort loading gui...', '']:
            raise e

if __name__ == '__main__':
    run_gui()
