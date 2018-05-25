# This file is part of pylabcontrol, software for laboratory equipment control for scientific experiments.
# Copyright (C) <2016>  Arthur Safira, Jan Gieseler, Aaron Kabcenell
#
# pylabcontrol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pylabcontrol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pylabcontrol.  If not, see <http://www.gnu.org/licenses/>.

import sys
from PyQt5 import QtWidgets
from pylabcontrol.gui.windows_and_widgets.main_window import MainWindow


def launch_gui(filename=None):
    app = QtWidgets.QApplication(sys.argv)

    try:
        ex = MainWindow(filename)
        ex.show()
        ex.raise_()
        sys.exit(app.exec_())

    except ValueError as e:
        if not e.message in['No config file was provided. abort loading gui...', '']:
            raise e


if __name__ == '__main__':
    launch_gui()
