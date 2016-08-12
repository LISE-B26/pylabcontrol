"""
    This file is part of PyLabControl, software for laboratory equipment control for scientific experiments.
    Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell

    PyLabControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyLabControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
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
        print("PyLabControl  Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell \n"
              "This program comes with ABSOLUTELY NO WARRANTY. \n"
              "This is free software, and you are welcome to redistribute it under certain conditions.")

        ex = qt_b26_gui.ControlMainWindow(fname)

        app.setWindowIcon(QtGui.QIcon('magnet_and_nv.ico'))

        ex.show()
        ex.raise_()
        sys.exit(app.exec_())

    except ValueError, e:
        print(e.message)
        if not e.message == 'No config file was provided. abort loading gui...':
            raise e

if __name__ == '__main__':
    run_gui()
